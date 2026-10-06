"""P.O. Status report view for the 'jsreport' app."""

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from purchase_order.models import PurchaseOrderLine

from jsreport.exports import JSReportExportMixin
from jsreport.permissions import JSReportPermission
from jsreport.serializers import DATE_FMT, POStatusSerializer
from jsreport.filters import get_po_status_queryset
from jsreport.views.open_order import JSReportPagination


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

    def get_export_meta(self, queryset):
        line = queryset.first()

        if line is None:
            return []

        order = line.poid
        vendor = order.vendorid

        return [
            ('P.O.#', order.pono),
            ('P.O. Date', order.podate.strftime(DATE_FMT) if order.podate else ''),
            ('Vendor', vendor.name if vendor else ''),
        ]