"""P.O. Status report view for the 'jsreport' app."""

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from purchase_order.models import PurchaseOrderLine

from jsreport.exports import GroupedLayout, JSReportExportMixin, RowBlock
from jsreport.filters import get_po_status_queryset
from jsreport.permissions import JSReportPermission
from jsreport.serializers import POStatusSerializer
from jsreport.views.open_order import JSReportPagination

# Two-level header: (group, label). Group None = spans both header rows.
PO_STATUS_HEADERS = [
    (None, '#'),
    (None, 'Image'),
    (None, 'Style'),
    (None, '# Of Sets'),
    ('Diamond Sent', 'Date'),
    ('Diamond Sent', '# Of Sets'),
    ('Diamond Sent', 'Cts.'),
    ('Diamond Sent', 'Inv.#'),
    ('Color Stone Sent', 'Date'),
    ('Color Stone Sent', '# Of Sets'),
    ('Color Stone Sent', 'Cts.'),
    ('Color Stone Sent', 'Inv.#'),
    ('Received', 'Date'),
    ('Received', '# Of Sets'),
    ('Received', 'Diamond Cts.'),
    ('Received', 'Color Stone Cts.'),
    ('Received', 'Inv.#'),
    ('Balance', '# Of Sets'),
    ('Balance', 'Diamond Cts.'),
    ('Balance', 'Color Stone Cts.'),
]

PO_STATUS_LAYOUT = GroupedLayout(
    merged_groups={'Balance'},  # one balance value per style, like #/Image/Style
    filled_groups={'Diamond Sent', 'Received'},  # yellow blocks
    freeze_cols=4,  # keep #, Image, Style, # Of Sets visible when scrolling
)


def _num(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _total(entries, key):
    return sum(_num(entry.get(key)) for entry in entries)


def _clean(value):
    """Whole numbers show as 10 not 10.0; avoids float noise."""
    value = round(value, 3)
    return int(value) if value == int(value) else value


def po_status_block(item):
    """One style -> one RowBlock.

    A style can have several diamond-sent / color-stone-sent / received
    entries. They are stacked line by line (line n shows entry n of each),
    while #, Image, Style, # Of Sets and Balance are merged over the block.

    Expected keys in the serialized item (adapt here if yours differ):
        image, styleno, qty
        diamond_sent : [{date, sets, cts, inv}, ...]
        color_sent   : [{date, sets, cts, inv}, ...]
        received     : [{date, sets, diamond_cts, color_cts, inv}, ...]
        balance_sets, balance_diamond_cts, balance_color_cts  (optional)
    """
    diamond = item.get('diamond_sent') or []
    color = item.get('color_sent') or []
    received = item.get('received') or []

    sets = item.get('qty')

    # Balance = sent - received (taken from the serializer when it has it)
    balance_sets = item.get('balance_sets')
    if balance_sets is None:
        balance_sets = _clean(_num(sets) - _total(received, 'sets'))

    balance_diamond = item.get('balance_diamond_cts')
    if balance_diamond is None:
        balance_diamond = _clean(_total(diamond, 'cts') - _total(received, 'diamond_cts'))

    balance_color = item.get('balance_color_cts')
    if balance_color is None:
        balance_color = _clean(_total(color, 'cts') - _total(received, 'color_cts'))

    lines = []

    for i in range(max(len(diamond), len(color), len(received), 1)):
        d = diamond[i] if i < len(diamond) else {}
        c = color[i] if i < len(color) else {}
        r = received[i] if i < len(received) else {}

        lines.append([
            None,  # "#", numbered by the export mixin
            item.get('image'),
            item.get('styleno'),
            sets,
            d.get('date'), d.get('sets'), d.get('cts'), d.get('inv'),
            c.get('date'), c.get('sets'), c.get('cts'), c.get('inv'),
            r.get('date'), r.get('sets'), r.get('diamond_cts'), r.get('color_cts'), r.get('inv'),
            balance_sets, balance_diamond, balance_color,
        ])

    return RowBlock(lines)


class POStatusReportView(JSReportExportMixin, ListAPI):
    """P.O. Status report.

    ?poid=<id> or ?pono=<P.O. number>
    """

    export_name = 'PO_Status'
    export_plugin = 'jsreport-po-status'
    export_serial = True

    queryset = PurchaseOrderLine.objects.all()
    serializer_class = POStatusSerializer
    pagination_class = JSReportPagination
    permission_classes = [JSReportPermission]

    filter_backends = SEARCH_ORDER_FILTER
    search_fields = [
        'styleno',
    ]
    ordering_fields = [
        'styleno',
        'qty',
    ]

    def get_queryset(self):
        params = self.request.query_params

        return get_po_status_queryset(
            poid=params.get('poid'),
            pono=params.get('pono'),
        )

    def get_export_table(self, queryset, items, instances):
        rows = [po_status_block(item) for item in items]
        return PO_STATUS_HEADERS, rows, PO_STATUS_LAYOUT