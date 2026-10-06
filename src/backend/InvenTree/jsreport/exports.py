import re
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, OneCellAnchor
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.units import pixels_to_EMU
from PIL import Image as PILImage
from rest_framework import serializers as drf_serializers
from rest_framework.response import Response

from common.models import DataOutput
from common.serializers import DataOutputSerializer
from InvenTree.helpers import str2bool

MIN_WIDTH = 8
MAX_WIDTH = 40

IMAGE_SIZE = (100, 100)  # max picture size in pixels, aspect ratio is kept
IMAGE_LABEL = "image"  # columns with this label are exported as pictures
IMAGE_PAD = 8  # extra pixels added to the row height around the picture

THIN_SIDE = Side(style="thin")
DATA_BORDER = Border(
    left=THIN_SIDE,
    right=THIN_SIDE,
    top=THIN_SIDE,
    bottom=THIN_SIDE,
)
MIDDLE = Alignment(vertical="center")


def image_file(value):
    """Return the local media file for an image url / path, or None."""
    if not value:
        return None

    text = str(value)
    path = urlparse(text).path if text.startswith(("http://", "https://")) else text

    media_url = settings.MEDIA_URL or "/media/"
    if path.startswith(media_url):
        path = path[len(media_url):]

    root = Path(settings.MEDIA_ROOT).resolve()
    candidate = (root / path.lstrip("/")).resolve()

    if root in candidate.parents and candidate.is_file():
        return candidate

    return None


class SimpleSheetBuilder:
    def __init__(self, title="Report"):
        self.title = title
        self._buffers = []

    def build(self, headers, rows, meta=None, image_cols=None):
        return self.build_multi(headers, [(self.title, rows)], meta=meta, image_cols=image_cols)

    def build_multi(self, headers, sheets, meta=None, image_cols=None):
        workbook = Workbook()
        workbook.remove(workbook.active)

        for title, rows in sheets or [(self.title, [])]:
            sheet = workbook.create_sheet(self._safe_title(title))
            self._fill(sheet, headers, rows, meta, image_cols or set())

        return workbook

    def to_bytes(self, workbook):
        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

    @staticmethod
    def _safe_title(title):
        return re.sub(r"[\[\]:*?/\\]", "-", str(title)).strip()[:31] or "Sheet"

    def _fill(self, ws, headers, rows, meta, image_cols):
        row = 1

        if meta:
            col = 1
            for label, value in meta:
                ws.cell(row=row, column=col, value=label).font = Font(bold=True)
                ws.cell(row=row, column=col + 1, value=value)
                col += 2
            row += 1

        ncols = len(headers)

        for col, head in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col, value=head)
            cell.font = Font(bold=True)
            cell.border = DATA_BORDER

        cell_width = self._image_col_width() * 7 + 5  # characters -> pixels

        for values in rows:
            row += 1
            pictures = []

            for col in range(1, ncols + 1):
                value = values[col - 1] if col <= len(values) else None
                cell = ws.cell(row=row, column=col)
                cell.border = DATA_BORDER

                if col in image_cols:
                    picture = self._load_image(value)
                    if picture:
                        pictures.append((col, picture))
                else:
                    cell.value = value

            if pictures:
                height = max(picture[1].size[1] for _, picture in pictures)
                row_height = height + IMAGE_PAD
                ws.row_dimensions[row].height = row_height * 0.75  # pixels -> points

                for col in range(1, ncols + 1):
                    ws.cell(row=row, column=col).alignment = MIDDLE

                for col, (image, picture) in pictures:
                    self._place_image(ws, image, picture, col, row, cell_width, row_height)

        self._fit_columns(ws, ncols, image_cols)

    @staticmethod
    def _image_col_width():
        return IMAGE_SIZE[0] / 7 + 2  # pixels -> characters

    def _load_image(self, value):
        """Return (excel image, resized picture) for a url / path, or None."""
        path = image_file(value)

        if path is None:
            return None

        try:
            picture = PILImage.open(path)
            picture.thumbnail(IMAGE_SIZE)

            if picture.mode not in ("RGB", "RGBA"):
                picture = picture.convert("RGB")

            buffer = BytesIO()
            picture.save(buffer, format="PNG")
            buffer.seek(0)
            self._buffers.append(buffer)

            return XLImage(buffer), picture
        except Exception:
            return None

    @staticmethod
    def _place_image(ws, image, picture, col, row, cell_width, row_height):
        """Anchor the picture in the middle of the cell, both ways."""
        width, height = picture.size
        marker = AnchorMarker(
            col=col - 1,
            row=row - 1,
            colOff=pixels_to_EMU(max(0, (cell_width - width) / 2)),
            rowOff=pixels_to_EMU(max(0, (row_height - height) / 2)),
        )
        image.anchor = OneCellAnchor(
            _from=marker,
            ext=XDRPositiveSize2D(pixels_to_EMU(width), pixels_to_EMU(height)),
        )
        ws.add_image(image)

    @staticmethod
    def _fit_columns(ws, ncols, image_cols=()):
        widths = {}

        for row in ws.iter_rows(max_col=ncols):
            for cell in row:
                if cell.value is not None:
                    length = len(str(cell.value))
                    widths[cell.column] = max(widths.get(cell.column, 0), length)

        for col in range(1, ncols + 1):
            if col in image_cols:
                width = SimpleSheetBuilder._image_col_width()
            else:
                width = min(max(widths.get(col, 0) + 2, MIN_WIDTH), MAX_WIDTH)
            ws.column_dimensions[get_column_letter(col)].width = width


