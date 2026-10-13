from pathlib import Path

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
            raise RuntimeError(
                f'template {self.template_name} failed: {exc}'
            ) from exc

        static_root = getattr(settings, 'STATIC_ROOT', None)
        base_url = Path(static_root).resolve().as_uri() + '/' if static_root and Path(static_root).is_dir() else None

        try:
            return HTML(string=html, base_url=base_url).write_pdf()
        except Exception as exc:
            raise RuntimeError(
                f'PDF generation failed for {self.template_name}: {exc}'
            ) from exc