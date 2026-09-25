"""Reusable openpyxl builder for the cost card presentation workbook.

One "COST BREAKDOWN SHEET" per cost card, all inside a single workbook.
Nothing here touches the database: cards are only read, never saved.

Usage:
    builder = CostCardSheetBuilder(overrides={'duty_pct': '100'}, modified_by='Shekhar')
    data = builder.to_bytes(builder.build(cards))
"""

import re
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
from PIL import Image as PILImage

# TODO: replace with the real company logo path once available (or set
# settings.COST_CARD_LOGO_PATH to point at it).
DEFAULT_LOGO_PATH = getattr(settings, 'COST_CARD_LOGO_PATH', None) or '/opt/inventree/data/static/img/company_logo.png'

FOOTER_TEXT = 'The above quotation is based on current market price and is subject to change at any time without prior notice'
LAST_COL = 16
THIN = Side(style='thin')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
MONEY = '0.00'
MIN_COL_WIDTH = 4
MAX_COL_WIDTH = 26
FIXED_LABOUR_ROWS = 2  # finish-type rows only; a STONE row is always added on top of these

# Professional, grayscale-only heading treatment - no bright colors.
# Section bars / column header rows get the slightly darker tone; individual
# field labels (CC No:, Customer:, row labels, etc.) get the lighter tone.
SECTION_FILL = PatternFill('solid', fgColor='D9D9D9')
LABEL_FILL = PatternFill('solid', fgColor='F2F2F2')

STUDDING_HEADERS = [
    'Type', 'Shape', 'Cut', 'MM Size', 'Sieve Size', 'Stone Type', 'Colour', 'Pointer',
    'Pcs', 'Carats', 'P/C', 'Rate', 'Amount', 'Setting', 'Rate', 'Amount',
]
STUDDING_FORMATS = {10: MONEY, 12: MONEY, 13: MONEY, 15: MONEY, 16: MONEY}
COST_HEADERS = ['Metal', 'Studding', 'Labour', 'Markup %', 'With Markup %', 'F O B', 'Duty %', 'With Duty', 'Margin %', 'Final Price']
COST_KEYS = ['metal', 'studding', 'labour', 'markup_pct', 'markup_amount', 'fob', 'duty_pct', 'with_duty', 'margin_pct', 'final']
COST_COLUMNS = ['F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']


def dec(value):
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    if value in (None, '', 'null'):
        return None
    try:
        return Decimal(str(value).strip())
    except InvalidOperation:
        return None


def num(value):
    return None if value is None else float(value)


def name_of(value):
    return '' if value is None else str(getattr(value, 'name', value))


def size_of(value):
    return '' if value is None else str(value.mm_size or value.name)


def put(ws, ref, value, bold=False, border=True, fmt=None, size=11, fill=None):
    cell = ws[ref]
    cell.value = value
    cell.font = Font(bold=bold, size=size)
    cell.alignment = CENTER
    if border:
        cell.border = BORDER
    if fmt:
        cell.number_format = fmt
    if fill:
        cell.fill = fill
    return cell


def merge(ws, cell_range, value, bold=False, border=True, fmt=None, size=11, fill=None):
    ws.merge_cells(cell_range)
    put(ws, cell_range.split(':')[0], value, bold, border, fmt, size, fill)
    if border:
        for row in ws[cell_range]:
            for cell in row:
                cell.border = BORDER
    if fill:
        for row in ws[cell_range]:
            for cell in row:
                cell.fill = fill


