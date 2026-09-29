"""Stone requisition API view."""

import re
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal

from django.core.files.base import ContentFile

from rest_framework.response import Response
from rest_framework.views import APIView

from common.models import DataOutput
from common.serializers import DataOutputSerializer
from InvenTree.helpers import str2bool
from purchase_order.models import POCostCardLine
from requisition.exports.stone import StoneOrderSheetBuilder
from requisition.permissions import RequisitionPermission

from .utils import get_po_lines, group_by_po, parse_po_ids

SUMMARY_FIELDS = [
    'stone',
    'shape',
    'cut',
    'colour',
    'quality',
    'mm_size',
    'sieve_size',
    'pointer',
]
ZERO = Decimal('0')
FOUR_DP = Decimal('0.0001')


def _label(value):
    if value is None:
        return ''

    for attr in ('mm_size', 'name'):
        inner = getattr(value, attr, None)

        if inner:
            return str(inner)

    return str(value)


def _mm_sort(value):
    match = re.search(r'\d+(?:\.\d+)?', value)

    return (float(match.group()) if match else 0.0, value)


def _stone_totals(stone, qty):
    return (stone.pcs or 0) * qty, (stone.cts or ZERO) * qty


class StoneOrderListView(APIView):
    """Read-only stone requirement for selected PO(s).

    Add ?export=true to get the matching Excel file (summary or details,
    following view_type) as a DataOutput record instead of JSON.
    """

    permission_classes = [RequisitionPermission]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        po_ids = parse_po_ids(request)

        if not po_ids:
            return Response(
                {'detail': 'At least one po is required.'},
                status=400,
            )

        params = request.query_params
        view_type = params.get('view_type', 'details')
        stone_type = params.get('stone_type', 'DIAMOND')
        stone_place = params.get('stone_place')
        show_rate = params.get('show_rate', 'no') == 'yes'

        po_lines = list(get_po_lines(po_ids))
        stones_by_card = self._stones_by_card(po_lines, stone_type, stone_place)
        grouped = group_by_po(po_lines, po_ids)

        if str2bool(params.get('export')):
            return self._export(
                request,
                grouped,
                stones_by_card,
                view_type,
                stone_type,
            )

        if view_type == 'summary':
            return Response(self._summary(grouped, stones_by_card, po_ids))

        return Response(
            self._details(grouped, stones_by_card, po_ids, show_rate)
        )

    @staticmethod
    def _stones_by_card(po_lines, stone_type, stone_place):
        stone_qs = POCostCardLine.objects.filter(
            po_costcard_id__in={pl.costcardid_id for pl in po_lines},
            etype=stone_type,
        ).order_by('pk')

        if stone_place:
            stone_qs = stone_qs.filter(stone_place=stone_place)

        stones_by_card = defaultdict(list)

        for stone in stone_qs:
            stones_by_card[stone.po_costcard_id].append(stone)

        return stones_by_card

    @staticmethod
    def _details(grouped, stones_by_card, po_ids, show_rate):
        result = []

        for po_lines in grouped.values():
            rows = []

            for po_line in po_lines:
                cc = po_line.costcardid
                qty = po_line.qty or 0

                for stone in stones_by_card.get(cc.pk, []):
                    total_pcs, total_cts = _stone_totals(stone, qty)

                    row = {
                        'sr_no': len(rows) + 1,
                        'style_no': cc.our_style_no,
                        'front_view': cc.front_view.url if cc.front_view else None,
                        'category': cc.sub_category.name if cc.sub_category else None,
                        'setting': stone.setting,
                        'stone': stone.stone,
                        'shape': stone.shape,
                        'cut': stone.cut,
                        'colour': stone.colour,
                        'quality': stone.quality,
                        'mm_size': stone.mm_size,
                        'sieve_size': stone.sieve_size,
                        'pointer': stone.pointer,
                        'pcs': stone.pcs,
                        'cts': stone.cts,
                        'po_qty': qty,
                        'total_pcs': total_pcs,
                        'total_cts': total_cts,
                    }

                    if show_rate:
                        row.update({'rate': stone.rate, 'amount': stone.amount})

                    rows.append(row)

            if not rows:
                continue

            po = po_lines[0].poid
            cc = po_lines[0].costcardid

            result.append({
                'po_id': po.pk,
                'po_no': po.pono,
                'po_date': po.podate,
                'due_date': po.ddate,
                'customer': cc.customer.name if cc.customer else None,
                'stone_ship_date': po.esdstone,
                'vendor': cc.vendor.name if cc.vendor else None,
                'prepared': po.prepby.get_full_name() if po.prepby else None,
                'ac_exe': po.acexeid.name if po.acexeid else None,
                'category': po.pocategory,
                'remarks': po.rem,
                'lines': rows,
                'totals': {
                    'pcs': sum(r['total_pcs'] for r in rows),
                    'cts': sum(r['total_cts'] for r in rows),
                },
            })

        return {'po_ids': po_ids, 'view_type': 'details', 'data': result}

    @staticmethod
    def _summary(grouped, stones_by_card, po_ids):
        buckets = {}

        for po_lines in grouped.values():
            for po_line in po_lines:
                qty = po_line.qty or 0

                for stone in stones_by_card.get(po_line.costcardid_id, []):
                    key = tuple(getattr(stone, field) for field in SUMMARY_FIELDS)
                    bucket = buckets.setdefault(
                        key,
                        {'total_pcs': 0, 'total_cts': ZERO},
                    )
                    total_pcs, total_cts = _stone_totals(stone, qty)
                    bucket['total_pcs'] += total_pcs
                    bucket['total_cts'] += total_cts

        def sort_key(key):
            return tuple('' if value is None else str(value) for value in key)

        rows = []

        for key in sorted(buckets, key=sort_key):
            rows.append({
                'sr_no': len(rows) + 1,
                **dict(zip(SUMMARY_FIELDS, key)),
                **buckets[key],
            })

        return {
            'po_ids': po_ids,
            'view_type': 'summary',
            'data': rows,
            'totals': {
                'pcs': sum(r['total_pcs'] for r in rows),
                'cts': sum(r['total_cts'] for r in rows),
            },
        }

    def _export(self, request, grouped, stones_by_card, view_type, stone_type):
        if view_type == 'summary':
            report = self._export_summary(grouped, stones_by_card)
            total = len(report['data'])
            file_name = 'StoneOrderSummary.xlsx'
        else:
            report = self._export_details(grouped, stones_by_card)
            total = sum(len(po['lines']) for po in report['data'])
            file_name = 'StoneOrderDetails.xlsx'

        report['stone_type'] = stone_type

        builder = StoneOrderSheetBuilder()
        content = builder.to_bytes(builder.build(report))

        user = request.user if request.user.is_authenticated else None

        output = DataOutput.objects.create(
            user=user,
            total=total,
            progress=100,
            complete=True,
            output_type=DataOutput.DataOutputTypes.EXPORT,
            plugin='requisition-stone-order',
        )

        output.output.save(file_name, ContentFile(content), save=True)

        return Response(DataOutputSerializer(output).data, status=200)

    @staticmethod
    def _export_details(grouped, stones_by_card):
        result = []

        for po_lines in grouped.values():
            rows = []
            qty_total = 0
            sr_no = 0

            for po_line in po_lines:
                cc = po_line.costcardid
                stones = stones_by_card.get(cc.pk, [])

                if not stones:
                    continue

                sr_no += 1
                qty = po_line.qty or 0
                qty_total += qty

                for stone in stones:
                    total_pcs, total_cts = _stone_totals(stone, qty)

                    rows.append({
                        'sr_no': sr_no,
                        'style_no': cc.our_style_no,
                        'category': _label(cc.sub_category),
                        'po_qty': qty,
                        'setting': _label(stone.setting),
                        'stone': _label(stone.stone),
                        'shape': _label(stone.shape),
                        'cut': _label(stone.cut),
                        'colour': _label(stone.colour),
                        'quality': _label(stone.quality),
                        'mm_size': _label(stone.mm_size),
                        'sieve_size': _label(stone.sieve_size),
                        'pointer': stone.pointer,
                        'pcs': stone.pcs or 0,
                        'cts': stone.cts or ZERO,
                        'total_pcs': total_pcs,
                        'total_cts': total_cts,
                    })

            if not rows:
                continue

            po = po_lines[0].poid
            cc = po_lines[0].costcardid
            customer = getattr(po, 'customerid', None) or cc.customer
            vendor = getattr(po, 'vendorid', None) or cc.vendor
            prepby = po.prepby

            result.append({
                'po_no': po.pono,
                'po_date': po.podate,
                'due_date': po.ddate,
                'stone_ship_date': po.esdstone,
                'customer': _label(customer),
                'vendor': _label(vendor),
                'prepared': (
                    (prepby.get_full_name() or prepby.get_username())
                    if prepby
                    else ''
                ),
                'ac_exe': _label(po.acexeid),
                'category': po.pocategory,
                'remarks': po.rem,
                'lines': rows,
                'totals': {
                    'qty': qty_total,
                    'pcs': sum(r['pcs'] for r in rows),
                    'cts': sum(r['cts'] for r in rows),
                    'total_pcs': sum(r['total_pcs'] for r in rows),
                    'total_cts': sum(r['total_cts'] for r in rows),
                },
            })

        return {'view_type': 'details', 'data': result}

    @staticmethod
    def _export_summary(grouped, stones_by_card):
        """Order list laid out like the reference sheet.

        Rows are grouped per PO and stone spec, so the same spec on two POs
        is listed once for each. Pointer is derived: total cts / total pcs
        to 4 decimals, blank when there are no pieces.
        """

        buckets = {}
        po_nos = []

        for po_index, po_lines in enumerate(grouped.values()):
            if po_lines:
                po_nos.append(po_lines[0].poid.pono)

            for po_line in po_lines:
                qty = po_line.qty or 0

                for stone in stones_by_card.get(po_line.costcardid_id, []):
                    key = (
                        po_index,
                        _label(stone.stone),
                        _label(stone.shape),
                        _label(stone.cut),
                        _label(stone.colour),
                        _label(stone.quality),
                        _label(stone.mm_size),
                        _label(stone.sieve_size),
                    )
                    bucket = buckets.setdefault(key, {'pcs': 0, 'cts': ZERO})
                    total_pcs, total_cts = _stone_totals(stone, qty)
                    bucket['pcs'] += total_pcs
                    bucket['cts'] += total_cts

        def sort_key(key):
            po_index, stone, shape, cut, colour, quality, mm_size, sieve_size = key

            return (
                stone,
                shape,
                cut,
                colour,
                quality,
                _mm_sort(mm_size),
                sieve_size,
                po_index,
            )

        rows = []

        for key in sorted(buckets, key=sort_key):
            _po_index, stone, shape, cut, colour, quality, mm_size, sieve_size = key
            pcs, cts = buckets[key]['pcs'], buckets[key]['cts']
            pointer = (
                (cts / Decimal(pcs)).quantize(FOUR_DP, rounding=ROUND_HALF_UP)
                if pcs
                else None
            )

            rows.append({
                'sr_no': len(rows) + 1,
                'stone': stone,
                'shape': shape,
                'cut': cut,
                'colour': colour,
                'quality': quality,
                'mm_size': mm_size,
                'sieve_size': sieve_size,
                'pointer': pointer,
                'pcs': pcs,
                'cts': cts,
            })

        return {
            'view_type': 'summary',
            'po_nos': po_nos,
            'data': rows,
            'totals': {
                'pcs': sum(r['pcs'] for r in rows),
                'cts': sum(r['cts'] for r in rows),
            },
        }