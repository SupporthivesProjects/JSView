from rest_framework.pagination import LimitOffsetPagination

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI

from . import serializers as po_serializers
from .models import PurchaseOrder, PurchaseOrderLine


class PurchaseOrderPagination(LimitOffsetPagination):
    """Default pagination for purchase order list endpoints."""

    default_limit = 10
    max_limit = 100


class PurchaseOrderList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating PurchaseOrder objects."""

    queryset = PurchaseOrder.objects.select_related(
        'linkid', 'customerid', 'vendorid', 'stampid', 'acexeid', 'termsid',
    ).prefetch_related('lines').all()
    serializer_class = po_serializers.PurchaseOrderSerializer
    pagination_class = PurchaseOrderPagination
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = [
        'potype', 'pocategory', 'customerid', 'vendorid',
        'stampid', 'acexeid', 'termsid', 'active',
    ]
    search_fields = ['pono', 'customer_pono', 'rem', 'note']
    ordering_fields = ['podate', 'npono', 'createdat', 'tqty']
    ordering = ['-podate', '-npono']


class PurchaseOrderDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single PurchaseOrder object."""

    queryset = PurchaseOrder.objects.select_related(
        'linkid', 'customerid', 'vendorid', 'stampid', 'acexeid', 'termsid',
    ).prefetch_related('lines').all()
    serializer_class = po_serializers.PurchaseOrderSerializer


class PurchaseOrderLineList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating PurchaseOrderLine objects."""

    queryset = PurchaseOrderLine.objects.select_related(
        'poid', 'costcardid', 'vendorid',
    ).all()
    serializer_class = po_serializers.PurchaseOrderLineSerializer
    pagination_class = PurchaseOrderPagination
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['poid', 'costcardid', 'vendorid', 'active']
    search_fields = ['styleno', 'vstyleno']
    ordering_fields = ['pk', 'qty']
    ordering = 'pk'


class PurchaseOrderLineDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single PurchaseOrderLine object."""

    queryset = PurchaseOrderLine.objects.select_related(
        'poid', 'costcardid', 'vendorid',
    ).all()
    serializer_class = po_serializers.PurchaseOrderLineSerializer
