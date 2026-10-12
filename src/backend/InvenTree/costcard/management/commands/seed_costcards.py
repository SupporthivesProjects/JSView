from decimal import ROUND_HALF_UP, Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from costcard.models import (
    CostCard,
    CostCardColorStoneLine,
    CostCardDiamondLine,
    CostCardFinishLine,
    StonePlace,
)
from company.models import Company
from master.models import (
    FindingItem,
    FindingType,
    FinishType,
    JewelryCategory,
    JewelrySubCategory,
    MetalPurity,
    Setting,
)
from properties.models import (
    ColorStone,
    ColorStoneColor,
    ColorStoneCut,
    ColorStoneQuality,
    ColorStoneShape,
    ColorStoneSize,
    DiamondColor,
    DiamondCut,
    DiamondQuality,
    DiamondShape,
    DiamondSize,
    DiamondStone,
)

ZERO = Decimal('0')
CENT = Decimal('0.01')
FOUR = Decimal('0.0001')
THREE = Decimal('0.001')
HUNDRED = Decimal('100')
TROY_OUNCE_GRAMS = Decimal('31.1035')
STONE_WEIGHT_PER_CT = Decimal('0.2')

SEEDS = [
    {
        'our_style_no': 'SEED-RING-001',
        'vendor_style_no': 'V-RING-001',
        'metal_grams': Decimal('4.500'),
        'karat': 14,
        'troy_ounce_price': Decimal('2400.00'),
        'finding_price': Decimal('4.00'),
        'metal_loss_pct': Decimal('8'),
        'dia_handling_pct': Decimal('2'),
        'col_handling_pct': Decimal('0'),
        'vendor_markup_pct': Decimal('3'),
        'duty_pct': Decimal('10'),
        'margin_pct': Decimal('15'),
        'diamonds': [
            {'pcs': 12, 'cts': Decimal('0.3600'), 'pc': 'C', 'rate': Decimal('900'), 'labour_rate': Decimal('40')},
            {'pcs': 1, 'cts': Decimal('0.5000'), 'pc': 'C', 'rate': Decimal('1800'), 'labour_rate': Decimal('60')},
        ],
        'colorstones': [],
        'finishes': [Decimal('3.50')],
    },
    {
        'our_style_no': 'SEED-PENDANT-002',
        'vendor_style_no': 'V-PEND-002',
        'metal_grams': Decimal('3.250'),
        'karat': 18,
        'troy_ounce_price': Decimal('2400.00'),
        'finding_price': Decimal('2.50'),
        'metal_loss_pct': Decimal('10'),
        'dia_handling_pct': Decimal('2'),
        'col_handling_pct': Decimal('1.5'),
        'vendor_markup_pct': Decimal('2'),
        'duty_pct': Decimal('10'),
        'margin_pct': Decimal('20'),
        'diamonds': [
            {'pcs': 8, 'cts': Decimal('0.2400'), 'pc': 'C', 'rate': Decimal('750'), 'labour_rate': Decimal('35')},
        ],
        'colorstones': [
            {'pcs': 1, 'cts': Decimal('1.2000'), 'pc': 'C', 'rate': Decimal('120'), 'labour_rate': Decimal('15')},
            {'pcs': 4, 'cts': Decimal('0.4000'), 'pc': 'P', 'rate': Decimal('6.50'), 'labour_rate': Decimal('1.20')},
        ],
        'finishes': [Decimal('2.00'), Decimal('1.25')],
    },
    {
        'our_style_no': 'SEED-EARRING-003',
        'vendor_style_no': 'V-EAR-003',
        'metal_grams': Decimal('6.800'),
        'karat': 10,
        'troy_ounce_price': Decimal('2400.00'),
        'finding_price': Decimal('6.00'),
        'metal_loss_pct': Decimal('6'),
        'dia_handling_pct': Decimal('0'),
        'col_handling_pct': Decimal('0'),
        'vendor_markup_pct': Decimal('0'),
        'duty_pct': Decimal('5'),
        'margin_pct': Decimal('12'),
        'diamonds': [
            {'pcs': 20, 'cts': Decimal('0.6000'), 'pc': 'P', 'rate': Decimal('14.00'), 'labour_rate': Decimal('0.80')},
        ],
        'colorstones': [],
        'finishes': [],
    },
]


