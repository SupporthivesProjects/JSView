"""DRF serializers for the 'properties' app."""

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin

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


class DiamondStoneSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the DiamondStone model."""

    class Meta:
        model = DiamondStone
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class DiamondCutSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the DiamondCut model."""

    class Meta:
        model = DiamondCut
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class DiamondShapeSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the DiamondShape model."""

    class Meta:
        model = DiamondShape
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class DiamondColorSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the DiamondColor model."""

    class Meta:
        model = DiamondColor
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class DiamondSizeSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the DiamondSize model."""

    class Meta:
        model = DiamondSize
        fields = ['pk', 'name', 'mm_size', 'description', 'active', 'created_at', 'updated_at']


class DiamondQualitySerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the DiamondQuality model."""

    class Meta:
        model = DiamondQuality
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class ColorStoneSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the ColorStone model."""

    class Meta:
        model = ColorStone
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class ColorStoneCutSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the ColorStoneCut model."""

    class Meta:
        model = ColorStoneCut
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class ColorStoneShapeSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the ColorStoneShape model."""

    class Meta:
        model = ColorStoneShape
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class ColorStoneColorSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the ColorStoneColor model."""

    class Meta:
        model = ColorStoneColor
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class ColorStoneSizeSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the ColorStoneSize model."""

    class Meta:
        model = ColorStoneSize
        fields = ['pk', 'name', 'mm_size', 'description', 'active', 'created_at', 'updated_at']
