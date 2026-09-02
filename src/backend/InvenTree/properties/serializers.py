"""DRF serializers for the 'properties' app."""

from rest_framework import serializers

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin

from company.models import Company

from .models import (
    ColorStone,
    ColorStoneColor,
    ColorStoneCut,
    ColorStoneQuality,
    ColorStoneRate,
    ColorStoneShape,
    ColorStoneSize,
    DiamondColor,
    DiamondCut,
    DiamondQuality,
    DiamondShape,
    DiamondSize,
    DiamondStone,
    DiamondStoneRate,
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
        fields = [
            'pk',
            'name',
            'mm_size',
            'sieve_size',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


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
        fields = [
            'pk',
            'name',
            'mm_size',
            'sieve_size',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


class ColorStoneQualitySerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the ColorStoneQuality model."""

    class Meta:
        model = ColorStoneQuality
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class RateCustomerBriefSerializer(serializers.ModelSerializer):
    """Minimal customer payload for rate dropdowns and nested detail."""

    class Meta:
        model = Company
        fields = ['pk', 'name', 'code', 'active']


class RateCustomerMixin(serializers.Serializer):
    """Shared customer multi-select fields for diamond / color-stone rates."""

    customers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Company.objects.filter(is_customer=True),
        required=False,
        allow_empty=True,
        help_text='Company PKs (is_customer=True) this rate applies to.',
    )
    customers_detail = RateCustomerBriefSerializer(
        source='customers', many=True, read_only=True
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        all_customers = attrs.get(
            'all_customers',
            getattr(self.instance, 'all_customers', False),
        )
        if all_customers:
            attrs['customers'] = []
        return attrs

    def create(self, validated_data):
        customers = validated_data.pop('customers', [])
        instance = super().create(validated_data)
        if not instance.all_customers and customers:
            instance.customers.set(customers)
        return instance

    def update(self, instance, validated_data):
        customers = validated_data.pop('customers', serializers.empty)
        instance = super().update(instance, validated_data)
        if instance.all_customers:
            instance.customers.clear()
        elif customers is not serializers.empty:
            instance.customers.set(customers)
        return instance


class DiamondStoneRateSerializer(
    RateCustomerMixin, DataExportSerializerMixin, InvenTreeModelSerializer
):
    """Serializer for the DiamondStoneRate model."""

    shape_detail = DiamondShapeSerializer(read_only=True, source='shape')
    mm_size_detail = DiamondSizeSerializer(read_only=True, source='mm_size')
    stone_detail = DiamondStoneSerializer(read_only=True, source='stone')
    color_detail = DiamondColorSerializer(read_only=True, source='color')
    cut_detail = DiamondCutSerializer(read_only=True, source='cut')
    quality_detail = DiamondQualitySerializer(read_only=True, source='quality')

    class Meta:
        model = DiamondStoneRate
        fields = [
            'pk',
            'shape', 'mm_size', 'stone', 'color', 'cut', 'quality',
            'pointer', 'rate', 'pc',
            'customers', 'customers_detail', 'all_customers',
            'active', 'created_at', 'updated_at',
            'shape_detail', 'mm_size_detail', 'stone_detail',
            'color_detail', 'cut_detail', 'quality_detail',
        ]
        read_only_fields = ['pk', 'created_at', 'updated_at']


class ColorStoneRateSerializer(
    RateCustomerMixin, DataExportSerializerMixin, InvenTreeModelSerializer
):
    """Serializer for the ColorStoneRate model."""

    shape_detail = ColorStoneShapeSerializer(read_only=True, source='shape')
    mm_size_detail = ColorStoneSizeSerializer(read_only=True, source='mm_size')
    stone_detail = ColorStoneSerializer(read_only=True, source='stone')
    color_detail = ColorStoneColorSerializer(read_only=True, source='color')
    cut_detail = ColorStoneCutSerializer(read_only=True, source='cut')
    quality_detail = ColorStoneQualitySerializer(read_only=True, source='quality')

    class Meta:
        model = ColorStoneRate
        fields = [
            'pk',
            'shape', 'mm_size', 'stone', 'color', 'cut', 'quality',
            'pointer', 'rate', 'pc',
            'customers', 'customers_detail', 'all_customers',
            'active', 'created_at', 'updated_at',
            'shape_detail', 'mm_size_detail', 'stone_detail',
            'color_detail', 'cut_detail', 'quality_detail',
        ]
        read_only_fields = ['pk', 'created_at', 'updated_at']
