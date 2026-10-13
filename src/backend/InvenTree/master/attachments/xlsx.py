from io import BytesIO
from openpyxl import Workbook
from .base import BaseAttachment, register


class XlsxAttachment(BaseAttachment):
    mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    extension = 'xlsx'
    sheet_title = 'Sheet1'
    headers = ()

    def rows(self, ctx):
        raise NotImplementedError

    def render(self, ctx):
        wb = Workbook()
        ws = wb.active
        ws.title = self.sheet_title
        ws.append(list(self.headers))
        for row in self.rows(ctx):
            ws.append(row)
        buf = BytesIO()
        wb.save(buf)
        return buf.getvalue()


@register
class StoneDiamondXlsx(XlsxAttachment):
    key = 'stone_diamond_xlsx'
    sheet_title = 'Diamonds'
    headers = ('Shape', 'Size', 'Color', 'Clarity', 'Pcs', 'Weight')

    def rows(self, ctx):
        return [[d['shape'], d['size'], d['color'], d['clarity'], d['pcs'], d['weight']]
                for d in ctx['diamonds']]


@register
class StoneColorXlsx(XlsxAttachment):
    key = 'stone_color_xlsx'
    sheet_title = 'Color Stones'
    headers = ('Stone', 'Shape', 'Size', 'Colour', 'Quality', 'Pcs', 'Weight')

    def rows(self, ctx):
        return [[s['name'], s['shape'], s['size'], s['colour'], s['quality'], s['pcs'], s['weight']]
                for s in ctx['stones']]