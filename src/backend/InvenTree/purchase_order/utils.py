"""Utility functions for the purchase_order app.

Replicates the fn_getpono PostgreSQL function in pure Python/Django ORM,
plus frozen POCostCard snapshot creation (mirrors legacy tbpocostcard1/2).
"""

from datetime import date

from django.db import connection, transaction
from django.db.models import Max

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
    # Get ccode from tbledger via raw SQL
    ccode = 'UNK'
    if customerid is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT ccode FROM tbledger WHERE ledgerid = %s',
                [customerid],
            )
            row = cursor.fetchone()
            if row and row[0]:
                ccode = row[0]

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
            costcardno=costcard.cost_card_no,
            our_style_no=costcard.our_style_no,
            vendor_style_no=costcard.vendor_style_no,
            vendor=costcard.vendor,
            customer=costcard.customer,
            karat=costcard.karat,
            metal_grams=costcard.metal_grams,
            net_weight=costcard.net_weight,
            gross_weight=costcard.gross_weight,
            troy_ounce_price=costcard.troy_ounce_price,
            finding_price=costcard.finding_price,
            metal_loss_pct=costcard.metal_loss_pct,
            metal_loss_amount=costcard.metal_loss_amount,
            metal_amount=costcard.metal_amount,
            dia_pcs=costcard.dia_pcs,
            dia_cts=costcard.dia_cts,
            dia_amount=costcard.dia_amount,
            col_pcs=costcard.col_pcs,
            col_cts=costcard.col_cts,
            col_amount=costcard.col_amount,
            stone_pcs=costcard.stone_pcs,
            stone_cts=costcard.stone_cts,
            stone_amount=costcard.stone_amount,
            labour_amount=(
                costcard.labour_amount
                or (
                    costcard.labour_finish_amount
                    + costcard.labour_diamond_amount
                    + costcard.labour_colorstone_amount
                )
            ),
            dia_handling_pct=costcard.dia_handling_pct,
            dia_handling_amount=costcard.dia_handling_amount,
            col_handling_pct=costcard.col_handling_pct,
            col_handling_amount=costcard.col_handling_amount,
            vendor_markup_pct=costcard.vendor_markup_pct,
            vendor_markup_amount=costcard.vendor_markup_amount,
            fob=costcard.fob,
            duty_pct=costcard.duty_pct,
            duty_amount=costcard.duty_amount,
            margin_pct=costcard.margin_pct,
            margin_amount=costcard.margin_amount,
            final_amount=costcard.final_amount,
            category=costcard.category,
            sub_category=costcard.sub_category,
            metal_purity=costcard.metal_purity,
            stnoauto=po_line.stnoauto,
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
                pcs=line.pcs,
                cts=line.cts,
                rate=line.rate,
                pc=line.pc,
                amount=line.amount,
                labour_rate=line.labour_rate,
                labour_amount=line.labour_amount,
                default_rate=line.default_rate,
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
                pcs=line.pcs,
                cts=line.cts,
                rate=line.rate,
                pc=line.pc,
                amount=line.amount,
                labour_rate=line.labour_rate,
                labour_amount=line.labour_amount,
                default_rate=line.default_rate,
            )
            for line in costcard.colorstone_lines.all()
        ])

        # 5d. Freeze finish lines (etype='FINISHTYPE'; name stored in `stone`)
        POCostCardLine.objects.bulk_create([
            POCostCardLine(
                po_costcard=po_costcard,
                etype='FINISHTYPE',
                stone=_name(line.finish_type),
                rate=line.rate,
                amount=line.rate,
            )
            for line in costcard.finish_lines.all()
        ])
