"""API views for the 'properties' app."""

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI
from rest_framework.pagination import LimitOffsetPagination

from . import serializers as properties_serializers
from .models import (
    ColorStone,
    ColorStoneColor,
    ColorStoneCut,
    ColorStoneShape,
    ColorStoneSize,
    DiamondColor,
    DiamondCut,
    DiamondQuality,
    DiamondShape,
    DiamondSize,
    DiamondStone,
)
from .permissions import PropertiesDataPermission


class PropertiesPagination(LimitOffsetPagination):
    """Default pagination for properties app list endpoints."""

    default_limit = 10
    max_limit = 100


class DiamondStoneList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating DiamondStone objects."""

    queryset = DiamondStone.objects.all()
    serializer_class = properties_serializers.DiamondStoneSerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class DiamondStoneDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single DiamondStone object."""

    queryset = DiamondStone.objects.all()
    serializer_class = properties_serializers.DiamondStoneSerializer
    permission_classes = [PropertiesDataPermission]


class DiamondCutList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating DiamondCut objects."""

    queryset = DiamondCut.objects.all()
    serializer_class = properties_serializers.DiamondCutSerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class DiamondCutDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single DiamondCut object."""

    queryset = DiamondCut.objects.all()
    serializer_class = properties_serializers.DiamondCutSerializer
    permission_classes = [PropertiesDataPermission]


class DiamondShapeList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating DiamondShape objects."""

    queryset = DiamondShape.objects.all()
    serializer_class = properties_serializers.DiamondShapeSerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class DiamondShapeDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single DiamondShape object."""

    queryset = DiamondShape.objects.all()
    serializer_class = properties_serializers.DiamondShapeSerializer
    permission_classes = [PropertiesDataPermission]


class DiamondColorList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating DiamondColor objects."""

    queryset = DiamondColor.objects.all()
    serializer_class = properties_serializers.DiamondColorSerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class DiamondColorDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single DiamondColor object."""

    queryset = DiamondColor.objects.all()
    serializer_class = properties_serializers.DiamondColorSerializer
    permission_classes = [PropertiesDataPermission]


class DiamondSizeList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating DiamondSize objects."""

    queryset = DiamondSize.objects.all()
    serializer_class = properties_serializers.DiamondSizeSerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class DiamondSizeDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single DiamondSize object."""

    queryset = DiamondSize.objects.all()
    serializer_class = properties_serializers.DiamondSizeSerializer
    permission_classes = [PropertiesDataPermission]


class DiamondQualityList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating DiamondQuality objects."""

    queryset = DiamondQuality.objects.all()
    serializer_class = properties_serializers.DiamondQualitySerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class DiamondQualityDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single DiamondQuality object."""

    queryset = DiamondQuality.objects.all()
    serializer_class = properties_serializers.DiamondQualitySerializer
    permission_classes = [PropertiesDataPermission]


class ColorStoneList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating ColorStone objects."""

    queryset = ColorStone.objects.all()
    serializer_class = properties_serializers.ColorStoneSerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class ColorStoneDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single ColorStone object."""

    queryset = ColorStone.objects.all()
    serializer_class = properties_serializers.ColorStoneSerializer
    permission_classes = [PropertiesDataPermission]


class ColorStoneCutList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating ColorStoneCut objects."""

    queryset = ColorStoneCut.objects.all()
    serializer_class = properties_serializers.ColorStoneCutSerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class ColorStoneCutDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single ColorStoneCut object."""

    queryset = ColorStoneCut.objects.all()
    serializer_class = properties_serializers.ColorStoneCutSerializer
    permission_classes = [PropertiesDataPermission]


class ColorStoneShapeList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating ColorStoneShape objects."""

    queryset = ColorStoneShape.objects.all()
    serializer_class = properties_serializers.ColorStoneShapeSerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class ColorStoneShapeDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single ColorStoneShape object."""

    queryset = ColorStoneShape.objects.all()
    serializer_class = properties_serializers.ColorStoneShapeSerializer
    permission_classes = [PropertiesDataPermission]


class ColorStoneColorList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating ColorStoneColor objects."""

    queryset = ColorStoneColor.objects.all()
    serializer_class = properties_serializers.ColorStoneColorSerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class ColorStoneColorDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single ColorStoneColor object."""

    queryset = ColorStoneColor.objects.all()
    serializer_class = properties_serializers.ColorStoneColorSerializer
    permission_classes = [PropertiesDataPermission]


class ColorStoneSizeList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating ColorStoneSize objects."""

    queryset = ColorStoneSize.objects.all()
    serializer_class = properties_serializers.ColorStoneSizeSerializer
    pagination_class = PropertiesPagination
    permission_classes = [PropertiesDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = 'name'


class ColorStoneSizeDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single ColorStoneSize object."""

    queryset = ColorStoneSize.objects.all()
    serializer_class = properties_serializers.ColorStoneSizeSerializer
    permission_classes = [PropertiesDataPermission]