def money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def carats(value):
    return Decimal(value).quantize(FOUR, rounding=ROUND_HALF_UP)


def percent_of(base, pct):
    return money(Decimal(base) * Decimal(pct or 0) / HUNDRED)


def pick(model, index):
    rows = list(model.objects.all()[:20])

    if not rows:
        return None

    return rows[index % len(rows)]


def line_quantity(line):
    return Decimal(line.pcs or 0) if line.pc == 'P' else Decimal(line.cts or 0)


def apply_line_amounts(line):
    quantity = line_quantity(line)
    line.amount = money(Decimal(line.rate or 0) * quantity)
    line.labour_amount = money(Decimal(line.labour_rate or 0) * quantity)


def recalculate(card):
    diamond_lines = list(card.diamond_lines.all())
    color_lines = list(card.colorstone_lines.all())
    finish_lines = list(card.finish_lines.all())

    for line in diamond_lines + color_lines:
        apply_line_amounts(line)
        line.save(update_fields=['amount', 'labour_amount', 'updated_at'])

    card.dia_pcs = sum(line.pcs for line in diamond_lines)
    card.dia_cts = carats(sum((line.cts for line in diamond_lines), ZERO))
    card.dia_amount = money(sum((line.amount for line in diamond_lines), ZERO))

    card.col_pcs = sum(line.pcs for line in color_lines)
    card.col_cts = carats(sum((line.cts for line in color_lines), ZERO))
    card.col_amount = money(sum((line.amount for line in color_lines), ZERO))

    card.stone_pcs = card.dia_pcs + card.col_pcs
    card.stone_cts = carats(card.dia_cts + card.col_cts)
    card.stone_amount = money(card.dia_amount + card.col_amount)

    card.labour_finish_amount = money(sum((line.rate for line in finish_lines), ZERO))
    card.labour_diamond_amount = money(sum((line.labour_amount for line in diamond_lines), ZERO))
    card.labour_colorstone_amount = money(sum((line.labour_amount for line in color_lines), ZERO))
    card.labour_amount = money(
        card.labour_finish_amount + card.labour_diamond_amount + card.labour_colorstone_amount
    )

    if card.metal_grams and card.karat and card.troy_ounce_price:
        value = (
            Decimal(card.metal_grams)
            * Decimal(card.troy_ounce_price)
            / TROY_OUNCE_GRAMS
            * Decimal(card.karat)
            / Decimal(24)
        )
        card.metal_loss_amount = percent_of(value, card.metal_loss_pct)
        card.metal_amount = money(value) + card.metal_loss_amount

    card.dia_handling_amount = percent_of(card.dia_amount, card.dia_handling_pct)
    card.col_handling_amount = percent_of(card.col_amount, card.col_handling_pct)

    base = (
        card.metal_amount
        + card.stone_amount
        + card.labour_amount
        + card.finding_price
        + card.dia_handling_amount
        + card.col_handling_amount
    )
    card.vendor_markup_amount = percent_of(base, card.vendor_markup_pct)
    card.fob = money(base + card.vendor_markup_amount)
    card.duty_amount = percent_of(card.fob, card.duty_pct)
    card.margin_amount = percent_of(card.fob + card.duty_amount, card.margin_pct)
    card.final_amount = money(card.fob + card.duty_amount + card.margin_amount)

    card.save()


def stone_references(index, kind):
    if kind == 'diamond':
        return {
            'stone': pick(DiamondStone, index),
            'shape': pick(DiamondShape, index),
            'mm_size': pick(DiamondSize, index),
            'color': pick(DiamondColor, index),
            'cut': pick(DiamondCut, index),
            'quality': pick(DiamondQuality, index),
            'setting': pick(Setting, index),
            'stone_place': pick(StonePlace, index),
        }

    return {
        'stone': pick(ColorStone, index),
        'shape': pick(ColorStoneShape, index),
        'mm_size': pick(ColorStoneSize, index),
        'color': pick(ColorStoneColor, index),
        'cut': pick(ColorStoneCut, index),
        'quality': pick(ColorStoneQuality, index),
        'setting': pick(Setting, index),
        'stone_place': pick(StonePlace, index),
    }


