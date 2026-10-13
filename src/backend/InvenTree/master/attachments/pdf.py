from django.conf import settings
from django.template.loader import get_template
from weasyprint import HTML
from .base import BaseAttachment, register


class PdfAttachment(BaseAttachment):
    mimetype = 'application/pdf'
    extension = 'pdf'
    template_name = ''

    def render(self, ctx):
        try:
            html = get_template(self.template_name).render(ctx)
        except Exception as exc:
            raise RuntimeError(f'template {self.template_name} failed: {exc}') from exc

        return HTML(string=html, base_url=str(settings.STATIC_ROOT or '')).write_pdf()


@register
class PoVendorPdf(PdfAttachment):
    key = 'po_vendor_pdf'
    template_name = 'master/attachments/po_vendor.html'


@register
class PoVendorCostcardPdf(PdfAttachment):
    key = 'po_vendor_costcard_pdf'
    template_name = 'master/attachments/po_vendor_costcard.html'


@register
class PoSelfPdf(PdfAttachment):
    key = 'po_self_pdf'
    template_name = 'master/attachments/po_self.html'


@register
class PoSelfCostcardPdf(PdfAttachment):
    key = 'po_self_costcard_pdf'
    template_name = 'master/attachments/po_self_costcard.html'