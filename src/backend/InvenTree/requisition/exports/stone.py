"""Stone order list workbook (summary and per-PO details)."""

from io import BytesIO
from math import ceil

from openpyxl import Workbook

from .base import LEFT, fit_columns, fmt_date, landscape_fit, merge, num, put, up

SUMMARY_HEADERS = [
    '#', 'Stone', 'Shape', 'Cut', 'Color', 'Quality', 'MM Size', 'Sieve Size', 'Pointer', 'Pcs', 'Cts.',
]
DETAIL_HEADERS = [
    'Sr. No', 'Style NO.', 'Category', 'Qty', 'Setting', 'Stone', 'Shape', 'Cut', 'Colour',
    'Quality', 'MM Size', 'Sieve Size', 'Ptr', 'Pcs', 'cts', 'Total Pcs', 'Total cts',
]
DETAIL_COLS = len(DETAIL_HEADERS)
TOTAL_FMT = '0.00'
POINTER_FMT = '0.0000'


class StoneOrderSheetBuilder:
    """Builds the '<STONE> ORDER LIST' workbook for the selected view type.

    Usage:
        builder = StoneOrderSheetBuilder()
        data = builder.to_bytes(builder.build(report))
    """

    def build(self, report):
        workbook = Workbook()
        ws = workbook.active
        ws.title = 'Stone Order List'
        title = f"{report.get('stone_type', 'STONE')} ORDER LIST"

        if report['view_type'] == 'summary':
            self._summary(ws, report, title)
            ncols = len(SUMMARY_HEADERS)
        else:
            self._details(ws, report, title)
            ncols = DETAIL_COLS

        fit_columns(ws, ncols)
        landscape_fit(ws)
        return workbook

    def to_bytes(self, workbook):
        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

    def _summary(self, ws, report, title):
        ncols = len(SUMMARY_HEADERS)
        merge(ws, 1, 1, ncols, title, bold=True, border=False, size=14)

        po_text = 'P.O#: ' + ', '.join(report['po_nos'])
        merge(ws, 2, 1, ncols, po_text, border=False, align=LEFT)
        ws.row_dimensions[2].height = 16 * max(1, ceil(len(po_text) / 90))

        for col, head in enumerate(SUMMARY_HEADERS, start=1):
            put(ws, 3, col, head, bold=True)

        row = 4
        for r in report['data']:
            values = [
                r['sr_no'], up(r['stone']), up(r['shape']), up(r['cut']), up(r['colour']), up(r['quality']),
                up(r['mm_size']), up(r['sieve_size']), num(r['pointer']), r['pcs'], num(r['cts']),
            ]
            for col, value in enumerate(values, start=1):
                put(ws, row, col, value, fmt=POINTER_FMT if col == 9 else None)
            row += 1

        col = merge(ws, row, 1, 9, 'Total', bold=True)
        put(ws, row, col, report['totals']['pcs'], bold=True)
        put(ws, row, col + 1, num(report['totals']['cts']), bold=True, fmt=TOTAL_FMT)

    def _details(self, ws, report, title):
        merge(ws, 1, 1, DETAIL_COLS, title, bold=True, border=False, size=14)
        row = 3
        for po in report['data']:
            row = self._po_block(ws, po, row)

        if not report['data']:
            merge(ws, row, 1, DETAIL_COLS, 'No stone data for the selected PO(s)', border=False)

    @staticmethod
    def _pairs(ws, row, pairs):
        col = 1
        for label, value, span in pairs:
            col = merge(ws, row, col, 1, label, bold=True)
            col = merge(ws, row, col, span, value, align=LEFT)

    def _po_block(self, ws, po, row):
        rest = DETAIL_COLS - 14
        self._pairs(ws, row, [
            ('PO NO', po['po_no'], 2), ('Customer', po['customer'], 4),
            ('Vendor', po['vendor'], 4), ('A/c Exe', po['ac_exe'], rest),
        ])
        self._pairs(ws, row + 1, [
            ('PO Date', fmt_date(po['po_date']), 2), ('Stone Ship Date', fmt_date(po['stone_ship_date']), 4),
            ('Prepared', po['prepared'], 4), ('Category', po['category'] or '', rest),
        ])
        remarks = po['remarks'] or ''
        self._pairs(ws, row + 2, [
            ('Due Date', fmt_date(po['due_date']), 2), ('Remarks', remarks, DETAIL_COLS - 4),
        ])
        ws.row_dimensions[row + 2].height = 16 * max(1, remarks.count('\n') + 1)

        row += 4
        for col, head in enumerate(DETAIL_HEADERS, start=1):
            put(ws, row, col, head, bold=True)
        row += 1

        previous = None
        for r in po['lines']:
            first = r['sr_no'] != previous
            previous = r['sr_no']
            values = [
                r['sr_no'] if first else None,
                up(r['style_no']) if first else None,
                up(r['category']) if first else None,
                r['po_qty'] if first else None,
                up(r['setting']), up(r['stone']), up(r['shape']), up(r['cut']), up(r['colour']), up(r['quality']),
                up(r['mm_size']), up(r['sieve_size']), num(r['pointer']), r['pcs'], num(r['cts']),
                r['total_pcs'], num(r['total_cts']),
            ]
            for col, value in enumerate(values, start=1):
                put(ws, row, col, value)
            row += 1

        t = po['totals']
        col = merge(ws, row, 1, 3, 'Total :', bold=True)
        put(ws, row, col, t['qty'], bold=True)
        col = merge(ws, row, col + 1, 9, 'Total :', bold=True)
        for offset, (value, fmt) in enumerate([
            (t['pcs'], None), (num(t['cts']), TOTAL_FMT), (t['total_pcs'], None), (num(t['total_cts']), TOTAL_FMT),
        ]):
            put(ws, row, col + offset, value, bold=True, fmt=fmt)

        return row + 2