from django.http import HttpResponse
from django.urls import include, path

from rest_framework import generics, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI

from costcard.permissions import CardsDataPermission, CostCardPermission

from . import serializers as cards_serializers
from .duplicates import duplicate_cost_card
from .multiexporter import CostCardSheetBuilder
from .models import (
    CostCard,
    CostCardColorStoneLine,
    CostCardDiamondLine,
    CostCardFinishLine,
    StonePlace,
)


class CardsPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class StonePlaceList(DataExportViewMixin, ListCreateAPI):
    queryset = StonePlace.objects.all()
    serializer_class = cards_serializers.StonePlaceSerializer
    pagination_class = CardsPagination
    permission_classes = [CardsDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class StonePlaceDetail(RetrieveUpdateDestroyAPI):
    queryset = StonePlace.objects.all()
    serializer_class = cards_serializers.StonePlaceSerializer
    permission_classes = [CardsDataPermission]


class CostCardList(DataExportViewMixin, ListCreateAPI):
    queryset = CostCard.objects.prefetch_related(
        'diamond_lines',
        'colorstone_lines',
        'finish_lines',
    ).all()
    serializer_class = cards_serializers.CostCardSerializer
    pagination_class = CardsPagination
    permission_classes = [CostCardPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = [
        'vendor',
        'customer',
        'category',
        'sub_category',
        'metal_purity',
        'finding_type',
        'finding_item',
        'active',
    ]
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
        'active',
    ]
    ordering = '-created_at'


class CostCardDetail(RetrieveUpdateDestroyAPI):
    queryset = CostCard.objects.prefetch_related(
        'diamond_lines',
        'colorstone_lines',
        'finish_lines',
    ).all()
    serializer_class = cards_serializers.CostCardSerializer
    permission_classes = [CostCardPermission]


class CostCardImageUpload(generics.UpdateAPIView):
    queryset = CostCard.objects.all()
    serializer_class = cards_serializers.CostCardImageSerializer
    permission_classes = [CostCardPermission]
    parser_classes = [MultiPartParser, FormParser]


class CostCardDiamondLineList(DataExportViewMixin, ListCreateAPI):
    queryset = CostCardDiamondLine.objects.all()
    serializer_class = cards_serializers.CostCardDiamondLineSerializer
    pagination_class = CardsPagination
    permission_classes = [CostCardPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = [
        'cost_card',
        'shape',
        'quality',
        'stone_place',
        'active',
    ]
    ordering_fields = [
        'pk',
        'created_at',
        'pcs',
        'cts',
        'amount',
    ]
    ordering = 'pk'


class CostCardDiamondLineDetail(RetrieveUpdateDestroyAPI):
    queryset = CostCardDiamondLine.objects.all()
    serializer_class = cards_serializers.CostCardDiamondLineSerializer
    permission_classes = [CostCardPermission]


class CostCardColorStoneLineList(DataExportViewMixin, ListCreateAPI):
    queryset = CostCardColorStoneLine.objects.all()
    serializer_class = cards_serializers.CostCardColorStoneLineSerializer
    pagination_class = CardsPagination
    permission_classes = [CostCardPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = [
        'cost_card',
        'shape',
        'quality',
        'stone_place',
        'active',
    ]
    ordering_fields = [
        'pk',
        'created_at',
        'pcs',
        'cts',
        'amount',
    ]
    ordering = 'pk'


class CostCardColorStoneLineDetail(RetrieveUpdateDestroyAPI):
    queryset = CostCardColorStoneLine.objects.all()
    serializer_class = cards_serializers.CostCardColorStoneLineSerializer
    permission_classes = [CostCardPermission]


class CostCardFinishLineList(DataExportViewMixin, ListCreateAPI):
    queryset = CostCardFinishLine.objects.all()
    serializer_class = cards_serializers.CostCardFinishLineSerializer
    pagination_class = CardsPagination
    permission_classes = [CostCardPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = [
        'cost_card',
        'finish_type',
        'active',
    ]
    ordering_fields = [
        'pk',
        'created_at',
        'rate',
    ]
    ordering = 'pk'


class CostCardFinishLineDetail(RetrieveUpdateDestroyAPI):
    queryset = CostCardFinishLine.objects.all()
    serializer_class = cards_serializers.CostCardFinishLineSerializer
    permission_classes = [CostCardPermission]


class CostCardDuplicate(generics.GenericAPIView):
    queryset = CostCard.objects.prefetch_related(
        'diamond_lines',
        'colorstone_lines',
        'finish_lines',
    ).all()
    serializer_class = cards_serializers.CostCardSerializer
    permission_classes = [CostCardPermission]

    def post(self, request, pk):
        cost_card = self.get_object()
        new_cost_card = duplicate_cost_card(cost_card, user=request.user)
        serializer = self.get_serializer(new_cost_card)

        return Response(
            {
                'duplicated': serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class CostCardPicturePresentation(DataExportViewMixin, generics.ListAPIView):
    queryset = CostCard.objects.select_related('metal_purity').prefetch_related('diamond_lines__stone')
    serializer_class = cards_serializers.CostCardPicturePresentationSerializer
    pagination_class = None
    permission_classes = [CostCardPermission]

    STONE_FIELDS = ('shape', 'mm_size', 'sieve_size', 'stone', 'color', 'cut', 'quality', 'pointer')

    # def _list_param(self, key):
    #     values = []
    #     for value in self.request.query_params.getlist(key):
    #         values.extend(v.strip() for v in value.split(',') if v.strip())
    #     return values

    def _list_param(self, key):
        params = self.request.query_params
        raw = params.getlist(key) if hasattr(params, 'getlist') else params.get(key, [])
        raw = raw if isinstance(raw, (list, tuple)) else [raw]
        values = []
        for value in raw:
            values.extend(v.strip().strip('\'"') for v in str(value).strip('[]() ').split(',') if v.strip())
        return values

    def get_queryset(self):
        queryset = super().get_queryset()
        # nos = self.request.query_params.get('cost_card_nos', '')
        # nos = [n.strip() for n in nos.split(',') if n.strip()]
        # if nos:
        #     queryset = queryset.filter(cost_card_no__in=nos)
        nos = self._list_param('cost_card_nos')
        ids = [i for i in self._list_param('cost_card_ids') if i.isdigit()]
        if nos:
            queryset = queryset.filter(cost_card_no__in=nos)
        if ids:
            queryset = queryset.filter(pk__in=ids)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        for key in ('duty_pct', 'margin_pct', 'gold_troy_ounce', 'silver_troy_ounce'):
            value = self.request.query_params.get(key)
            if value not in (None, ''):
                context[key] = value
        return context

    # @staticmethod
    # def _label(value):
    #     if value is None:
    #         return ''
    #     if hasattr(value, 'normalize'):
    #         return format(value.normalize(), 'f')
    #     if hasattr(value, '_meta'):
    #         for attr in ('name', 'quality_name', 'title', 'label', 'code'):
    #             if getattr(value, attr, None):
    #                 return str(getattr(value, attr))
    #     return str(value)

    @staticmethod
    def _name_label(value):
        return '' if value is None else str(getattr(value, 'name', value))

    @staticmethod
    def _number_label(value):
        return '' if value is None else format(value.normalize(), 'f')

    @staticmethod
    def _mm_size_label(value):
        return '' if value is None else str(value.mm_size or value.name)

    # def _stone_key(self, line):
    #     return tuple(
    #         self._number_label(line.pointer) if field == 'pointer' else self._name_label(getattr(line, field))
    #         for field in self.STONE_FIELDS
    #     )

    def _stone_key(self, line):
        special = {'pointer': self._number_label, 'mm_size': self._mm_size_label}
        return tuple(special.get(f, self._name_label)(getattr(line, f)) for f in self.STONE_FIELDS)

    def _stones(self, queryset):
        rows = {}
        for card in queryset:
            for line in [*card.diamond_lines.all(), *card.colorstone_lines.all()]:
                key = self._stone_key(line)
                if key not in rows:
                    rows[key] = {**dict(zip(self.STONE_FIELDS, key)), 'rate': line.rate}
        return list(rows.values())

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if request.query_params.get('export'):
            return response
        queryset = self.filter_queryset(self.get_queryset())
        return Response({'results': response.data, 'stones': self._stones(queryset)})


class CostCardRepresentation(generics.GenericAPIView):
    queryset = CostCard.objects.select_related(
        'metal_purity__metal_type', 'vendor', 'customer', 'category', 'sub_category',
    ).prefetch_related(
        'diamond_lines__shape', 'diamond_lines__mm_size', 'diamond_lines__stone',
        'diamond_lines__color', 'diamond_lines__cut', 'diamond_lines__setting',
        'colorstone_lines__shape', 'colorstone_lines__mm_size', 'colorstone_lines__stone',
        'colorstone_lines__color', 'colorstone_lines__cut', 'colorstone_lines__setting',
        'finish_lines__finish_type',
    )
    permission_classes = [CostCardPermission]

    def _list_param(self, key):
        params = self.request.query_params
        raw = params.getlist(key) if hasattr(params, 'getlist') else params.get(key, [])
        raw = raw if isinstance(raw, (list, tuple)) else [raw]
        values = []
        for value in raw:
            values.extend(v.strip().strip('\'"') for v in str(value).strip('[]() ').split(',') if v.strip())
        return values

    def get_queryset(self):
        queryset = super().get_queryset()
        nos = self._list_param('cost_card_nos')
        ids = [i for i in self._list_param('cost_card_ids') if i.isdigit()]
        if nos:
            queryset = queryset.filter(cost_card_no__in=nos)
        if ids:
            queryset = queryset.filter(pk__in=ids)
        return queryset

    def _overrides(self):
        params = self.request.query_params
        keys = ('duty_pct', 'margin_pct', 'gold_troy_ounce', 'silver_troy_ounce')
        return {key: params.get(key) for key in keys if params.get(key) not in (None, '')}

    def _modified_by(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return ''
        return user.get_full_name() or user.get_username()

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        builder = CostCardSheetBuilder(overrides=self._overrides(), modified_by=self._modified_by())
        content = builder.to_bytes(builder.build(queryset))

        response = HttpResponse(
            content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="CostCardRepresentation.xlsx"'
        return response


cards_api_urls = [
    path(
        'stone-place/',
        include([
            path(
                '<int:pk>/',
                StonePlaceDetail.as_view(),
                name='api-stone-place-detail',
            ),
            path(
                '',
                StonePlaceList.as_view(),
                name='api-stone-place-list',
            ),
        ]),
    ),
    path(
        'cost-card/',
        include([
            path(
                '<int:pk>/',
                include([
                    path(
                        'images/',
                        CostCardImageUpload.as_view(),
                        name='api-cost-card-images',
                    ),
                    path(
                        'duplicate/',
                        CostCardDuplicate.as_view(),
                        name='api-cost-card-duplicate',
                    ),
                    path(
                        '',
                        CostCardDetail.as_view(),
                        name='api-cost-card-detail',
                    ),
                ]),
            ),
            path(
                '',
                CostCardList.as_view(),
                name='api-cost-card-list',
            ),
        ]),
    ),
    path(
        'cost-card-diamond-line/',
        include([
            path(
                '<int:pk>/',
                CostCardDiamondLineDetail.as_view(),
                name='api-cost-card-diamond-line-detail',
            ),
            path(
                '',
                CostCardDiamondLineList.as_view(),
                name='api-cost-card-diamond-line-list',
            ),
        ]),
    ),
    path(
        'cost-card-colorstone-line/',
        include([
            path(
                '<int:pk>/',
                CostCardColorStoneLineDetail.as_view(),
                name='api-cost-card-colorstone-line-detail',
            ),
            path(
                '',
                CostCardColorStoneLineList.as_view(),
                name='api-cost-card-colorstone-line-list',
            ),
        ]),
    ),
    path(
        'cost-card-finish-line/',
        include([
            path(
                '<int:pk>/',
                CostCardFinishLineDetail.as_view(),
                name='api-cost-card-finish-line-detail',
            ),
            path(
                '',
                CostCardFinishLineList.as_view(),
                name='api-cost-card-finish-line-list',
            ),
        ]),
    ),
    path(
        'picture-presentation/',
        CostCardPicturePresentation.as_view(),
        name='api-picture-presentation',
    ),
    path(
        'costcard-representation/',
        CostCardRepresentation.as_view(),
        name='api-costcard-representation',
    ),
]