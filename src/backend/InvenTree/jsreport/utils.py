"""Helper functions for the 'jsreport' app."""

from django.db.models import F, IntegerField, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce, Greatest

from purchase_order.models import PurchaseOrderLine
from vendor_shipment.models import VendorShipmentLine


def get_open_order_queryset(vendorid=None, customerid=None):
    """Open Order rows: one row per P.O. line whose balance is above 0.

    Same rule as ``vendor_shipment.utils``:
    balance = max(0, ordered qty - shipped pcs), matched on (poid, costcardid).

    * vendorid   -> vendorwise export
    * customerid -> customerwise export
    * neither    -> all vendor export
    """
    received = (
        VendorShipmentLine.objects
        .filter(poid_id=OuterRef('poid_id'), costcardid_id=OuterRef('costcardid_id'))
        .order_by()
        .values('poid_id', 'costcardid_id')
        .annotate(total=Sum('pcs'))
        .values('total')
    )

    qs = (
        PurchaseOrderLine.objects
        .filter(poid__potype='ORDER', poid__active=True)
        # TODO: confirm whether cancelled P.O.s (poid__canc_dt) must be excluded
        .select_related('poid', 'poid__customerid', 'poid__vendorid', 'poid__acexeid')
        .annotate(
            balqty=Greatest(
                F('qty') - Coalesce(
                    Subquery(received, output_field=IntegerField()), Value(0)
                ),
                Value(0),
                output_field=IntegerField(),
            )
        )
        .filter(balqty__gt=0)
    )

    if vendorid:
        qs = qs.filter(poid__vendorid_id=vendorid)

    if customerid:
        qs = qs.filter(poid__customerid_id=customerid)

    # TODO: confirm legacy sort order
    return qs.order_by('poid__customerid__code', 'poid__podate', 'poid__pono', 'pk')