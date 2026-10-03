"""Open Order report view for the 'jsreport' app."""

from rest_framework.pagination import LimitOffsetPagination

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from purchase_order.models import PurchaseOrderLine

from ..permissions import JSReportPermission
from ..serializers import OpenOrderSerializer
from ..utils import get_open_order_queryset


class JSReportPagination(LimitOffsetPagination):
    """Default pagination for jsreport list endpoints."""

    default_limit = 25
    max_limit = 500


class OpenOrderReportView(DataExportViewMixin, ListAPI):
    """Open Order report."""

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
        return get_open_order_queryset()