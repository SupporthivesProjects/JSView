"""Provides the JSON API for the 'revision' app."""

from django.db.models import OuterRef, Subquery
from django.urls import path

from data_exporter.mixins import DataExportViewMixin

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI, RetrieveAPI
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from . import serializers as history_serializers
from .models import CostCardVersion


class HistoryPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class CostCardHistoryList(DataExportViewMixin, ListAPI):
    """
    List cost card history records.

    Cost cards are listed by their latest version.
    """

    latest_version = (
        CostCardVersion.objects
        .filter(
            cost_card=OuterRef('cost_card'),
            active=True,
        )
        .order_by('-version')
        .values('version')[:1]
    )

    queryset = (
        CostCardVersion.objects
        .select_related('cost_card', 'created_by')
        .filter(
            active=True,
            version=Subquery(latest_version),
        )
        .order_by('-created_at')
    )

    serializer_class = history_serializers.CostCardVersionListSerializer
    pagination_class = HistoryPagination

    filter_backends = SEARCH_ORDER_FILTER

    filterset_fields = [
        'cost_card',
        'active',
    ]

    search_fields = [
        'cost_card__number',
    ]

    ordering_fields = [
        'cost_card',
        'version',
        'created_at',
    ]

    ordering = '-created_at'


class CostCardHistoryDetail(RetrieveAPI):
    """
    Return complete version history for a specific cost card.
    """

    serializer_class = history_serializers.CostCardVersionSerializer

    def get_queryset(self):
        return (
            CostCardVersion.objects
            .select_related('cost_card', 'created_by')
            .filter(
                cost_card_id=self.kwargs['pk'],
                active=True,
            )
            .order_by('-version')
        )

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)


history_api_urls = [
    path(
        'costcard/',
        CostCardHistoryList.as_view(),
        name='api-history-costcard-list',
    ),
    path(
        'costcard/<int:pk>/',
        CostCardHistoryDetail.as_view(),
        name='api-history-costcard-detail',
    ),
]