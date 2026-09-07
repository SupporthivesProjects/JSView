from rest_framework import serializers as drf_serializers

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin

from .models import PurchaseOrder, PurchaseOrderLine


class PurchaseOrderLineSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the PurchaseOrderLine model."""

    class Meta:
        model = PurchaseOrderLine
        fields = [
            'pk', 'poid', 'costcardid', 'styleno', 'vstyleno', 'vendorid',
            'qty', 'size', 'spcs', 'stnoauto',
            'active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class PurchaseOrderSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """
    Serializer for the PurchaseOrder model.

    Includes nested line items (read-only) and FK detail serializers.
    """

    lines = PurchaseOrderLineSerializer(many=True, read_only=True)

    # Read-only detail fields for FK relations
    customer_name = drf_serializers.CharField(
        source='customerid.name', read_only=True, default=None,
    )
    vendor_name = drf_serializers.CharField(
        source='vendorid.name', read_only=True, default=None,
    )
    stamp_name = drf_serializers.CharField(
        source='stampid.name', read_only=True, default=None,
    )
    acexe_name = drf_serializers.CharField(
        source='acexeid.name', read_only=True, default=None,
    )
    terms_name = drf_serializers.CharField(
        source='termsid.name', read_only=True, default=None,
    )

    class Meta:
        model = PurchaseOrder
        fields = [
            'pk',
            # Header
            'linkid', 'potype', 'pono', 'npono', 'nyear', 'podate',
            'prepby', 'ddate', 'vcsdate', 'esdstone',
            'customerid', 'customer_pono', 'customer_name',
            'pocategory', 'rem', 'note',
            'stampid', 'stamp_name',
            'acexeid', 'acexe_name',
            'vendorid', 'vendor_name',
            'tqty',
            'termsid', 'terms_name',
            'luser',
            # Cancellation
            'canc_dt', 'canc_rem', 'canc_user',
            # Common
            'active', 'created_at', 'updated_at',
            # Nested
            'lines',
        ]
        read_only_fields = [
            'pono', 'npono', 'nyear',
            'created_at', 'updated_at',
        ]
