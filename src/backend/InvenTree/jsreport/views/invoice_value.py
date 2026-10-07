"""Invoice Value P/C report view for the 'jsreport' app."""

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from vendor_shipment.models import VendorShipmentLine

from jsreport.exports import JSReportExportMixin
from jsreport.permissions import JSReportPermission
from jsreport.serializers import DATE_FMT, InvoiceValueSerializer
from jsreport.filters import get_invoice_value_queryset
from jsreport.views.open_order import JSReportPagination


class InvoiceValueReportView(JSReportExportMixin, ListAPI):
    """Invoice Value P/C report.

    ?vendorid=<id>&vsno=<invoice no>
    """

    export_name = 'Inv_Wise_Value_PC'
    export_plugin = 'jsreport-invoice-value'
    export_serial = True

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

    def get_export_meta(self, queryset):
        line = queryset.first()

        if line is None:
            return []

        shipment = line.vendorshipid
        vendor = shipment.vendorid

        return [
            ('Invoice No.', shipment.vsno),
            ('Vendor', vendor.code if vendor else ''),
            ('Invoice Date', shipment.vsdate.strftime(DATE_FMT) if shipment.vsdate else ''),
        ]