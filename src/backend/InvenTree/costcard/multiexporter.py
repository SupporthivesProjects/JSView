"""Reusable openpyxl builder for the cost card presentation workbook.

One sheet per cost card, named after the cost card number, all inside a
single workbook. Each sheet shows the same flat row/columns as the
picture-presentation export (JS Style No., Vendor Style No., KT, DIA CTS.,
QUALITY, COL CTS., COST $, COMMENTS, Duty %, Margin %) plus an embedded
Picture in column A.

Nothing here touches the database: cards are only read, never saved.

Usage:
    builder = CostCardSheetBuilder(overrides={'duty_pct': '100'})
    data = builder.to_bytes(builder.build(cards))
"""

import re
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path

from django.conf import settings

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.drawing.image import Image as XLImage
from PIL import Image as PILImage

THIN = Side(style='thin')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
MONEY = '0.00'

HEADERS = [
    'Picture', 'JS Style No.', 'Vendor Style No.', 'KT', 'DIA CTS.', 'QUALITY',
    'COL CTS.', 'COST $', 'COMMENTS', 'Duty %', 'Margin %',
]
IMAGE_SIZE = (100, 100)
ROW_HEIGHT = 78


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


def put(ws, ref, value, bold=False, border=True, fmt=None, size=11):
    cell = ws[ref]
    cell.value = value
    cell.font = Font(bold=bold, size=size)
    cell.alignment = CENTER
    if border:
        cell.border = BORDER
    if fmt:
        cell.number_format = fmt
    return cell


class CostCardSheetBuilder:
    """Builds one sheet per cost card, sheet name = cost card number.
    Each sheet's single data row mirrors the picture-presentation export.
    """

    def __init__(self, overrides=None, modified_by='', sheet_title=None):
        self.overrides = {key: dec(value) for key, value in (overrides or {}).items()}
        self.modified_by = modified_by
        self.sheet_title = sheet_title
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
        figures = self.figures(card)

        for col, title in enumerate(HEADERS, start=1):
            put(ws, ws.cell(row=1, column=col).coordinate, title, bold=True)

        values = [
            None,  # Picture column handled separately below
            card.our_style_no,
            card.vendor_style_no or '',
            name_of(card.metal_purity) if card.metal_purity else (card.karat or ''),
            num(card.dia_cts),
            self._quality(card),
            num(card.col_cts),
            num(figures['cost']),
            card.remarks or '',
            num(figures['duty_pct']),
            num(figures['margin_pct']),
        ]
        for col, value in enumerate(values, start=1):
            fmt = MONEY if col in (5, 7, 8, 10, 11) else None
            put(ws, ws.cell(row=2, column=col).coordinate, value, fmt=fmt)

        ws.row_dimensions[2].height = ROW_HEIGHT
        ws.column_dimensions['A'].width = 18
        for letter in 'BCDEFGHIJK':
            ws.column_dimensions[letter].width = 18

        if card.front_view:
            self._image(ws, Path(settings.MEDIA_ROOT) / card.front_view.name, 'A2')

    def figures(self, card):
        overrides = self.overrides
        purity = card.metal_purity
        text = f"{name_of(getattr(purity, 'metal_type', None))} {name_of(purity)}".lower()
        price = overrides.get('silver_troy_ounce' if 'silver' in text else 'gold_troy_ounce')
        ratio = price / card.troy_ounce_price if price is not None and card.troy_ounce_price else None

        fob = card.fob
        if ratio is not None:
            fob += (card.metal_amount + card.metal_loss_amount) * (ratio - 1)

        duty_pct = overrides['duty_pct'] if overrides.get('duty_pct') is not None else card.duty_pct
        margin_pct = overrides['margin_pct'] if overrides.get('margin_pct') is not None else card.margin_pct

        if any(value is not None for value in overrides.values()):
            duty_amt = fob * duty_pct / 100
            margin_amt = (fob + duty_amt) * margin_pct / 100
            cost = (fob + duty_amt + margin_amt).quantize(Decimal('0.01'))
        else:
            cost = card.final_amount

        return {
            'duty_pct': duty_pct,
            'margin_pct': margin_pct,
            'cost': cost,
        }

    @staticmethod
    def _quality(card):
        line = card.diamond_lines.first()
        return line.stone.name if line and line.stone else ''

    def _image(self, ws, path, anchor):
        try:
            picture = PILImage.open(path)
            picture.thumbnail(IMAGE_SIZE)
            buffer = BytesIO()
            picture.save(buffer, format='PNG')
            buffer.seek(0)
            self._buffers.append(buffer)
            ws.add_image(XLImage(buffer), anchor)
        except Exception:
            pass

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