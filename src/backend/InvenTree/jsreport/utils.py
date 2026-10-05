"""Helper functions for the 'jsreport' app."""

from decimal import Decimal

from django.db.models import F, IntegerField, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce, Greatest

from purchase_order.models import PurchaseOrderLine
from vendor_shipment.models import VendorShipmentLine

TROY_OZ_GRAMS = Decimal('31.1035')
OTHER_EXP_PCT = Decimal('1')  # TODO: confirm, inferred from the sample (0.84 = 1% of 83.85)


def _get_order_line_queryset(vendorid=None, customerid=None):
    """Base P.O. line queryset annotated with shipqty and balqty.

    balance = max(0, ordered qty - shipped pcs), matched on (poid, costcardid).
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
            shipqty=Coalesce(Subquery(received, output_field=IntegerField()), Value(0)),
        )
        .annotate(
            balqty=Greatest(
                F('qty') - F('shipqty'),
                Value(0),
                output_field=IntegerField(),
            )
        )
    )

    if vendorid:
        qs = qs.filter(poid__vendorid_id=vendorid)

    if customerid:
        qs = qs.filter(poid__customerid_id=customerid)

    return qs


def get_open_order_queryset(vendorid=None, customerid=None):
    """Open Order rows: one row per P.O. line whose balance is above 0."""
    qs = _get_order_line_queryset(vendorid, customerid).filter(balqty__gt=0)

    # TODO: confirm legacy sort order
    return qs.order_by('poid__customerid__code', 'poid__podate', 'poid__pono', 'pk')


def get_close_order_queryset(vendorid=None, customerid=None):
    """Close Order rows: one row per P.O. line fully shipped (balance = 0)."""
    # TODO: confirm close rule with client (balance 0 assumed)
    qs = _get_order_line_queryset(vendorid, customerid).filter(qty__gt=0, balqty=0)

    # TODO: confirm legacy sort order
    return qs.order_by('poid__customerid__code', 'poid__podate', 'poid__pono', 'pk')


def get_invoice_value_queryset(vendorid=None, vsno=None):
    """Invoice Value P/C rows: one row per shipment line of the selected invoice."""
    qs = (
        VendorShipmentLine.objects
        .filter(active=True, vendorshipid__active=True)
        .select_related('vendorshipid', 'vendorshipid__vendorid', 'poid', 'costcardid')
    )

    if vendorid:
        qs = qs.filter(vendorshipid__vendorid_id=vendorid)

    if vsno:
        qs = qs.filter(vendorshipid__vsno=vsno)

    return qs.order_by('vendorshipid__vsno', 'poid__pono', 'pk')


def get_invoice_figures(line):
    """Per-piece figures for one shipment line (cached on the instance)."""
    cached = getattr(line, '_inv_figures', None)
    if cached is not None:
        return cached

    card = line.costcardid
    pcs = Decimal(line.pcs or 0)

    def per_pc(value):
        return (value / pcs) if pcs else Decimal('0')

    avg_netwt = per_pc(line.metalwt)
    avg_cts = per_pc(line.diawt)
    avg_labor = per_pc(line.labour)

    karat = Decimal(card.karat or 0) if card else Decimal('0')
    loss_pct = card.metal_loss_pct if card else Decimal('0')
    duty_pct = card.duty_pct if card else Decimal('0')
    # TODO: confirm, stone rate per carat taken from the cost card (dia_amount / dia_cts)
    dia_rate = (card.dia_amount / card.dia_cts) if card and card.dia_cts else Decimal('0')

    # TODO: confirm metal formula against a sample with a non-zero net weight
    avg_metal = avg_netwt * (line.triounce / TROY_OZ_GRAMS) * (karat / 24) * (1 + loss_pct / 100)
    cts_value = avg_cts * dia_rate
    base = avg_metal + avg_labor + cts_value
    duty = base * duty_pct / 100
    other = base * OTHER_EXP_PCT / 100

    figures = {
        'avg_netwt': avg_netwt,
        'avg_cts': avg_cts,
        'avg_labor': avg_labor,
        'avg_cts_value': cts_value,
        'avg_metal': avg_metal,
        'duty': duty,
        'other': other,
        'per_pc': base + duty + other,
    }
    line._inv_figures = figures
    return figures