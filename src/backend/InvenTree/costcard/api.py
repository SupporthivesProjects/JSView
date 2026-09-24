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

    # def _list_param(self, key):
    #     values = []
    #     for value in self.request.query_params.getlist(key):
    #         values.extend(v.strip() for v in value.split(',') if v.strip())
    #     return values

    def _list_param(self, key):
        params = self.request.query_params
        if hasattr(params, 'getlist'):
            raw = params.getlist(key)
        else:
            raw = params.get(key, [])
            if not isinstance(raw, (list, tuple)):
                raw = [raw]
        values = []
        for value in raw:
            cleaned = str(value).strip('[]() ')
            values.extend(v.strip().strip('\'"') for v in cleaned.split(',') if v.strip())
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
]