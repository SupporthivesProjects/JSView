"""DRF serializers for the 'master' app."""

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin
from data_importer.mixins import DataImportSerializerMixin

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


class MetalTypeSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = MetalType
        fields = ['pk', 'code', 'name', 'description', 'active', 'created_at', 'updated_at']


class MetalPuritySerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = MetalPurity
        fields = ['pk', 'metal_type', 'name', 'purity', 'active', 'created_at', 'updated_at']


class MetalRateSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = MetalRate
        fields = ['pk', 'metal_type', 'date', 'rate', 'active', 'created_at', 'updated_at']


class FindingTypeSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = FindingType
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class FinishTypeSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = FinishType
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class SettingSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = Setting
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class LabourSettingSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = LabourSetting
        fields = ['pk', 'name', 'setting', 'charge_type', 'rate', 'active', 'created_at', 'updated_at']


class DutySerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = Duty
        fields = ['pk', 'metal_type', 'duty', 'markup', 'description', 'active', 'created_at', 'updated_at']


class StampSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = Stamp
        fields = ['pk', 'name', 'description', 'image', 'active', 'created_at', 'updated_at']


class ACExecutiveSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = ACExecutive
        fields = ['pk', 'name', 'code', 'email', 'phone', 'active', 'created_at', 'updated_at']


class TermsSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = Terms
        fields = ['pk', 'name', 'days', 'description', 'active', 'created_at', 'updated_at']


class CourierServiceSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = CourierService
        fields = ['pk', 'name', 'contact_person', 'phone', 'email', 'tracking_url', 'active', 'created_at', 'updated_at']


class JewelryCategorySerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = JewelryCategory
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class JewelrySubCategorySerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = JewelrySubCategory
        fields = ['pk', 'category', 'name', 'description', 'active', 'created_at', 'updated_at']


class TemplatesSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = Templates
        fields = ['pk', 'name', 'subject', 'template', 'active', 'created_at', 'updated_at']


class POMailSerializer(DataImportSerializerMixin, DataExportSerializerMixin, InvenTreeModelSerializer):
    class Meta:
        model = POMail
        fields = ['pk', 'name', 'order', 'format1', 'format2', 'format3', 'format4', 'active', 'created_at', 'updated_at']