import re
from io import BytesIO

from django.core.files.base import ContentFile
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Border, Font, Side
from openpyxl.utils import get_column_letter
from rest_framework import serializers as drf_serializers
from rest_framework.response import Response

from common.models import DataOutput
from common.serializers import DataOutputSerializer
from InvenTree.helpers import str2bool

MIN_WIDTH = 8
MAX_WIDTH = 40

THIN_SIDE = Side(style="thin")
DATA_BORDER = Border(
    left=THIN_SIDE,
    right=THIN_SIDE,
    top=THIN_SIDE,
    bottom=THIN_SIDE,
)


class SimpleSheetBuilder:
    def __init__(self, title="Report"):
        self.title = title

    def build(self, headers, rows, meta=None):
        return self.build_multi(headers, [(self.title, rows)], meta=meta)

    def build_multi(self, headers, sheets, meta=None):
        workbook = Workbook()
        workbook.remove(workbook.active)

        for title, rows in sheets or [(self.title, [])]:
            sheet = workbook.create_sheet(self._safe_title(title))
            self._fill(sheet, headers, rows, meta)

        return workbook

    def to_bytes(self, workbook):
        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

    @staticmethod
    def _safe_title(title):
        return re.sub(r"[\[\]:*?/\\]", "-", str(title)).strip()[:31] or "Sheet"

    def _fill(self, ws, headers, rows, meta):
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

        for values in rows:
            row += 1
            for col in range(1, ncols + 1):
                value = values[col - 1] if col <= len(values) else None
                ws.cell(row=row, column=col, value=value).border = DATA_BORDER

        self._fit_columns(ws, ncols)

    @staticmethod
    def _fit_columns(ws, ncols):
        widths = {}

        for row in ws.iter_rows(max_col=ncols):
            for cell in row:
                if cell.value is not None:
                    length = len(str(cell.value))
                    widths[cell.column] = max(widths.get(cell.column, 0), length)

        for col in range(1, ncols + 1):
            width = min(max(widths.get(col, 0) + 2, MIN_WIDTH), MAX_WIDTH)
            ws.column_dimensions[get_column_letter(col)].width = width


class JSReportExportMixin:
    export_name = "Report"
    export_plugin = "jsreport"
    export_serial = False

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

        sheets = self._split_sheets(instances, rows)

        if self.export_serial:
            headers.insert(0, "#")
            sheets = [
                (title, [[number] + row for number, row in enumerate(sheet_rows, start=1)])
                for title, sheet_rows in sheets
            ]

        builder = SimpleSheetBuilder(self.export_name.replace("_", " "))
        content = builder.to_bytes(
            builder.build_multi(headers, sheets, meta=self.get_export_meta(queryset))
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