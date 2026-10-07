"""P.O. Stone Valuation report view for the 'jsreport' app."""

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from purchase_order.models import PurchaseOrderLine

from jsreport.exports import JSReportExportMixin
from jsreport.permissions import JSReportPermission
from jsreport.serializers import POStoneValuationSerializer
from jsreport.filters import get_po_stone_valuation_queryset
from jsreport.views.open_order import JSReportPagination


class POStoneValuationReportView(JSReportExportMixin, ListAPI):
    """P.O. Stone Valuation report. The Excel export has one sheet per vendor.

    ?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD   -> P.O. date range
    ?vendorid=<id>                             -> optional, one vendor only
    """

    export_name = 'PO_Stone_Valuation'
    export_plugin = 'jsreport-po-stone-valuation'

    queryset = PurchaseOrderLine.objects.all()
    serializer_class = POStoneValuationSerializer
    pagination_class = JSReportPagination
    permission_classes = [JSReportPermission]

    filter_backends = SEARCH_ORDER_FILTER
    search_fields = [
        'poid__pono',
        'styleno',
    ]
    ordering_fields = [
        'poid__pono',
        'styleno',
    ]

    def get_queryset(self):
        params = self.request.query_params

        return get_po_stone_valuation_queryset(
            date_from=params.get('date_from'),
            date_to=params.get('date_to'),
            vendorid=params.get('vendorid'),
        )

    def get_export_sheet_title(self, instance):
        vendor = instance.poid.vendorid

        return vendor.code if vendor else None