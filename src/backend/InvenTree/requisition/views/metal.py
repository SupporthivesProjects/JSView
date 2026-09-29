"""Metal requisition API view."""

from decimal import Decimal

from rest_framework.response import Response
from rest_framework.views import APIView

from requisition.permissions import RequisitionPermission

from .utils import get_po_lines, group_by_po, parse_po_ids

METALS = ('gold', 'silver', 'platinum')


def _empty_totals():
    return {'qty': 0, 'total_weight': Decimal('0'), **{m: Decimal('0') for m in METALS}}


class MetalOrderRequisitionView(APIView):
    """Read-only metal requirement (Gold/Silver/Platinum) for selected PO(s)."""

    permission_classes = [RequisitionPermission]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        po_ids = parse_po_ids(request)
        if not po_ids:
            return Response({'detail': 'At least one po is required.'}, status=400)

        grouped = group_by_po(get_po_lines(po_ids), po_ids)

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