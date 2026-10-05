"""Close Order report view for the 'jsreport' app."""

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from purchase_order.models import PurchaseOrderLine

from jsreport.exports import JSReportExportMixin
from jsreport.permissions import JSReportPermission
from jsreport.serializers import CloseOrderSerializer
from jsreport.filters import get_close_order_queryset
from jsreport.views.open_order import JSReportPagination


class CloseOrderReportView(JSReportExportMixin, ListAPI):
    """Close Order report.

    ?report_type=all                      -> all vendors
    ?report_type=vendor&vendorid=<id>     -> vendorwise
    ?report_type=customer&customerid=<id> -> customerwise
    """

    export_name = 'Close_Order'
    export_plugin = 'jsreport-close-order'

    queryset = PurchaseOrderLine.objects.all()
    serializer_class = CloseOrderSerializer
    pagination_class = JSReportPagination
    permission_classes = [JSReportPermission]

    filter_backends = SEARCH_ORDER_FILTER
    search_fields = [
        'poid__pono',
        'poid__customer_pono',
        'styleno',
    ]
    ordering_fields = [
        'poid__podate',
        'poid__pono',
        'qty',
        'shipqty',
    ]

    def get_queryset(self):
        params = self.request.query_params
        report_type = params.get('report_type', 'all')

        vendorid = params.get('vendorid') if report_type == 'vendor' else None
        customerid = params.get('customerid') if report_type == 'customer' else None

        return get_close_order_queryset(vendorid=vendorid, customerid=customerid)