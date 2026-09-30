"""Utility functions for the purchase_order app.

Replicates the fn_getpono PostgreSQL function in pure Python/Django ORM,
plus frozen POCostCard snapshot creation (mirrors legacy tbpocostcard1/2).
"""

from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Max

from company.models import Company

from .models import PurchaseOrder

# POCategories treated as "sample" for numbering purposes
SAMPLE_CATEGORIES = [
    'Sample',
    'CZ Sample',
    'CZ Host Sample',
    'Photo Sample',
]


def generate_po_number(
    potype: str,
    pocategory: str,
    customerid: int | None,
    podate: date,
) -> tuple[str, int]:
    """
    Replicate fn_getpono PostgreSQL function.

    Generates a PO number in the format: ``{ccode} {year}-{npono:04d} {prefix}``

    Returns:
        Tuple of (pono: str, npono: int)
    """
    # Get ccode from Company model
    ccode = 'UNK'
    if customerid is not None:
        try:
            ccode = Company.objects.get(pk=customerid).code or 'UNK'
        except Company.DoesNotExist:
            ccode = 'UNK'

    # Determine the year from podate
    nyear = podate.year if podate else date.today().year

    # Determine prefix and filter
    is_sample = pocategory in SAMPLE_CATEGORIES

    if is_sample:
        prefix = 'S'
    else:
        prefix = 'P'

    # Find the max npono for the same year, potype, and sample/non-sample group
    queryset = PurchaseOrder.objects.filter(
        nyear=nyear,
        potype=potype,
    )

    if is_sample:
        queryset = queryset.filter(pocategory__in=SAMPLE_CATEGORIES)
    else:
        queryset = queryset.exclude(pocategory__in=SAMPLE_CATEGORIES)

    max_npono = queryset.aggregate(max_npono=Max('npono'))['max_npono']

    if max_npono is not None:
        npono = max_npono + 1
    else:
        npono = 1

    pono = f'{ccode} {nyear}-{npono:04d} {prefix}'

    return pono, npono


def _name(obj) -> str | None:
    """Freeze a lookup record to its display name (None-safe)."""
    if obj is None:
        return None
    return str(obj)


def _s(value) -> str:
    """Text for a NOT NULL text column: None becomes an empty string."""
    return '' if value is None else value


def _d(value) -> Decimal:
    """Number for a NOT NULL decimal column: None becomes 0."""
    return Decimal('0') if value is None else value


def _i(value) -> int:
    """Number for a NOT NULL integer column: None becomes 0."""
    return 0 if value is None else value


def _default_rate_flag(value) -> bool:
    """Coerce a cost card D.R. value to the boolean frozen flag.

    ``CostCardStoneLineMixin.default_rate`` stores a 'yes'/'no' string, while
    ``POCostCardLine.default_rate`` is a boolean, so the value has to be
    translated when the snapshot is frozen (legacy boolean values still work).
    """
    if isinstance(value, str):
        return value.strip().lower() in ('yes', 'y', 'true', '1')

    return bool(value)


