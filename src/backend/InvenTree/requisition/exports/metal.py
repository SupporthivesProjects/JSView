"""Metal order requisition workbook."""

from io import BytesIO

from openpyxl import Workbook

from .base import LEFT, fit_columns, landscape_fit, merge, num, put, up

HEADERS = ['Sr. No', 'Style No.', 'Qty', 'Net. Weight', 'KT', 'Gold(24KT)', 'Silver', 'Platinum']
NCOLS = len(HEADERS)
TOTAL_FMT = '0.000'


class MetalOrderSheetBuilder:
    """Builds the METAL ORDER REQUISITION workbook from a metal report dict.

    Usage:
        builder = MetalOrderSheetBuilder()
        data = builder.to_bytes(builder.build(report))
    """

    def build(self, report):
        workbook = Workbook()
        ws = workbook.active
        ws.title = 'Metal Order Requisition'

        merge(ws, 1, 1, NCOLS, 'METAL ORDER REQUISITION', bold=True, border=False, size=14)
        row = 3
        for po in report['data']:
            row = self._po_block(ws, po, row)

        if report['data']:
            self._grand_total(ws, report['grand_totals'], row)
        else:
            merge(ws, row, 1, NCOLS, 'No metal data for the selected PO(s)', border=False)

        fit_columns(ws, NCOLS)
        landscape_fit(ws)
        return workbook

    def to_bytes(self, workbook):
        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

    def _po_block(self, ws, po, row):
        merge(ws, row, 1, 4, f"PO NO: {po['po_no']}", bold=True, align=LEFT)
        merge(ws, row, 5, 4, f"Vendor: {po['vendor']}", bold=True, align=LEFT)
        row += 1

        for col, head in enumerate(HEADERS, start=1):
            put(ws, row, col, head, bold=True)
        row += 1

        for r in po['lines']:
            values = [
                r['sr_no'], up(r['style_no']), r['qty'], num(r['net_weight']), up(r['kt']),
                num(r['gold']), num(r['silver']), num(r['platinum']),
            ]
            for col, value in enumerate(values, start=1):
                put(ws, row, col, value)
            row += 1

        t = po['totals']
        col = merge(ws, row, 1, 2, 'Total :', bold=True)
        for offset, (value, fmt) in enumerate([
            (t['qty'], None), (num(t['net_weight']), TOTAL_FMT), (None, None),
            (num(t['gold']), TOTAL_FMT), (num(t['silver']), TOTAL_FMT), (num(t['platinum']), TOTAL_FMT),
        ]):
            put(ws, row, col + offset, value, bold=True, fmt=fmt)

        return row + 2

    def _grand_total(self, ws, g, row):
        col = merge(ws, row, 1, 2, 'Total', bold=True)
        for offset, head in enumerate(['Qty', 'Net. Weight', '', 'Gold(24KT)', 'Silver', 'Platinum']):
            put(ws, row, col + offset, head, bold=True)

        row += 1
        col = merge(ws, row, 1, 2, None)
        for offset, (value, fmt) in enumerate([
            (g['qty'], None), (num(g['net_weight']), TOTAL_FMT), (None, None),
            (num(g['gold']), TOTAL_FMT), (num(g['silver']), TOTAL_FMT), (num(g['platinum']), TOTAL_FMT),
        ]):
            put(ws, row, col + offset, value, bold=True, fmt=fmt)