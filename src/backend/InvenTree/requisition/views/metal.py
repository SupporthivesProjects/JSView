"""Metal requisition API view (JSON + xlsx export)."""

import re
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation

from django.core.files.base import ContentFile

from rest_framework.response import Response
from rest_framework.views import APIView

from common.models import DataOutput
from common.serializers import DataOutputSerializer
from InvenTree.helpers import str2bool
from requisition.exports.metal import MetalOrderSheetBuilder
from requisition.permissions import RequisitionPermission

from .utils import get_po_lines, group_by_po, parse_po_ids

METALS = ('gold', 'silver', 'platinum')
WEIGHT_FIELD = 'net_weight'  
ZERO = Decimal('0')
THREE_DP = Decimal('0.001')


def _empty_totals():
    return {'qty': 0, 'total_weight': Decimal('0'), **{m: Decimal('0') for m in METALS}}


def _name(value):
    return '' if value is None else str(getattr(value, 'name', value))


def _metal_kind(cc):
    purity = cc.metal_purity
    metal_type = getattr(purity, 'metal_type', None) if purity else None
    text = f'{_name(metal_type)} {_name(purity)}'.lower()
    return next((m for m in METALS if m in text), None)


def _karat(cc):
    for source in (cc.karat, _name(cc.metal_purity)):
        match = re.search(r'\d+(?:\.\d+)?', '' if source is None else str(source))
        if match:
            try:
                value = Decimal(match.group())
            except InvalidOperation:
                continue
            if value > 0:
                return value
    return None


class MetalOrderRequisitionView(APIView):
    """Read-only metal requirement (Gold/Silver/Platinum) for selected PO(s).

    Add ?export=true (or export_format=xlsx) to get the Excel file as a DataOutput
    record instead of JSON.
    """

    permission_classes = [RequisitionPermission]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        po_ids = parse_po_ids(request)
        if not po_ids:
            return Response({'detail': 'At least one po is required.'}, status=400)

        grouped = group_by_po(get_po_lines(po_ids), po_ids)

        params = request.query_params
        if str2bool(params.get('export')) or params.get('export_format'):
            return self._export(request, grouped)

        result = []
        grand = _empty_totals()

        for po_id, po_lines in grouped.items():
            if not po_lines:
                result.append({
                    'po_id': po_id,
                    'po_no': None,
                    'vendor': None,
                    'lines': [],
                    'totals': _empty_totals(),
                })
                continue

            totals = _empty_totals()
            rows = []

            for idx, po_line in enumerate(po_lines, start=1):
                cc = po_line.costcardid
                qty = po_line.qty or 0
                net_weight = cc.metal_grams or Decimal('0')
                total_weight = net_weight * qty
                metal_type = (
                    cc.metal_purity.metal_type.name
                    if cc.metal_purity and cc.metal_purity.metal_type
                    else None
                )

                metal_values = {
                    m: total_weight if metal_type and metal_type.lower() == m else Decimal('0')
                    for m in METALS
                }

                rows.append({
                    'sr_no': idx,
                    'style_no': cc.our_style_no,
                    'qty': qty,
                    'net_weight': net_weight,
                    'total_weight': total_weight,
                    'kt': cc.karat,
                    **metal_values,
                })

                totals['qty'] += qty
                totals['total_weight'] += total_weight
                for m in METALS:
                    totals[m] += metal_values[m]

            po = po_lines[0].poid
            vendor = po_lines[0].costcardid.vendor

            result.append({
                'po_id': po.pk,
                'po_no': po.pono,
                'vendor': vendor.name if vendor else None,
                'lines': rows,
                'totals': totals,
            })

            for key, value in totals.items():
                grand[key] += value

        return Response({'po_ids': po_ids, 'data': result, 'grand_totals': grand})

    def _export(self, request, grouped):
        report = self._export_report(grouped)

        builder = MetalOrderSheetBuilder()
        content = builder.to_bytes(builder.build(report))

        user = request.user if request.user.is_authenticated else None
        output = DataOutput.objects.create(
            user=user,
            total=sum(len(po['lines']) for po in report['data']),
            progress=100,
            complete=True,
            output_type=DataOutput.DataOutputTypes.EXPORT,
            plugin='requisition-metal-order',
        )
        output.output.save('MetalOrderRequisition.xlsx', ContentFile(content), save=True)

        return Response(DataOutputSerializer(output).data, status=200)

    @staticmethod
    def _export_report(grouped):
        """Sheet figures: Net. Weight is per-piece weight x qty; Gold is shown as 24KT
        (net x KT / 24, rounded to 3 decimals per line, ties to even); Silver / Platinum are the net weight.
        A metal column stays blank when the PO has none of that metal."""
        data = []
        grand = {'qty': 0, 'net_weight': ZERO, **{m: None for m in METALS}}

        for po_lines in grouped.values():
            if not po_lines:
                continue

            rows = []
            totals = {'qty': 0, 'net_weight': ZERO, **{m: None for m in METALS}}

            for sr_no, po_line in enumerate(po_lines, start=1):
                cc = po_line.costcardid
                qty = po_line.qty or 0
                net_weight = (getattr(cc, WEIGHT_FIELD, None) or ZERO) * qty
                kind = _metal_kind(cc)
                karat = _karat(cc)

                values = {m: None for m in METALS}
                if kind == 'gold':
                    pure = net_weight * karat / 24 if karat else net_weight
                    values['gold'] = pure.quantize(THREE_DP, rounding=ROUND_HALF_EVEN)
                elif kind:
                    values[kind] = net_weight

                rows.append({
                    'sr_no': sr_no,
                    'style_no': cc.our_style_no,
                    'qty': qty,
                    'net_weight': net_weight,
                    'kt': cc.karat,
                    **values,
                })

                totals['qty'] += qty
                totals['net_weight'] += net_weight
                for m, value in values.items():
                    if value is not None:
                        totals[m] = (totals[m] or ZERO) + value

            po = po_lines[0].poid
            first = po_lines[0].costcardid
            vendor = getattr(po, 'vendorid', None) or first.vendor

            data.append({
                'po_no': po.pono,
                'vendor': _name(vendor),
                'lines': rows,
                'totals': totals,
            })

            grand['qty'] += totals['qty']
            grand['net_weight'] += totals['net_weight']
            for m in METALS:
                if totals[m] is not None:
                    grand[m] = (grand[m] or ZERO) + totals[m]

        return {'data': data, 'grand_totals': grand}