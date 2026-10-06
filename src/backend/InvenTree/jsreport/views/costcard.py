from decimal import Decimal

from django.db.models import Q

from rest_framework import serializers as drf_serializers

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from costcard.models import CostCard

from jsreport.exports import JSReportExportMixin
from jsreport.permissions import JSReportPermission
from jsreport.serializers import DATE_FMT
from jsreport.views.open_order import JSReportPagination


def _ids(value):
    return [int(v) for v in str(value or '').split(',') if v.strip().isdigit()]


class CostCardExportSerializer(drf_serializers.ModelSerializer):
    cost_card_no = drf_serializers.CharField(label='Cost Card No.')
    customer = drf_serializers.SerializerMethodField(label='Customer')
    vendor = drf_serializers.SerializerMethodField(label='Vendor')
    style = drf_serializers.CharField(source='our_style_no', label='Style')
    v_style = drf_serializers.SerializerMethodField(label='V.Style')
    category = drf_serializers.SerializerMethodField(label='Category')
    sub_category = drf_serializers.SerializerMethodField(label='Sub Category')
    date = drf_serializers.SerializerMethodField(label='Date')
    metal = drf_serializers.SerializerMethodField(label='Metal')
    tr_oz = drf_serializers.DecimalField(
        source='troy_ounce_price', max_digits=15, decimal_places=2, label='Tr.Oz'
    )
    kt = drf_serializers.IntegerField(source='karat', label='Kt')
    net_wt = drf_serializers.DecimalField(
        source='net_weight', max_digits=10, decimal_places=3, label='Net Wt.'
    )
    metal_loss_pct = drf_serializers.DecimalField(
        max_digits=6, decimal_places=2, label='Metal Loss %'
    )
    metal_amount = drf_serializers.DecimalField(
        max_digits=15, decimal_places=2, label='Metal Amount'
    )
    dia_pcs = drf_serializers.IntegerField(label='Dia. Pcs')
    dia_cts = drf_serializers.DecimalField(
        max_digits=10, decimal_places=4, label='Dia. Cts'
    )
    dia_amount = drf_serializers.DecimalField(
        max_digits=15, decimal_places=2, label='Dia. Amount'
    )
    col_pcs = drf_serializers.IntegerField(label='Col. Pcs')
    col_cts = drf_serializers.DecimalField(
        max_digits=10, decimal_places=4, label='Col. Cts'
    )
    col_amount = drf_serializers.DecimalField(
        max_digits=15, decimal_places=2, label='Col. Amount'
    )
    studding = drf_serializers.DecimalField(
        source='stone_amount', max_digits=15, decimal_places=2, label='Studding'
    )
    labour = drf_serializers.DecimalField(
        source='labour_amount', max_digits=15, decimal_places=2, label='Labour'
    )
    finding = drf_serializers.SerializerMethodField(label='Finding')
    finding_amount = drf_serializers.DecimalField(
        source='finding_price', max_digits=15, decimal_places=2, label='Finding Amount'
    )
    markup_pct = drf_serializers.DecimalField(
        source='vendor_markup_pct', max_digits=6, decimal_places=2, label='Markup%'
    )
    with_markup = drf_serializers.SerializerMethodField(label='With Markup%')
    fob = drf_serializers.DecimalField(
        max_digits=15, decimal_places=2, label='FOB'
    )
    duty_pct = drf_serializers.DecimalField(
        max_digits=6, decimal_places=2, label='Duty%'
    )
    with_duty = drf_serializers.SerializerMethodField(label='With Duty')
    margin_pct = drf_serializers.DecimalField(
        max_digits=6, decimal_places=2, label='Margin%'
    )
    final_amount = drf_serializers.DecimalField(
        max_digits=15, decimal_places=2, label='Final Amount'
    )

    class Meta:
        model = CostCard
        fields = [
            'cost_card_no',
            'customer',
            'vendor',
            'style',
            'v_style',
            'category',
            'sub_category',
            'date',
            'metal',
            'tr_oz',
            'kt',
            'net_wt',
            'metal_loss_pct',
            'metal_amount',
            'dia_pcs',
            'dia_cts',
            'dia_amount',
            'col_pcs',
            'col_cts',
            'col_amount',
            'studding',
            'labour',
            'finding',
            'finding_amount',
            'markup_pct',
            'with_markup',
            'fob',
            'duty_pct',
            'with_duty',
            'margin_pct',
            'final_amount',
        ]

    def get_customer(self, obj):
        return obj.customer.name if obj.customer else ''

    def get_vendor(self, obj):
        return obj.vendor.name if obj.vendor else ''

    def get_v_style(self, obj):
        return obj.vendor_style_no or ''

    def get_category(self, obj):
        return obj.category.name if obj.category else ''

    def get_sub_category(self, obj):
        return obj.sub_category.name if obj.sub_category else ''

    def get_date(self, obj):
        return obj.created_at.strftime(DATE_FMT) if obj.created_at else ''

    def get_metal(self, obj):
        return obj.metal_purity.name if obj.metal_purity else ''

    def get_finding(self, obj):
        return obj.finding_type.name if obj.finding_type else ''

    def get_with_markup(self, obj):
        return obj.fob if obj.vendor_markup_pct else None

    def get_with_duty(self, obj):
        return (obj.fob or Decimal('0')) + (obj.duty_amount or Decimal('0'))


class CostCardExportReportView(JSReportExportMixin, ListAPI):
    """Cost Card Export report.

    ?cost_card_no=&our_style_no=&vendor_style_no=
    &customer=<id>&vendor=<id>&category=<id>&sub_category=<id>&metal_purity=<id>
    """

    export_name = 'Cost_Card_Export'
    export_plugin = 'jsreport-costcard-export'

    queryset = CostCard.objects.all()
    serializer_class = CostCardExportSerializer
    pagination_class = JSReportPagination
    permission_classes = [JSReportPermission]

    filter_backends = SEARCH_ORDER_FILTER
    search_fields = [
        'cost_card_no',
        'our_style_no',
        'vendor_style_no',
    ]
    ordering_fields = [
        'cost_card_no',
        'our_style_no',
        'created_at',
        'final_amount',
    ]
    ordering = ['cost_card_no']

    def get_queryset(self):
        params = self.request.query_params

        queryset = CostCard.objects.select_related(
            'customer',
            'vendor',
            'category',
            'sub_category',
            'metal_purity',
            'finding_type',
        )

        for param, lookup in (
            ('cost_card_no', 'cost_card_no__icontains'),
            ('our_style_no', 'our_style_no__icontains'),
            ('vendor_style_no', 'vendor_style_no__icontains'),
        ):
            value = (params.get(param) or '').strip()
            if value:
                queryset = queryset.filter(Q(**{lookup: value}))

        for param, lookup in (
            ('customer', 'customer_id__in'),
            ('vendor', 'vendor_id__in'),
            ('category', 'category_id__in'),
            ('sub_category', 'sub_category_id__in'),
            ('metal_purity', 'metal_purity_id__in'),
        ):
            ids = _ids(params.get(param))
            if ids:
                queryset = queryset.filter(Q(**{lookup: ids}))

        return queryset