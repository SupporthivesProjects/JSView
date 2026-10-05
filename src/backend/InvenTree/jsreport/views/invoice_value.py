"""Invoice Value P/C report view for the 'jsreport' app."""

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from vendor_shipment.models import VendorShipmentLine

from jsreport.permissions import JSReportPermission
from jsreport.serializers import InvoiceValueSerializer
from jsreport.utils import get_invoice_value_queryset
from jsreport.views.open_order import JSReportPagination


class InvoiceValueReportView(DataExportViewMixin, ListAPI):
    """Invoice Value P/C report.

    ?vendorid=<id>&vsno=<invoice no>
    """

    queryset = VendorShipmentLine.objects.all()
    serializer_class = InvoiceValueSerializer
    pagination_class = JSReportPagination
    permission_classes = [JSReportPermission]

    filter_backends = SEARCH_ORDER_FILTER
    search_fields = [
        'poid__pono',
        'costcardid__vendor_style_no',
    ]
    ordering_fields = [
        'poid__pono',
        'pcs',
    ]

    def get_queryset(self):
        params = self.request.query_params

        return get_invoice_value_queryset(
            vendorid=params.get('vendorid'),
            vsno=params.get('vsno'),
        )