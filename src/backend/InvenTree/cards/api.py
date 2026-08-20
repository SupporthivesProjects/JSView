from django.urls import include, path

from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import generics, status
from rest_framework.response import Response

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI

from cards.permissions import CardsDataPermission, CostCardPermission

from . import serializers as cards_serializers
from .models import (
    CostCard,
    CostCardColorStoneLine,
    CostCardDiamondLine,
    CostCardFinishLine,
    StonePlace,
)
from .duplicates import duplicate_cost_card


class CardsPagination(LimitOffsetPagination):
    """Default pagination for cards app list endpoints."""

    default_limit = 10
    max_limit = 100


# ---------------------------------------------------------------------------
# Master-like reference data
# ---------------------------------------------------------------------------


class StonePlaceList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating StonePlace objects."""

    queryset = StonePlace.objects.all()
    serializer_class = cards_serializers.StonePlaceSerializer
    pagination_class = CardsPagination
    permission_classes = [CardsDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class StonePlaceDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single StonePlace object."""

    queryset = StonePlace.objects.all()
    serializer_class = cards_serializers.StonePlaceSerializer
    permission_classes = [CardsDataPermission]


# ---------------------------------------------------------------------------
# Cost Card - the main tabbed-form endpoint (nested create/update)
# ---------------------------------------------------------------------------


class CostCardList(DataExportViewMixin, ListCreateAPI):
    """
    API endpoint for listing / creating CostCard objects.

    POST accepts the whole tabbed form at once, including nested
    diamond_lines / colorstone_lines / finish_lines arrays - see
    CostCardSerializer for the exact payload shape.
    """

    queryset = CostCard.objects.prefetch_related(
        'diamond_lines', 'colorstone_lines', 'finish_lines'
    ).all()
    serializer_class = cards_serializers.CostCardSerializer
    pagination_class = CardsPagination
    permission_classes = [CostCardPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['vendor', 'customer', 'category', 'sub_category', 'metal_purity', 'finding_type', 'active']
    search_fields = ['cost_card_no', 'our_style_no', 'vendor_style_no']
    ordering_fields = ['cost_card_no', 'our_style_no', 'created_at', 'final_amount', 'active']
    ordering = '-created_at'


class CostCardDetail(RetrieveUpdateDestroyAPI):
    """
    API endpoint for detail view of a single CostCard object.

    PUT/PATCH accept the same nested shape as CostCardList's POST, so the
    whole form (or just the tab(s) being edited) can be resubmitted here.
    """

    queryset = CostCard.objects.prefetch_related(
        'diamond_lines', 'colorstone_lines', 'finish_lines'
    ).all()
    serializer_class = cards_serializers.CostCardSerializer
    permission_classes = [CostCardPermission]


class CostCardImageUpload(generics.UpdateAPIView):
    """
    API endpoint for the Images tab.

    PATCH multipart/form-data with any of front_view / side_view /
    back_view to upload that view for a cost card, independently of the
    main JSON create/update endpoint above.
    """

    queryset = CostCard.objects.all()
    serializer_class = cards_serializers.CostCardImageSerializer
    permission_classes = [CostCardPermission]
    parser_classes = [MultiPartParser, FormParser]


# ---------------------------------------------------------------------------
# Per-line endpoints - manage a single existing row without resubmitting
# the whole cost card.
# ---------------------------------------------------------------------------


class CostCardDiamondLineList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating CostCardDiamondLine objects."""

    queryset = CostCardDiamondLine.objects.all()
    serializer_class = cards_serializers.CostCardDiamondLineSerializer
    pagination_class = CardsPagination
    permission_classes = [CostCardPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['cost_card', 'shape', 'quality', 'stone_place', 'active']
    ordering_fields = ['pk', 'created_at', 'pcs', 'cts', 'amount']
    ordering = 'pk'


class CostCardDiamondLineDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single CostCardDiamondLine object."""

    queryset = CostCardDiamondLine.objects.all()
    serializer_class = cards_serializers.CostCardDiamondLineSerializer
    permission_classes = [CostCardPermission]


class CostCardColorStoneLineList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating CostCardColorStoneLine objects."""

    queryset = CostCardColorStoneLine.objects.all()
    serializer_class = cards_serializers.CostCardColorStoneLineSerializer
    pagination_class = CardsPagination
    permission_classes = [CostCardPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['cost_card', 'shape', 'quality', 'stone_place', 'active']
    ordering_fields = ['pk', 'created_at', 'pcs', 'cts', 'amount']
    ordering = 'pk'


class CostCardColorStoneLineDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single CostCardColorStoneLine object."""

    queryset = CostCardColorStoneLine.objects.all()
    serializer_class = cards_serializers.CostCardColorStoneLineSerializer
    permission_classes = [CostCardPermission]


class CostCardFinishLineList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating CostCardFinishLine objects."""

    queryset = CostCardFinishLine.objects.all()
    serializer_class = cards_serializers.CostCardFinishLineSerializer
    pagination_class = CardsPagination
    permission_classes = [CostCardPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['cost_card', 'finish_type', 'active']
    ordering_fields = ['pk', 'created_at', 'rate']
    ordering = 'pk'


class CostCardFinishLineDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single CostCardFinishLine object."""

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

        new_cost_card = duplicate_cost_card(cost_card)

        serializer = self.get_serializer(new_cost_card)

        return Response(
            {
                'duplicated': serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


cards_api_urls = [
    path('stone-place/', include([
        path('<int:pk>/', StonePlaceDetail.as_view(), name='api-stone-place-detail'),
        path('', StonePlaceList.as_view(), name='api-stone-place-list'),
    ])),

    path('cost-card/', include([
        path(
            '<int:pk>/',
            include([
                path('images/', CostCardImageUpload.as_view(), name='api-cost-card-images'),
                path('duplicate/', CostCardDuplicate.as_view(), name='api-cost-card-duplicate'),
                path('', CostCardDetail.as_view(), name='api-cost-card-detail'),
            ])
        ),
        path('', CostCardList.as_view(), name='api-cost-card-list'),
    ])),

    path('cost-card-diamond-line/', include([
        path('<int:pk>/', CostCardDiamondLineDetail.as_view(), name='api-cost-card-diamond-line-detail'),
        path('', CostCardDiamondLineList.as_view(), name='api-cost-card-diamond-line-list'),
    ])),

    path('cost-card-colorstone-line/', include([
        path('<int:pk>/', CostCardColorStoneLineDetail.as_view(), name='api-cost-card-colorstone-line-detail'),
        path('', CostCardColorStoneLineList.as_view(), name='api-cost-card-colorstone-line-list'),
    ])),

    path('cost-card-finish-line/', include([
        path('<int:pk>/', CostCardFinishLineDetail.as_view(), name='api-cost-card-finish-line-detail'),
        path('', CostCardFinishLineList.as_view(), name='api-cost-card-finish-line-list'),
    ])),
]