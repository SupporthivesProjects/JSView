from django.db import transaction
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


class PurchaseOrderLineItemSerializer(drf_serializers.ModelSerializer):
    """Writable line payload nested under header create (`items`).

    `poid` is not accepted — the parent header PK is attached after create.
    """

    class Meta:
        model = PurchaseOrderLine
        fields = [
            'costcardid', 'styleno', 'vstyleno', 'vendorid',
            'qty', 'size', 'spcs', 'stnoauto', 'active',
        ]


class PurchaseOrderSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the PurchaseOrder model.

    POST may include ``items`` (po-lines). The header is saved first, then
    each item is created with that header as ``poid``.
    ``prepby`` is always the authenticated InvenTree user on create.
    """

    lines = PurchaseOrderLineSerializer(many=True, read_only=True)
    items = PurchaseOrderLineItemSerializer(many=True, required=False, write_only=True)

    prepby = drf_serializers.PrimaryKeyRelatedField(read_only=True)
    prepby_username = drf_serializers.CharField(
        source='prepby.username', read_only=True, default=None, allow_null=True,
    )

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
            'linkid', 'potype', 'pono', 'npono', 'nyear', 'podate',
            'prepby', 'prepby_username',
            'ddate', 'vcsdate', 'esdstone',
            'customerid', 'customer_pono', 'customer_name',
            'pocategory', 'rem', 'note',
            'stampid', 'stamp_name',
            'acexeid', 'acexe_name',
            'vendorid', 'vendor_name',
            'tqty',
            'termsid', 'terms_name',
            'luser',
            'canc_dt', 'canc_rem', 'canc_user',
            'active', 'created_at', 'updated_at',
            'lines', 'items',
        ]
        read_only_fields = [
            'pono', 'npono', 'nyear', 'prepby',
            'created_at', 'updated_at',
        ]

    def skip_create_fields(self):
        fields = list(super().skip_create_fields())
        if 'items' not in fields:
            fields.append('items')
        return fields

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self._items = attrs.pop('items', [])
        return attrs

    def create(self, validated_data):
        validated_data.pop('items', None)

        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is not None and getattr(user, 'is_authenticated', False):
            validated_data['prepby'] = user
            if not validated_data.get('luser'):
                validated_data['luser'] = user.get_username()

        with transaction.atomic():
            instance = super().create(validated_data)
            total_qty = 0
            for item in getattr(self, '_items', []) or []:
                line = PurchaseOrderLine(poid=instance, **item)
                line.save()
                total_qty += line.qty or 0
            if total_qty and not instance.tqty:
                instance.tqty = total_qty
                PurchaseOrder.objects.filter(pk=instance.pk).update(tqty=total_qty)
                instance.tqty = total_qty
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('items', None)
        validated_data.pop('prepby', None)
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is not None and getattr(user, 'is_authenticated', False):
            validated_data['luser'] = user.get_username()
        return super().update(instance, validated_data)
