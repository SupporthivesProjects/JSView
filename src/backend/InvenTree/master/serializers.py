"""DRF serializers for the 'master' app."""

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin
from importer.mixins import DataImportSerializerMixin
from importer.registry import register_importer

from .models import (
    ACExecutive,
    CourierService,
    Duty,
    FindingType,
    FinishType,
    JewelryCategory,
    JewelrySubCategory,
    LabourSetting,
    MetalPurity,
    MetalRate,
    MetalType,
    POMail,
    Setting,
    Stamp,
    Templates,
    Terms,
)


@register_importer()
class MetalTypeSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = MetalType
        fields = [
            'pk',
            'code',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class MetalPuritySerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = MetalPurity
        fields = [
            'pk',
            'metal_type',
            'name',
            'purity',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class MetalRateSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = MetalRate
        fields = [
            'pk',
            'metal_type',
            'date',
            'rate',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class FindingTypeSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = FindingType
        fields = [
            'pk',
            'name',
            'type',
            'weight',
            'metal',
            'price',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class FinishTypeSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = FinishType
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class SettingSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = Setting
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class LabourSettingSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = LabourSetting
        fields = [
            'pk',
            'name',
            'setting',
            'charge_type',
            'rate',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class DutySerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = Duty
        fields = [
            'pk',
            'metal_type',
            'duty',
            'markup',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class StampSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = Stamp
        fields = [
            'pk',
            'name',
            'description',
            'image',
            'customers',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class ACExecutiveSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = ACExecutive
        fields = [
            'pk',
            'name',
            'code',
            'email',
            'phone',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class TermsSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = Terms
        fields = [
            'pk',
            'name',
            'days',
            'vendors',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class CourierServiceSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = CourierService
        fields = [
            'pk',
            'name',
            'contact_person',
            'phone',
            'email',
            'tracking_url',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class JewelryCategorySerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = JewelryCategory
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class JewelrySubCategorySerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = JewelrySubCategory
        fields = [
            'pk',
            'category',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class TemplatesSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = Templates
        fields = [
            'pk',
            'name',
            'subject',
            'template',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class POMailSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = POMail
        fields = [
            'pk',
            'name',
            'order',
            'format1',
            'format2',
            'format3',
            'format4',
            'active',
            'created_at',
            'updated_at',
        ]