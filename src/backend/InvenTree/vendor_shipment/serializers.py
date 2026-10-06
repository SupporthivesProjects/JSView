"""Serializers for the 'vendor_shipment' app."""

from django.db import transaction
from rest_framework import serializers as drf_serializers

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin

from .models import VendorShipment, VendorShipmentLine


class VendorShipmentLineSerializer(
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    """Serializer for the VendorShipmentLine model."""

    pono = drf_serializers.CharField(
        source='poid.pono',
        read_only=True,
        default=None,
    )

    styleno = drf_serializers.CharField(
        source='costcardid.our_style_no',
        read_only=True,
        default=None,
    )

    class Meta:
        model = VendorShipmentLine
        fields = [
            'pk',
            'vendorshipid',
            'poid',
            'pono',
            'costcardid',
            'styleno',
            'pcs',
            'metalwt',
            'diawt',
            'stplace',
            'colwt',
            'labour',
            'finding',
            'triounce',
            'confrm',
            'active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
        ]


class VendorShipmentLineItemSerializer(drf_serializers.ModelSerializer):
    """Writable nested line payload.

    ``vendorshipid`` is not accepted — the parent header PK is attached after
    the header has been created.
    """

    class Meta:
        model = VendorShipmentLine
        fields = [
            'poid',
            'costcardid',
            'pcs',
            'metalwt',
            'diawt',
            'stplace',
            'colwt',
            'labour',
            'finding',
            'triounce',
            'confrm',
            'active',
        ]


class VendorShipmentSerializer(
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    """Serializer for the VendorShipment model (read + header-only update)."""

    lines = VendorShipmentLineSerializer(
        many=True,
        read_only=True,
    )

    vendor_name = drf_serializers.CharField(
        source='vendorid.name',
        read_only=True,
        default=None,
    )

    courier_name = drf_serializers.CharField(
        source='courierid.name',
        read_only=True,
        default=None,
    )

    is_open = drf_serializers.SerializerMethodField()

    def get_is_open(self, obj):
        return obj.lines.filter(confrm__isnull=True).exists()

    class Meta:
        model = VendorShipment
        fields = [
            'pk',
            'vsno',
            'vsdate',
            'vendorid',
            'vendor_name',
            'courierid',
            'courier_name',
            'trackref',
            'luser',
            'active',
            'created_at',
            'updated_at',
            'is_open',
            'lines',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'is_open',
        ]


class VendorShipmentCreateSerializer(InvenTreeModelSerializer):
    """Create a shipment header together with its ``lines[]`` in one POST.

    The header is saved first, then every line is created with that header as
    ``vendorshipid`` — both inside a single ``transaction.atomic()`` block.
    """

    lines = VendorShipmentLineItemSerializer(
        many=True,
        required=False,
    )

    vendor_name = drf_serializers.CharField(
        source='vendorid.name',
        read_only=True,
        default=None,
    )

    courier_name = drf_serializers.CharField(
        source='courierid.name',
        read_only=True,
        default=None,
    )

    class Meta:
        model = VendorShipment
        fields = [
            'pk',
            'vsno',
            'vsdate',
            'vendorid',
            'vendor_name',
            'courierid',
            'courier_name',
            'trackref',
            'luser',
            'active',
            'created_at',
            'updated_at',
            'lines',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
        ]

    def skip_create_fields(self):
        fields = list(super().skip_create_fields())

        if 'lines' not in fields:
            fields.append('lines')

        return fields

    def create(self, validated_data):
        lines = validated_data.pop('lines', []) or []

        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if (
            user is not None
            and getattr(user, 'is_authenticated', False)
            and not validated_data.get('luser')
        ):
            validated_data['luser'] = user.get_username()

        with transaction.atomic():
            shipment = VendorShipment.objects.create(**validated_data)

            for line in lines:
                VendorShipmentLine.objects.create(
                    vendorshipid=shipment,
                    **line,
                )

        return shipment