"""DRF serializers for the 'properties' app."""

from rest_framework.fields import empty

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin
from importer.mixins import DataImportSerializerMixin
from importer.registry import register_importer

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


@register_importer()
class DiamondStoneSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = DiamondStone
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class DiamondCutSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = DiamondCut
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class DiamondShapeSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = DiamondShape
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class DiamondColorSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = DiamondColor
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class DiamondSizeSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
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


@register_importer()
class DiamondQualitySerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = DiamondQuality
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class ColorStoneSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = ColorStone
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class ColorStoneCutSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = ColorStoneCut
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class ColorStoneShapeSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = ColorStoneShape
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class ColorStoneColorSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = ColorStoneColor
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class ColorStoneSizeSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
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


@register_importer()
class ColorStoneQualitySerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = ColorStoneQuality
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class DiamondStoneRateSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = DiamondStoneRate
        fields = [
            'pk',
            'shape',
            'mm_size',
            'stone',
            'color',
            'cut',
            'quality',
            'pointer',
            'rate',
            'pc',
            'all_customers',
            'customers',
            'active',
            'created_at',
            'updated_at',
        ]

    def run_validation(self, data=empty):
        extra_m2m = {}

        if data is not empty and hasattr(data, 'items'):
            data = data.copy() if hasattr(data, 'copy') else dict(data)
            if 'customers' in data:
                if hasattr(data, 'getlist'):
                    extra_m2m['customers'] = data.getlist('customers')
                    del data['customers']
                else:
                    extra_m2m['customers'] = data.pop('customers')

        validated_data = super().run_validation(data)
        validated_data.update(extra_m2m)
        return validated_data

    def create(self, validated_data):
        customers = validated_data.pop('customers', None)
        instance = super().create(validated_data)
        if customers is not None:
            instance.customers.set(customers)
        return instance

    def update(self, instance, validated_data):
        customers = validated_data.pop('customers', None)
        instance = super().update(instance, validated_data)
        if customers is not None:
            instance.customers.set(customers)
        return instance


@register_importer()
class ColorStoneRateSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = ColorStoneRate
        fields = [
            'pk',
            'shape',
            'mm_size',
            'stone',
            'color',
            'cut',
            'quality',
            'pointer',
            'rate',
            'pc',
            'all_customers',
            'customers',
            'active',
            'created_at',
            'updated_at',
        ]

    def run_validation(self, data=empty):
        extra_m2m = {}

        if data is not empty and hasattr(data, 'items'):
            data = data.copy() if hasattr(data, 'copy') else dict(data)
            if 'customers' in data:
                if hasattr(data, 'getlist'):
                    extra_m2m['customers'] = data.getlist('customers')
                    del data['customers']
                else:
                    extra_m2m['customers'] = data.pop('customers')

        validated_data = super().run_validation(data)
        validated_data.update(extra_m2m)
        return validated_data

    def create(self, validated_data):
        customers = validated_data.pop('customers', None)
        instance = super().create(validated_data)
        if customers is not None:
            instance.customers.set(customers)
        return instance

    def update(self, instance, validated_data):
        customers = validated_data.pop('customers', None)
        instance = super().update(instance, validated_data)
        if customers is not None:
            instance.customers.set(customers)
        return instance