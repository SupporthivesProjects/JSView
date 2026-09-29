"""API views for the 'vendor_shipment' app.

Two sections are exposed:

1. Shipment       — CRUD for :class:`VendorShipment` / :class:`VendorShipmentLine`
2. Confirm        — bulk confirmation of received shipment lines plus the
   dropdown/helper endpoints which replicate the legacy PostgreSQL functions.
"""

from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI

from . import serializers as shipment_serializers
from . import utils
from .models import VendorShipment, VendorShipmentLine


class VendorShipmentPagination(LimitOffsetPagination):
    """Default pagination for vendor shipment list endpoints."""

    default_limit = 10
    max_limit = 100


def _query_bool(value, default=True):
    """Parse a boolean-ish query parameter (``None`` -> ``default``)."""
    if value is None:
        return default
    return str(value).strip().lower() in ('1', 'true', 'yes', 'y', 'open')


def _query_int(value):
    """Parse an integer query parameter (``None`` / invalid -> ``None``)."""
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Shipment section — CRUD
# ---------------------------------------------------------------------------

class VendorShipmentList(DataExportViewMixin, ListCreateAPI):
    """List / create vendor shipments.

    POST accepts the header fields plus a nested ``lines[]`` array; the header
    and all of its lines are saved together in a single transaction.
    """

    queryset = VendorShipment.objects.select_related(
        'vendorid', 'courierid',
    ).prefetch_related('lines').all()
    serializer_class = shipment_serializers.VendorShipmentSerializer
    pagination_class = VendorShipmentPagination
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['vendorid', 'active']
    search_fields = ['vsno', 'trackref']
    ordering_fields = ['vsdate', 'id']
    ordering = ['-id']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return shipment_serializers.VendorShipmentCreateSerializer
        return shipment_serializers.VendorShipmentSerializer


class VendorShipmentDetail(RetrieveUpdateDestroyAPI):
    """Detail view of a single vendor shipment (header + nested lines)."""

    queryset = VendorShipment.objects.select_related(
        'vendorid', 'courierid',
    ).prefetch_related('lines').all()
    serializer_class = shipment_serializers.VendorShipmentSerializer


class VendorShipmentLineList(DataExportViewMixin, ListCreateAPI):
    """List / create vendor shipment lines.

    When mounted under ``<pk>/lines/`` the results are scoped to that shipment.
    """

    queryset = VendorShipmentLine.objects.select_related(
        'vendorshipid', 'poid', 'costcardid',
    ).all()
    serializer_class = shipment_serializers.VendorShipmentLineSerializer
    pagination_class = VendorShipmentPagination
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['vendorshipid', 'poid', 'costcardid', 'confrm', 'active']
    search_fields = ['poid__pono', 'costcardid__our_style_no']
    ordering_fields = ['pk', 'pcs']
    ordering = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        shipment_pk = self.kwargs.get('pk')
        if shipment_pk is not None:
            queryset = queryset.filter(vendorshipid_id=shipment_pk)
        return queryset


class VendorShipmentLineDetail(RetrieveUpdateDestroyAPI):
    """Detail view of a single vendor shipment line."""

    queryset = VendorShipmentLine.objects.select_related(
        'vendorshipid', 'poid', 'costcardid',
    ).all()
    serializer_class = shipment_serializers.VendorShipmentLineSerializer


# ---------------------------------------------------------------------------
# Shipment section — dropdown helpers
# ---------------------------------------------------------------------------

class VendorPOListView(APIView):
    """GET /api/vendor-shipment/po-list/?vendorid=<id>&is_open=true.

    Replicates ``fn_po_vendorstatus`` — returns ``[{poid, pono}]``.
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        vendorid = _query_int(request.query_params.get('vendorid'))
        is_open = _query_bool(request.query_params.get('is_open'), default=True)
        return Response(utils.get_vendor_po_list(vendorid, is_open))


class VendorStyleListView(APIView):
    """GET /api/vendor-shipment/style-list/?poid=<id>&is_open=true.

    Replicates ``fn_vendor_style`` — returns ``[{costcardid, styleno}]``.
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        poid = _query_int(request.query_params.get('poid'))

        if not poid:
            return Response(
                {'error': 'poid is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_open = _query_bool(request.query_params.get('is_open'), default=True)
        return Response(utils.get_vendor_style_list(poid, is_open))


# ---------------------------------------------------------------------------
# Confirm shipment section
# ---------------------------------------------------------------------------

class ConfirmPendingInvoiceView(APIView):
    """GET /api/vendor-shipment/confirm/invoices/?vendorid=<id>.

    Replicates ``fn_tbvendorship1_vendorpo`` — returns the shipments which
    still have unconfirmed lines (``confrm IS NULL``).
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        vendorid = _query_int(request.query_params.get('vendorid'))
        return Response(utils.get_confirm_pending_invoices(vendorid))


class ConfirmPendingDataView(APIView):
    """GET /api/vendor-shipment/confirm/data/?vendorid=<id>&vendorshipid=<id>.

    Replicates ``fn_tbvendorship_data`` — returns the detailed shipment lines
    joined with PO / ordered quantity / frozen cost card values.
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        vendorid = _query_int(request.query_params.get('vendorid'))
        vendorshipid = _query_int(request.query_params.get('vendorshipid'))

        if not vendorshipid:
            return Response(
                {'error': 'vendorshipid is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(utils.get_confirm_pending_data(vendorid, vendorshipid))


class ConfirmUpdateView(APIView):
    """POST /api/vendor-shipment/confirm/update/.

    Body: ``[{"tableid": 1, "confrm": true}, ...]``

    Bulk updates the ``confrm`` flag of the referenced shipment lines.
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        entries = request.data

        if isinstance(entries, dict):
            entries = entries.get('lines') or entries.get('items') or [entries]

        if not isinstance(entries, list):
            return Response(
                {'error': 'A list of {tableid, confrm} objects is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = utils.update_confirm_flags(entries)

        return Response({'updated': updated})
