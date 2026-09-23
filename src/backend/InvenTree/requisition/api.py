"""Provides a JSON API for the 'requisition' app."""

from decimal import Decimal

from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from django.urls import include, path

from data_exporter.mixins import DataExportViewMixin

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from purchase_order.models import POCostCard, POCostCardLine

from . import serializers as requisition_serializers
from .models import MetalSent


class RequisitionPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class MetalSentList(DataExportViewMixin, ListCreateAPI):
    queryset = MetalSent.objects.all()
    serializer_class = requisition_serializers.MetalSentSerializer
    pagination_class = RequisitionPagination
    # permission_classes = [RequisitionPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['purchase_order', 'active']
    search_fields = ['invoice_no', 'purchase_order__pono', 'triounce']
    ordering_fields = ['metal_sent_no', 'metal_sent_date', 'invoice_no', 'metal_gms', 'metal_amount']
    ordering = '-metal_sent_date'

    def perform_create(self, serializer):
        serializer.save(prepby=self.request.user)


class MetalSentDetail(RetrieveUpdateDestroyAPI):
    queryset = MetalSent.objects.all()
    serializer_class = requisition_serializers.MetalSentSerializer
    # permission_classes = [RequisitionPermission]


class StoneOrderListView(APIView):
    """Read-only aggregation of stone requirements for selected PO(s)."""

    # permission_classes = [RequisitionPermission]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        po_ids = request.query_params.getlist('po')
        view_type = request.query_params.get('view_type', 'details')
        stone_type = request.query_params.get('stone_type', 'DIAMOND')
        stone_place = request.query_params.get('stone_place')
        show_rate = request.query_params.get('show_rate', 'no') == 'yes'

        if not po_ids:
            return Response({'detail': 'At least one po is required.'}, status=400)

        lines = POCostCardLine.objects.filter(
            po_costcard__poid__pk__in=po_ids,
            etype=stone_type,
        ).select_related('po_costcard', 'po_costcard__poid', 'po_costcard__vendor', 'po_costcard__customer')

        if stone_place:
            lines = lines.filter(stone_place=stone_place)

        if view_type == 'summary':
            return Response(self._build_summary(lines, po_ids, show_rate))

        return Response(self._build_details(lines, po_ids, show_rate))

    def _build_details(self, lines, po_ids, show_rate):
        result = []
        for po_id in po_ids:
            po_lines = lines.filter(po_costcard__poid__pk=po_id)
            if not po_lines.exists():
                continue

            first = po_lines.first()
            po = first.po_costcard.poid
            cc = first.po_costcard

            rows = []
            for idx, line in enumerate(po_lines, start=1):
                row = {
                    'sr_no': idx,
                    'style_no': cc.our_style_no,
                    'category': cc.sub_category.name if cc.sub_category else None,
                    'setting': line.setting,
                    'stone': line.stone,
                    'shape': line.shape,
                    'cut': line.cut,
                    'colour': line.colour,
                    'quality': line.quality,
                    'mm_size': line.mm_size,
                    'sieve_size': line.sieve_size,
                    'pointer': line.pointer,
                    'pcs': line.pcs,
                    'cts': line.cts,
                    # 'total_pcs' / 'total_cts' need PO Line qty — pending
                    # clarification on POCostCard <-> PurchaseOrderLine link
                }
                if show_rate:
                    row.update({'rate': line.rate, 'amount': line.amount})
                rows.append(row)

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
                    'pcs': sum(r['pcs'] for r in rows),
                    'cts': sum(r['cts'] for r in rows),
                },
            })
        return {'po_ids': po_ids, 'view_type': 'details', 'data': result}

    def _build_summary(self, lines, po_ids, show_rate):
        group_fields = ['stone', 'shape', 'cut', 'colour', 'quality', 'mm_size', 'sieve_size', 'pointer']

        grouped = (
            lines
            .values(*group_fields)
            .annotate(
                total_pcs=Coalesce(Sum('pcs'), 0),
                total_cts=Coalesce(Sum('cts'), Decimal('0'), output_field=DecimalField()),
            )
            .order_by(*group_fields)
        )

        rows = [{'sr_no': i, **row} for i, row in enumerate(grouped, start=1)]

        return {
            'po_ids': po_ids,
            'view_type': 'summary',
            'data': rows,
            'totals': {
                'pcs': sum(r['total_pcs'] for r in rows),
                'cts': sum(r['total_cts'] for r in rows),
            },
        }