def seed_card(index, spec):
    defaults = {
        'vendor_style_no': spec['vendor_style_no'],
        'vendor': pick(Company, index),
        'customer': pick(Company, index + 1),
        'category': pick(JewelryCategory, index),
        'sub_category': pick(JewelrySubCategory, index),
        'metal_purity': pick(MetalPurity, index),
        'karat': spec['karat'],
        'metal_grams': spec['metal_grams'],
        'net_weight': spec['metal_grams'],
        'finding_type': pick(FindingType, index),
        'finding_item': pick(FindingItem, index),
        'finding_price': spec['finding_price'],
        'troy_ounce_price': spec['troy_ounce_price'],
        'metal_loss_pct': spec['metal_loss_pct'],
        'dia_handling_pct': spec['dia_handling_pct'],
        'col_handling_pct': spec['col_handling_pct'],
        'vendor_markup_pct': spec['vendor_markup_pct'],
        'duty_pct': spec['duty_pct'],
        'margin_pct': spec['margin_pct'],
        'active': True,
    }
    card, created = CostCard.objects.update_or_create(
        our_style_no=spec['our_style_no'], defaults=defaults
    )

    card.diamond_lines.all().delete()
    card.colorstone_lines.all().delete()
    card.finish_lines.all().delete()

    for position, row in enumerate(spec['diamonds']):
        CostCardDiamondLine.objects.create(
            cost_card=card,
            pcs=row['pcs'],
            cts=row['cts'],
            pc=row['pc'],
            rate=row['rate'],
            labour_rate=row['labour_rate'],
            default_rate='no',
            **stone_references(index + position, 'diamond'),
        )

    for position, row in enumerate(spec['colorstones']):
        CostCardColorStoneLine.objects.create(
            cost_card=card,
            pcs=row['pcs'],
            cts=row['cts'],
            pc=row['pc'],
            rate=row['rate'],
            labour_rate=row['labour_rate'],
            default_rate='no',
            **stone_references(index + position, 'colorstone'),
        )

    finish_types = list(FinishType.objects.all()[: len(spec['finishes'])])

    for finish_type, rate in zip(finish_types, spec['finishes']):
        CostCardFinishLine.objects.create(cost_card=card, finish_type=finish_type, rate=rate)

    recalculate(card)

    card.gross_weight = (
        Decimal(card.net_weight) + Decimal(card.stone_cts) * STONE_WEIGHT_PER_CT
    ).quantize(THREE, rounding=ROUND_HALF_UP)
    card.save()

    return card, created


def recalculate_existing(ids):
    queryset = CostCard.objects.all()

    if ids:
        queryset = queryset.filter(pk__in=ids)

    done = []
    skipped = []

    for card in queryset:
        has_lines = (
            card.diamond_lines.exists()
            or card.colorstone_lines.exists()
            or card.finish_lines.exists()
        )

        if not has_lines:
            skipped.append(card)
            continue

        recalculate(card)
        done.append(card)

    return done, skipped


class Command(BaseCommand):
    help = 'Seed consistent cost cards and optionally recalculate existing ones.'

    def add_arguments(self, parser):
        parser.add_argument('--skip-seed', action='store_true')
        parser.add_argument('--recalc', action='store_true')
        parser.add_argument('--ids', nargs='+', type=int)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        with transaction.atomic():
            if not options['skip_seed']:
                for index, spec in enumerate(SEEDS):
                    card, created = seed_card(index, spec)
                    self.stdout.write(
                        f"{'created' if created else 'updated'} card {card.cost_card_no} "
                        f"{card.our_style_no}: fob {card.fob}, duty {card.duty_amount}, "
                        f"margin {card.margin_amount}, final {card.final_amount}"
                    )

            if options['recalc']:
                done, skipped = recalculate_existing(options['ids'])

                for card in done:
                    self.stdout.write(
                        f"recalculated card {card.cost_card_no} {card.our_style_no}: "
                        f"fob {card.fob}, final {card.final_amount}"
                    )

                for card in skipped:
                    self.stdout.write(
                        f"skipped card {card.cost_card_no} {card.our_style_no}: no stone or finish lines"
                    )

            if options['dry_run']:
                transaction.set_rollback(True)
                self.stdout.write('dry run: all changes rolled back')


# python manage.py seed_costcards
# python manage.py seed_costcards --skip-seed --recalc