class CostCardSheetBuilder:
    """Builds one sheet per cost card. Every block is its own method, so blocks can be
    switched off, reordered or replaced through `sections`."""

    SECTIONS = ('title', 'header', 'metal', 'studding', 'labour_and_cost', 'design', 'footer')

    def __init__(self, overrides=None, modified_by='', logo_path=None, footer_text=FOOTER_TEXT, sheet_title=None, sections=None):
        self.overrides = {key: dec(value) for key, value in (overrides or {}).items()}
        self.modified_by = modified_by
        self.logo_path = logo_path or DEFAULT_LOGO_PATH
        self.footer_text = footer_text
        self.sheet_title = sheet_title
        self.sections = sections or self.SECTIONS
        self._buffers = []

    def build(self, cards):
        workbook = Workbook()
        workbook.remove(workbook.active)
        used = set()
        for card in cards:
            self.fill_sheet(workbook.create_sheet(self._unique_title(card, used)), card)
        if not workbook.sheetnames:
            workbook.create_sheet('No data')
        return workbook

    def to_bytes(self, workbook):
        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

    def fill_sheet(self, ws, card):
        # Keep the workbook's default gridlines visible everywhere. The explicit thin
        # BORDER boxes drawn per table stay as they are; on top of that we add a single
        # outer frame around the whole data block (see _apply_outer_border below).
        ws.sheet_view.showGridLines = True
        figures = self.figures(card)
        row = 1
        for name in self.sections:
            row = getattr(self, f'_section_{name}')(ws, card, figures, row)
        last_row = row - 1
        self._apply_outer_border(ws, last_row)
        self._autofit_columns(ws)
        self._setup_print(ws, last_row)

    def figures(self, card):
        overrides = self.overrides
        purity = card.metal_purity
        text = f"{name_of(getattr(purity, 'metal_type', None))} {name_of(purity)}".lower()
        price = overrides.get('silver_troy_ounce' if 'silver' in text else 'gold_troy_ounce')
        ratio = price / card.troy_ounce_price if price is not None and card.troy_ounce_price else None

        fob, metal, tr_oz = card.fob, card.metal_amount, card.troy_ounce_price
        if ratio is not None:
            fob += (card.metal_amount + card.metal_loss_amount) * (ratio - 1)
            metal, tr_oz = metal * ratio, price

        duty_pct = overrides['duty_pct'] if overrides.get('duty_pct') is not None else card.duty_pct
        margin_pct = overrides['margin_pct'] if overrides.get('margin_pct') is not None else card.margin_pct

        if any(value is not None for value in overrides.values()):
            with_duty = fob + fob * duty_pct / 100
            final = (with_duty + with_duty * margin_pct / 100).quantize(Decimal('0.01'))
        else:
            with_duty, final = fob + card.duty_amount, card.final_amount

        return {
            'tr_oz': tr_oz,
            'metal': metal,
            'studding': card.stone_amount,
            'labour': card.labour_amount,
            'markup_pct': card.vendor_markup_pct,
            'markup_amount': card.vendor_markup_amount,
            'fob': fob,
            'duty_pct': duty_pct,
            'with_duty': with_duty,
            'margin_pct': margin_pct,
            'final': final,
        }

    def _section_title(self, ws, card, figures, row):
        merge(ws, f'A{row}:P{row}', 'COST BREAKDOWN SHEET', bold=True, border=False, size=14, fill=SECTION_FILL)
        if self.logo_path:
            self._image(ws, self.logo_path, f'B{row + 1}', (80, 80))
            return row + 5
        return row + 1

    def _section_header(self, ws, card, figures, row):
        left = [
            ('CC No :', card.cost_card_no),
            ('Customer :', name_of(card.customer)),
            ('Vendor :', name_of(card.vendor)),
            ('V. Style :', card.vendor_style_no or ''),
        ]
        right = [
            ('Style :', card.our_style_no),
            ('Category :', name_of(card.category)),
            ('Sub Category :', name_of(card.sub_category)),
            ('Date :', timezone.now().strftime('%d %b %Y')),
            ('Modified By :', self.modified_by),
        ]
        for offset, (label, value) in enumerate(left):
            put(ws, f'A{row + offset}', label, fill=LABEL_FILL)
            merge(ws, f'B{row + offset}:C{row + offset}', value)
        for offset, (label, value) in enumerate(right):
            put(ws, f'E{row + offset}', label, fill=LABEL_FILL)
            merge(ws, f'F{row + offset}:G{row + offset}', value)
            ws.row_dimensions[row + offset].height = 22
        if card.front_view:
            self._image(ws, Path(settings.MEDIA_ROOT) / card.front_view.name, f'I{row}', (120, 120))
        return row + 6

    def _section_metal(self, ws, card, figures, row):
        for col, title in zip('ABCDE', ['Type', 'Tr. Oz', 'KT', 'Net Wt.', 'Loss %']):
            put(ws, f'{col}{row}', title, bold=True, fill=SECTION_FILL)
        merge(ws, f'F{row}:G{row}', 'Metal Amount', bold=True, fill=SECTION_FILL)

        purity = card.metal_purity
        values = [
            name_of(getattr(purity, 'metal_type', None)),
            num(figures['tr_oz']),
            card.karat,
            num(card.net_weight),
            num(card.metal_loss_pct),
        ]
        for col, value in zip('ABCDE', values):
            put(ws, f'{col}{row + 1}', value)
        merge(ws, f'F{row + 1}:G{row + 1}', num(figures['metal']), fmt=MONEY)
        return row + 3

    def _section_studding(self, ws, card, figures, row):
        merge(ws, f'A{row}:M{row}', 'Studding Details', bold=True, fill=SECTION_FILL)
        merge(ws, f'N{row}:P{row}', 'Labour', bold=True, fill=SECTION_FILL)
        for col, title in enumerate(STUDDING_HEADERS, start=1):
            put(ws, f'{get_column_letter(col)}{row + 1}', title, bold=True, fill=SECTION_FILL)
        row += 2

        pcs = cts = amount = labour = 0
        for kind, line in self._lines(card):
            values = [
                kind, name_of(line.shape), name_of(line.cut), size_of(line.mm_size), line.sieve_size or '',
                name_of(line.stone), name_of(line.color), num(line.pointer), line.pcs, num(line.cts),
                line.pc, num(line.rate), num(line.amount), name_of(line.setting), num(line.labour_rate), num(line.labour_amount),
            ]
            for col, value in enumerate(values, start=1):
                put(ws, f'{get_column_letter(col)}{row}', value, fmt=STUDDING_FORMATS.get(col))
            pcs += line.pcs
            cts += line.cts
            amount += line.amount
            labour += line.labour_amount
            row += 1

        # Totals row always shows a value (0 when there are no lines) - never blank.
        totals = {8: 'Total', 9: pcs, 10: num(cts), 13: num(amount), 16: num(labour)}
        for col in range(1, LAST_COL + 1):
            put(
                ws, f'{get_column_letter(col)}{row}', totals.get(col),
                bold=col in totals, fmt=STUDDING_FORMATS.get(col),
                fill=LABEL_FILL if col == 8 else None,
            )
        return row + 2

    def _section_labour_and_cost(self, ws, card, figures, row):
        merge(ws, f'A{row}:B{row}', 'Labour Details', bold=True, fill=SECTION_FILL)

        # Fixed layout: always exactly FIXED_LABOUR_ROWS finish-type rows (padded if
        # there are fewer, truncated if there are more) plus one STONE row - always
        # 3 rows total, matching the original template. Missing data shows as 0, not
        # blank, and the STONE row/label is always present.
        finish_rows = [(line.finish_type.name, line.rate) for line in card.finish_lines.all()]
        finish_rows = finish_rows[:FIXED_LABOUR_ROWS]
        while len(finish_rows) < FIXED_LABOUR_ROWS:
            finish_rows.append(('', 0))
        stone_value = sum(line.labour_amount for _, line in self._lines(card))
        labour_rows = finish_rows + [('STONE', stone_value)]

        for offset, (label, value) in enumerate(labour_rows, start=1):
            merge(ws, f'A{row + offset}:B{row + offset}', label, fill=LABEL_FILL)
            put(ws, f'C{row + offset}', num(value) or 0, fmt=MONEY)

        for col, title in zip(COST_COLUMNS, COST_HEADERS):
            put(ws, f'{col}{row}', title, bold=True, fill=SECTION_FILL)
        for col, key in zip(COST_COLUMNS, COST_KEYS):
            put(ws, f'{col}{row + 1}', num(figures[key]), fmt=MONEY)

        return row + len(labour_rows) + 2

    def _section_design(self, ws, card, figures, row):
        merge(ws, f'E{row}:F{row + 2}', 'Design Instruction', fill=LABEL_FILL)
        merge(ws, f'G{row}:P{row + 2}', card.design_note or '')
        return row + 4

    def _section_footer(self, ws, card, figures, row):
        merge(ws, f'A{row}:P{row}', self.footer_text, border=False)
        return row + 1

    @staticmethod
    def _lines(card):
        return [('DIAMOND', line) for line in card.diamond_lines.all()] + [('COLORSTONE', line) for line in card.colorstone_lines.all()]

    def _image(self, ws, path, anchor, size):
        try:
            picture = PILImage.open(path)
            picture.thumbnail(size)
            buffer = BytesIO()
            picture.save(buffer, format='PNG')
            buffer.seek(0)
            self._buffers.append(buffer)
            ws.add_image(XLImage(buffer), anchor)
        except Exception:
            pass

    def _apply_outer_border(self, ws, last_row):
        """Draws one single thin border around the whole data block (A1:P{last_row})
        for the sheet, on top of whatever internal borders each table already has."""
        def edged(cell, **sides):
            b = cell.border
            cell.border = Border(
                left=sides.get('left', b.left),
                right=sides.get('right', b.right),
                top=sides.get('top', b.top),
                bottom=sides.get('bottom', b.bottom),
            )

        for col in range(1, LAST_COL + 1):
            edged(ws.cell(row=1, column=col), top=THIN)
            edged(ws.cell(row=last_row, column=col), bottom=THIN)
        for r in range(1, last_row + 1):
            edged(ws.cell(row=r, column=1), left=THIN)
            edged(ws.cell(row=r, column=LAST_COL), right=THIN)

    def _setup_print(self, ws, last_row):
        """Auto-fit the sheet's data onto a single printed page."""
        ws.print_area = f'A1:{get_column_letter(LAST_COL)}{last_row}'
        ws.page_setup.orientation = 'landscape'
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 1
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_options.horizontalCentered = True
        ws.page_margins.left = ws.page_margins.right = 0.3
        ws.page_margins.top = ws.page_margins.bottom = 0.4

    def _autofit_columns(self, ws):
        merged_starts = {
            (rng.min_row, rng.min_col)
            for rng in ws.merged_cells.ranges
            if rng.max_col > rng.min_col
        }
        widths = {}
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell, MergedCell) or cell.value is None:
                    continue
                if (cell.row, cell.column) in merged_starts:
                    continue
                length = len(str(cell.value))
                col = cell.column_letter
                widths[col] = max(widths.get(col, 0), length)
        for col in range(1, LAST_COL + 1):
            letter = get_column_letter(col)
            length = widths.get(letter, 0)
            # Fit tightly to the actual content - no extra padding added on top.
            ws.column_dimensions[letter].width = min(max(length, MIN_COL_WIDTH), MAX_COL_WIDTH)

    def _unique_title(self, card, used):
        base = self.sheet_title(card) if self.sheet_title else card.cost_card_no
        base = re.sub(r'[\[\]:*?/\\]', '-', str(base)).strip()[:31] or 'Sheet'
        title, count = base, 1
        while title.lower() in used:
            count += 1
            suffix = f'-{count}'
            title = base[:31 - len(suffix)] + suffix
        used.add(title.lower())
        return title