def create_po_costcard_snapshot(po_line) -> None:
    """
    Called when a PurchaseOrderLine is saved for an ORDER.

    Creates a frozen snapshot of the CostCard into POCostCard /
    POCostCardLine (mirrors the legacy tbpocostcard1/tbpocostcard2 tables).

    Rules:
    - Only for potype='ORDER' (not REQUEST — requests use the live CostCard)
    - If a snapshot already exists for this poid+costcard, skip it
      (enforced by unique_together ['poid', 'costcard'])
    - Copy ALL header fields from CostCard → POCostCard
    - Copy ALL lines from CostCardDiamondLine / CostCardColorStoneLine /
      CostCardFinishLine → POCostCardLine, storing lookup values as
      NAME STRINGS so the snapshot survives deletion of the originals.
    - NULL values on the source cost card are converted to empty / zero
      values for columns that do not allow NULL (e.g. karat).
    """
    po = po_line.poid

    # 1. Only ORDER-type POs get snapshots
    if po.potype != 'ORDER':
        return

    # Get the original CostCard; nothing to snapshot without one
    costcard = po_line.costcardid
    if not costcard:
        return

    # Skip if a snapshot already exists for this poid+costcard
    from .models import POCostCard, POCostCardLine

    if POCostCard.objects.filter(poid=po, costcard=costcard).exists():
        return

    with transaction.atomic():
        # 5a. Freeze the CostCard header
        po_costcard = POCostCard.objects.create(
            poid=po,
            costcard=costcard,
            costcardno=_s(costcard.cost_card_no),
            our_style_no=_s(costcard.our_style_no),
            vendor_style_no=costcard.vendor_style_no,
            vendor=costcard.vendor,
            customer=costcard.customer,
            karat=_s(costcard.karat),
            metal_grams=_d(costcard.metal_grams),
            net_weight=costcard.net_weight,
            gross_weight=costcard.gross_weight,
            troy_ounce_price=costcard.troy_ounce_price,
            finding_price=_d(costcard.finding_price),
            metal_loss_pct=_d(costcard.metal_loss_pct),
            metal_loss_amount=_d(costcard.metal_loss_amount),
            metal_amount=_d(costcard.metal_amount),
            dia_pcs=_i(costcard.dia_pcs),
            dia_cts=_d(costcard.dia_cts),
            dia_amount=_d(costcard.dia_amount),
            col_pcs=_i(costcard.col_pcs),
            col_cts=_d(costcard.col_cts),
            col_amount=_d(costcard.col_amount),
            stone_pcs=_i(costcard.stone_pcs),
            stone_cts=_d(costcard.stone_cts),
            stone_amount=_d(costcard.stone_amount),
            labour_amount=(
                _d(costcard.labour_amount)
                or (
                    _d(costcard.labour_finish_amount)
                    + _d(costcard.labour_diamond_amount)
                    + _d(costcard.labour_colorstone_amount)
                )
            ),
            dia_handling_pct=_d(costcard.dia_handling_pct),
            dia_handling_amount=_d(costcard.dia_handling_amount),
            col_handling_pct=_d(costcard.col_handling_pct),
            col_handling_amount=_d(costcard.col_handling_amount),
            vendor_markup_pct=_d(costcard.vendor_markup_pct),
            vendor_markup_amount=_d(costcard.vendor_markup_amount),
            fob=_d(costcard.fob),
            duty_pct=_d(costcard.duty_pct),
            duty_amount=_d(costcard.duty_amount),
            margin_pct=_d(costcard.margin_pct),
            margin_amount=_d(costcard.margin_amount),
            final_amount=_d(costcard.final_amount),
            category=costcard.category,
            sub_category=costcard.sub_category,
            metal_purity=costcard.metal_purity,
            stnoauto=_i(po_line.stnoauto),
        )

        # 5b. Freeze diamond lines (etype='DIAMOND')
        POCostCardLine.objects.bulk_create([
            POCostCardLine(
                po_costcard=po_costcard,
                etype='DIAMOND',
                stone=_name(line.stone),
                shape=_name(line.shape),
                cut=_name(line.cut),
                colour=_name(line.color),
                quality=_name(line.quality),
                mm_size=_name(line.mm_size),
                sieve_size=line.sieve_size,
                setting=_name(line.setting),
                stone_place=_name(line.stone_place),
                pointer=line.pointer,
                pcs=_i(line.pcs),
                cts=_d(line.cts),
                rate=_d(line.rate),
                pc=line.pc or 'C',
                amount=_d(line.amount),
                labour_rate=_d(line.labour_rate),
                labour_amount=_d(line.labour_amount),
                default_rate=_default_rate_flag(line.default_rate),
            )
            for line in costcard.diamond_lines.all()
        ])

        # 5c. Freeze color stone lines (etype='COLOURSTONE')
        POCostCardLine.objects.bulk_create([
            POCostCardLine(
                po_costcard=po_costcard,
                etype='COLOURSTONE',
                stone=_name(line.stone),
                shape=_name(line.shape),
                cut=_name(line.cut),
                colour=_name(line.color),
                quality=_name(line.quality),
                mm_size=_name(line.mm_size),
                sieve_size=line.sieve_size,
                setting=_name(line.setting),
                stone_place=_name(line.stone_place),
                pointer=line.pointer,
                pcs=_i(line.pcs),
                cts=_d(line.cts),
                rate=_d(line.rate),
                pc=line.pc or 'C',
                amount=_d(line.amount),
                labour_rate=_d(line.labour_rate),
                labour_amount=_d(line.labour_amount),
                default_rate=_default_rate_flag(line.default_rate),
            )
            for line in costcard.colorstone_lines.all()
        ])

        # 5d. Freeze finish lines (etype='FINISHTYPE'; name stored in `stone`)
        POCostCardLine.objects.bulk_create([
            POCostCardLine(
                po_costcard=po_costcard,
                etype='FINISHTYPE',
                stone=_name(line.finish_type),
                rate=_d(line.rate),
                amount=_d(line.rate),
            )
            for line in costcard.finish_lines.all()
        ])