class MetalOrderRequisitionView(APIView):
    """Read-only metal requirement aggregation (Gold/Silver/Platinum) for selected PO(s)."""

    # permission_classes = [RequisitionPermission]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        po_ids = request.query_params.getlist('po')

        if not po_ids:
            return Response({'detail': 'At least one po is required.'}, status=400)

        costcards = POCostCard.objects.filter(
            poid__pk__in=po_ids,
        ).select_related('poid', 'vendor', 'metal_purity', 'metal_purity__metal_type')

        result = []
        grand_qty = 0
        grand_net_weight = Decimal('0')
        grand_gold = Decimal('0')
        grand_silver = Decimal('0')
        grand_platinum = Decimal('0')

        for po_id in po_ids:
            po_cards = costcards.filter(poid__pk=po_id)
            if not po_cards.exists():
                result.append({'po_id': po_id, 'po_no': None, 'vendor': None, 'lines': [], 'totals': {
                    'qty': 0, 'net_weight': Decimal('0'), 'gold': Decimal('0'),
                    'silver': Decimal('0'), 'platinum': Decimal('0'),
                }})
                continue

            po = po_cards.first().poid
            rows = []
            po_qty = 0
            po_net_weight = Decimal('0')
            po_gold = Decimal('0')
            po_silver = Decimal('0')
            po_platinum = Decimal('0')

            for idx, cc in enumerate(po_cards, start=1):
                po_line = po.lines.filter(styleno=cc.our_style_no).first()
                qty = po_line.qty if po_line else 0
                net_weight = cc.metal_grams or Decimal('0')
                metal_type_name = (
                    cc.metal_purity.metal_type.name if cc.metal_purity and cc.metal_purity.metal_type else None
                )

                gold = net_weight if metal_type_name == 'Gold' else Decimal('0')
                silver = net_weight if metal_type_name == 'Silver' else Decimal('0')
                platinum = net_weight if metal_type_name == 'Platinum' else Decimal('0')

                rows.append({
                    'sr_no': idx,
                    'style_no': cc.our_style_no,
                    'qty': qty,
                    'net_weight': net_weight,
                    'kt': cc.karat,
                    'gold': gold,
                    'silver': silver,
                    'platinum': platinum,
                })

                po_qty += qty
                po_net_weight += net_weight
                po_gold += gold
                po_silver += silver
                po_platinum += platinum

            result.append({
                'po_id': po.pk,
                'po_no': po.pono,
                'vendor': po_cards.first().vendor.name if po_cards.first().vendor else None,
                'lines': rows,
                'totals': {
                    'qty': po_qty,
                    'net_weight': po_net_weight,
                    'gold': po_gold,
                    'silver': po_silver,
                    'platinum': po_platinum,
                },
            })

            grand_qty += po_qty
            grand_net_weight += po_net_weight
            grand_gold += po_gold
            grand_silver += po_silver
            grand_platinum += po_platinum

        return Response({
            'po_ids': po_ids,
            'data': result,
            'grand_totals': {
                'qty': grand_qty,
                'net_weight': grand_net_weight,
                'gold': grand_gold,
                'silver': grand_silver,
                'platinum': grand_platinum,
            },
        })


requisition_api_urls = [
    path('metal-sent/', include([
        path('<int:pk>/', MetalSentDetail.as_view(), name='api-metal-sent-detail'),
        path('', MetalSentList.as_view(), name='api-metal-sent-list'),
    ])),
    path('stone/', StoneOrderListView.as_view(), name='api-stone'),
    path('metal/', MetalOrderRequisitionView.as_view(), name='api-metal'),
]