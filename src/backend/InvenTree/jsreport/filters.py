"""Helper functions for the 'jsreport' app."""

from decimal import ROUND_HALF_UP, Decimal

from django.db.models import (
    DateField, DecimalField, ExpressionWrapper, F, IntegerField, Max, OuterRef, Q, Subquery,
    Sum, Value,
)
from django.db.models.functions import Coalesce, Greatest
from django.utils.dateparse import parse_date

from purchase_order.models import PurchaseOrderLine
from requisition.models import FluteEntryLine
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

    side = Q(stone_type='diamond', stone_place__name__iregex=r'^(left|right|side)$')
    center = Q(stone_type='diamond', stone_place__name__iexact='center')
    color = Q(stone_type='color_stone')  # TODO: confirm color stones are not split by place

    def flute_sets(cond):
        return Subquery(
            FluteEntryLine.objects
            .filter(
                cond,
                purchase_order_id=OuterRef('poid_id'),
                cost_card_id=OuterRef('costcardid_id'),
                active=True,
                flute_entry__active=True,
            )
            .order_by()
            .values('purchase_order_id', 'cost_card_id')
            .annotate(total=Sum('sets'))
            .values('total'),
            output_field=DecimalField(max_digits=15, decimal_places=2),
        )

    def flute_date(cond):
        return Subquery(
            FluteEntryLine.objects
            .filter(
                cond,
                purchase_order_id=OuterRef('poid_id'),
                cost_card_id=OuterRef('costcardid_id'),
                active=True,
                flute_entry__active=True,
            )
            .order_by()
            .values('purchase_order_id', 'cost_card_id')
            # TODO: confirm latest flute date is the one the client shows
            .annotate(last=Max('flute_entry__flute_date'))
            .values('last'),
            output_field=DateField(),
        )

    zero = Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))

    def set_left(key):
        return ExpressionWrapper(
            Coalesce(F(key), zero) - F('shipqty'),
            output_field=DecimalField(max_digits=15, decimal_places=2),
        )

    qs = (
        PurchaseOrderLine.objects
        .filter(poid__potype='ORDER', poid__active=True)
        # TODO: confirm whether cancelled P.O.s (poid__canc_dt) must be excluded
        .select_related('poid', 'poid__customerid', 'poid__vendorid', 'poid__acexeid')
        .annotate(
            shipqty=Coalesce(Subquery(received, output_field=IntegerField()), Value(0)),
            side_flute=flute_sets(side),
            center_flute=flute_sets(center),
            color_flute=flute_sets(color),
            side_date=flute_date(side),
            center_date=flute_date(center),
            color_date=flute_date(color),
        )
        .annotate(
            balqty=Greatest(
                F('qty') - F('shipqty'),
                Value(0),
                output_field=IntegerField(),
            ),
            # stone sets sent on flute entries, less pieces already shipped (matches client sheet)
            side_set=set_left('side_flute'),
            center_set=set_left('center_flute'),
            color_set=set_left('color_flute'),
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


STONE_DEC = DecimalField(max_digits=15, decimal_places=4)
TWO_DP = Decimal('0.01')


def _line_sum(queryset, po_field, card_field, value_field):
    """Sum of value_field for rows matching the outer P.O. line's (poid, costcardid)."""
    return Coalesce(
        Subquery(
            queryset
            .filter(**{po_field: OuterRef('poid_id'), card_field: OuterRef('costcardid_id')})
            .order_by()
            .values(po_field, card_field)
            .annotate(total=Sum(value_field))
            .values('total'),
            output_field=STONE_DEC,
        ),
        Value(0, output_field=STONE_DEC),
    )


def get_po_stone_valuation_queryset(date_from=None, date_to=None, vendorid=None):
    """P.O. Stone Valuation rows: one row per P.O. line, filtered on P.O. date.

    Issued stones come from flute entries, received stones from vendor shipments.
    """
    flute = FluteEntryLine.objects.filter(active=True, flute_entry__active=True)
    diamond = flute.filter(stone_type='diamond')
    color = flute.filter(stone_type='color_stone')
    shipments = VendorShipmentLine.objects.all()

    po_f, card_f = 'purchase_order_id', 'cost_card_id'
    po_s, card_s = 'poid_id', 'costcardid_id'

    qs = (
        PurchaseOrderLine.objects
        .filter(poid__potype='ORDER', poid__active=True)
        .select_related('poid', 'poid__vendorid', 'costcardid')
        .annotate(
            issue_dia_cts=_line_sum(diamond, po_f, card_f, 'cts'),
            issue_dia_amount=_line_sum(diamond, po_f, card_f, 'amount'),
            issue_col_cts=_line_sum(color, po_f, card_f, 'cts'),
            issue_col_amount=_line_sum(color, po_f, card_f, 'amount'),
            rec_dia_cts=_line_sum(shipments, po_s, card_s, 'diawt'),
            rec_col_cts=_line_sum(shipments, po_s, card_s, 'colwt'),
            ship_pcs=_line_sum(shipments, po_s, card_s, 'pcs'),
        )
    )

    date_from = parse_date(date_from) if date_from else None
    date_to = parse_date(date_to) if date_to else None

    if date_from:
        qs = qs.filter(poid__podate__gte=date_from)

    if date_to:
        qs = qs.filter(poid__podate__lte=date_to)

    if vendorid:
        qs = qs.filter(poid__vendorid_id=vendorid)

    return qs.order_by('poid__pono', 'styleno', 'pk')


def get_stone_valuation_figures(line):
    """Displayed figures for one P.O. line (cached on the instance).

    Rate = issued amount / issued cts, rounded to 2 places. Balance amount = displayed
    balance cts x rate. Balances may go negative (over-received), as in the client sheet.
    """
    cached = getattr(line, '_stone_figures', None)
    if cached is not None:
        return cached

    def two(value):
        return Decimal(value).quantize(TWO_DP, rounding=ROUND_HALF_UP)

    def kind(issue_cts, issue_amount, rec_cts):
        issue = two(issue_cts)
        received = two(rec_cts)
        rate = two(issue_amount / issue_cts) if issue_cts else Decimal('0.00')
        balance = issue - received
        return {
            'issue_cts': issue,
            'issue_rate': rate,
            'issue_amount': two(issue_amount),
            'rec_cts': received,
            'bal_cts': balance,
            'bal_amount': two(balance * rate),
        }

    figures = {
        'dia': kind(line.issue_dia_cts, line.issue_dia_amount, line.rec_dia_cts),
        'col': kind(line.issue_col_cts, line.issue_col_amount, line.rec_col_cts),
        'bal_pcs': (line.qty or 0) - int(line.ship_pcs or 0),
    }
    line._stone_figures = figures
    return figures