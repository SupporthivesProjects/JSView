"""Close Order report view for the 'jsreport' app."""

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from purchase_order.models import PurchaseOrderLine

from jsreport.permissions import JSReportPermission
from jsreport.serializers import CloseOrderSerializer
from jsreport.utils import get_close_order_queryset
from jsreport.views.open_order import JSReportPagination


class CloseOrderReportView(DataExportViewMixin, ListAPI):
    """Close Order report."""

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
        return get_close_order_queryset()