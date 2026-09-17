import django_filters.rest_framework.filters as rest_filters
from django_filters.rest_framework.filterset import FilterSet
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


class PurchaseOrderFilter(FilterSet):
    """Filters for the PurchaseOrder list endpoint.

    Besides the exact-match fields, each table column has its own text filter,
    so that several columns can be searched at once (combined with AND).
    """

    class Meta:
        model = PurchaseOrder
        fields = [
            'potype', 'pocategory', 'customerid', 'vendorid',
            'stampid', 'acexeid', 'termsid', 'prepby', 'active',
        ]

    pono_search = rest_filters.CharFilter(field_name='pono', lookup_expr='icontains')

    # Matches against the ISO date text, e.g. "2026-09" or "2026-09-17"
    podate_search = rest_filters.CharFilter(
        field_name='podate', lookup_expr='icontains',
    )

    customer_search = rest_filters.CharFilter(
        field_name='customerid__name', lookup_expr='icontains',
    )

    pocategory_search = rest_filters.CharFilter(
        field_name='pocategory', lookup_expr='icontains',
    )

    tqty_search = rest_filters.CharFilter(method='filter_tqty_search')

    def filter_tqty_search(self, queryset, name, value):
        """Exact match on total quantity; non-numeric input matches nothing."""
        value = value.strip()

        if not value.isdigit():
            return queryset.none()

        return queryset.filter(tqty=int(value))

    prepby_search = rest_filters.CharFilter(
        field_name='prepby__username', lookup_expr='icontains',
    )


class PurchaseOrderList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating PurchaseOrder objects."""

    queryset = PurchaseOrder.objects.select_related(
        'linkid', 'customerid', 'vendorid', 'stampid', 'acexeid', 'termsid', 'prepby',
    ).prefetch_related('lines').all()
    serializer_class = po_serializers.PurchaseOrderSerializer
    pagination_class = PurchaseOrderPagination
    filter_backends = SEARCH_ORDER_FILTER
    filterset_class = PurchaseOrderFilter
    search_fields = ['pono', 'customer_pono', 'rem', 'note', 'prepby__username']
    ordering_fields = ['podate', 'npono', 'createdat', 'tqty']
    ordering = ['-podate', '-npono']


class PurchaseOrderDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single PurchaseOrder object."""

    queryset = PurchaseOrder.objects.select_related(
        'linkid', 'customerid', 'vendorid', 'stampid', 'acexeid', 'termsid', 'prepby',
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

    def get_queryset(self):
        queryset = super().get_queryset()
        po_pk = self.kwargs.get('pk')
        if po_pk is not None:
            queryset = queryset.filter(poid_id=po_pk)
        return queryset


class PurchaseOrderLineDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single PurchaseOrderLine object."""

    queryset = PurchaseOrderLine.objects.select_related(
        'poid', 'costcardid', 'vendorid',
    ).all()
    serializer_class = po_serializers.PurchaseOrderLineSerializer
