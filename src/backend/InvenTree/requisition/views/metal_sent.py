"""Metal sent API views."""

from data_exporter.mixins import DataExportViewMixin

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI
from requisition import serializers as requisition_serializers
from requisition.models import MetalSent
from requisition.permissions import RequisitionPermission

from .pagination import RequisitionPagination


class MetalSentList(DataExportViewMixin, ListCreateAPI):
    queryset = MetalSent.objects.all()
    serializer_class = requisition_serializers.MetalSentSerializer
    pagination_class = RequisitionPagination
    permission_classes = [RequisitionPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['purchase_order', 'active', 'triounce']
    search_fields = ['invoice_no', 'purchase_order__pono']
    ordering_fields = [
        'metal_sent_no',
        'metal_sent_date',
        'invoice_no',
        'metal_gms',
        'metal_amount',
    ]
    ordering = '-metal_sent_date'

    def perform_create(self, serializer):
        serializer.save(prepby=self.request.user)


class MetalSentDetail(RetrieveUpdateDestroyAPI):
    queryset = MetalSent.objects.all()
    serializer_class = requisition_serializers.MetalSentSerializer
    permission_classes = [RequisitionPermission]