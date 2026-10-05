"""Serializers for the 'jsreport' app."""

from rest_framework import serializers as drf_serializers

from data_exporter.mixins import DataExportSerializerMixin
from InvenTree.serializers import InvenTreeModelSerializer

from purchase_order.models import PurchaseOrderLine

DATE_FMT = '%d %b %Y'  


class OpenOrderSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """One row per open P.O. line. Labels match the Open Order export headers."""

    podate = drf_serializers.DateField(
        source='poid.podate', read_only=True, format=DATE_FMT, label='P.O. Date',
    )
    customer_code = drf_serializers.CharField(
        source='poid.customerid.code', read_only=True, default=None, label='Customer Code',
    )
    vendor_code = drf_serializers.CharField(
        source='poid.vendorid.name', read_only=True, default=None, label='Vendor Code',
    )
    pono = drf_serializers.CharField(
        source='poid.pono', read_only=True, label='P.O. No.',
    )
    customer_pono = drf_serializers.CharField(
        source='poid.customer_pono', read_only=True, default=None, label='Customer P.O. No.',
    )
    styleno = drf_serializers.CharField(read_only=True, label='Style No.')
    qty = drf_serializers.IntegerField(read_only=True, label='Qty.')
    balqty = drf_serializers.IntegerField(read_only=True, label='Bal. Qty.')
    ddate = drf_serializers.DateField(
        source='poid.ddate', read_only=True, format=DATE_FMT, default=None, label='Due Date',
    )
    vcsdate = drf_serializers.DateField(
        source='poid.vcsdate', read_only=True, format=DATE_FMT, default=None,
        label='Vendor Confirmed Ship Date',
    )
    # TODO (step 5): Side / Center / Color Stone Date and Set columns go here
    acexecutive = drf_serializers.CharField(
        source='poid.acexeid.name', read_only=True, default=None, label='A/C Executive',
    )

    class Meta:
        model = PurchaseOrderLine
        fields = [
            'podate', 'customer_code', 'vendor_code', 'pono', 'customer_pono',
            'styleno', 'qty', 'balqty', 'ddate', 'vcsdate', 'acexecutive',
        ]


class CloseOrderSerializer(OpenOrderSerializer):
    """One row per closed (fully shipped) P.O. line.

    Same columns as Open Order, but Bal. Qty. (always 0) is replaced by Shipped Qty.
    """

    balqty = None  # drop inherited column
    shipqty = drf_serializers.IntegerField(read_only=True, label='Shipped Qty.')

    class Meta(OpenOrderSerializer.Meta):
        fields = [
            'podate', 'customer_code', 'vendor_code', 'pono', 'customer_pono',
            'styleno', 'qty', 'shipqty', 'ddate', 'vcsdate', 'acexecutive',
        ]