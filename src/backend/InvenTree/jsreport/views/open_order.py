"""Open Order report view for the 'jsreport' app."""

from rest_framework.pagination import LimitOffsetPagination

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from purchase_order.models import PurchaseOrderLine

from jsreport.exports import JSReportExportMixin
from jsreport.permissions import JSReportPermission
from jsreport.serializers import OpenOrderSerializer
from jsreport.filters import get_open_order_queryset


class JSReportPagination(LimitOffsetPagination):
    """Default pagination for jsreport list endpoints."""

    default_limit = 25
    max_limit = 500


class OpenOrderReportView(JSReportExportMixin, ListAPI):
    """Open Order report.

    ?report_type=all                      -> all vendors
    ?report_type=vendor&vendorid=<id>     -> vendorwise
    ?report_type=customer&customerid=<id> -> customerwise
    """

    export_name = 'Open_Order'
    export_plugin = 'jsreport-open-order'

    queryset = PurchaseOrderLine.objects.all()
    serializer_class = OpenOrderSerializer
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
        'balqty',
    ]

    def get_queryset(self):
        params = self.request.query_params
        report_type = params.get('report_type', 'all')

        vendorid = params.get('vendorid') if report_type == 'vendor' else None
        customerid = params.get('customerid') if report_type == 'customer' else None

        return get_open_order_queryset(vendorid=vendorid, customerid=customerid)