class JSReportExportMixin:
    export_name = "Report"
    export_plugin = "jsreport"
    export_serial = False
    export_image_fields = None  # field names to export as pictures; None = label "Image"

    def get_export_meta(self, queryset):
        return []

    def get_export_sheet_title(self, instance):
        return None

    def list(self, request, *args, **kwargs):
        params = request.query_params

        if str2bool(params.get("export")) or params.get("export_format"):
            return self.export_response(request)

        return super().list(request, *args, **kwargs)

    def export_response(self, request):
        export_format = request.query_params.get("export_format") or "xlsx"

        if export_format.lower() != "xlsx":
            return Response({"detail": "Only xlsx export is supported."}, status=400)

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        fields = serializer.child.fields
        items = serializer.data
        instances = list(queryset)

        names = list(fields.keys())
        headers = [fields[name].label or name for name in names]
        rows = [
            [self._cell(fields[name], item.get(name)) for name in names]
            for item in items
        ]

        image_cols = self._image_cols(names, headers)
        sheets = self._split_sheets(instances, rows)

        if self.export_serial:
            headers.insert(0, "#")
            image_cols = {col + 1 for col in image_cols}
            sheets = [
                (title, [[number] + row for number, row in enumerate(sheet_rows, start=1)])
                for title, sheet_rows in sheets
            ]

        builder = SimpleSheetBuilder(self.export_name.replace("_", " "))
        content = builder.to_bytes(
            builder.build_multi(
                headers,
                sheets,
                meta=self.get_export_meta(queryset),
                image_cols=image_cols,
            )
        )

        output = DataOutput.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total=len(rows),
            progress=100,
            complete=True,
            output_type=DataOutput.DataOutputTypes.EXPORT,
            plugin=self.export_plugin,
        )

        timestamp = timezone.now().strftime("%Y_%m_%d_%H_%M")
        output.output.save(
            f"{self.export_name}_{timestamp}.xlsx",
            ContentFile(content),
            save=True,
        )

        return Response(DataOutputSerializer(output).data, status=200)

    def _image_cols(self, names, headers):
        """1-based column numbers that hold pictures."""
        if self.export_image_fields is not None:
            return {names.index(n) + 1 for n in self.export_image_fields if n in names}

        return {
            col
            for col, head in enumerate(headers, start=1)
            if str(head).strip().lower() == IMAGE_LABEL
        }

    def _split_sheets(self, instances, rows):
        titles = [self.get_export_sheet_title(instance) for instance in instances]

        if not any(titles):
            return [(self.export_name.replace("_", " "), rows)]

        grouped = {}
        for title, row in zip(titles, rows):
            grouped.setdefault(title or "No Vendor", []).append(row)

        ordered = sorted(grouped, key=lambda t: t.casefold().replace(" ", ""))

        return [
            (f"{number}-{title}", grouped[title])
            for number, title in enumerate(ordered, start=1)
        ]

    @staticmethod
    def _cell(field, value):
        if value is None:
            return None
        if isinstance(field, drf_serializers.DecimalField):
            return float(value)
        return value