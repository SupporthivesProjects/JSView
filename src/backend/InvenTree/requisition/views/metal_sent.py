"""Metal sent API views."""

from data_exporter.mixins import DataExportViewMixin

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI
from requisition import serializers as requisition_serializers
from requisition.models import MetalSent
from requisition.permissions import RequisitionPermission

from .pagination import RequisitionPagination


def metal_sent_queryset():
    """Base queryset with related objects loaded in a single query."""

    return MetalSent.objects.select_related('purchase_order', 'prepby')


class MetalSentList(DataExportViewMixin, ListCreateAPI):
    """List and create Metal Sent records."""

    queryset = metal_sent_queryset()
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
        """Record the creating user; metal_sent_no is assigned in save()."""

        user = self.request.user

        serializer.save(prepby=user if user.is_authenticated else None)


class MetalSentDetail(RetrieveUpdateDestroyAPI):
    """Retrieve, update, or delete a Metal Sent record."""

    queryset = metal_sent_queryset()
    serializer_class = requisition_serializers.MetalSentSerializer
    permission_classes = [RequisitionPermission]