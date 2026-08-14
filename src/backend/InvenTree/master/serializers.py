"""DRF serializers for the 'master' app."""

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin

from .models import (
    ACExecutive,
    CourierService,
    Duty,
    FindingType,
    FinishType,
    LabourSetting,
    MetalPurity,
    MetalRate,
    MetalType,
    Setting,
    Stamp,
    Terms,
)


class MetalTypeSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the MetalType model."""

    class Meta:
        model = MetalType
        fields = ['pk', 'code', 'name', 'description', 'active', 'created_at', 'updated_at']


class MetalPuritySerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the MetalPurity model."""

    class Meta:
        model = MetalPurity
        fields = ['pk', 'metal_type', 'name', 'purity', 'active', 'created_at', 'updated_at']


class MetalRateSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the MetalRate model."""

    class Meta:
        model = MetalRate
        fields = ['pk', 'metal_type', 'date', 'rate', 'active', 'created_at', 'updated_at']


class FindingTypeSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the FindingType model."""

    class Meta:
        model = FindingType
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class FinishTypeSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the FinishType model."""

    class Meta:
        model = FinishType
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class SettingSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the Setting model."""

    class Meta:
        model = Setting
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class LabourSettingSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the LabourSetting model."""

    class Meta:
        model = LabourSetting
        fields = ['pk', 'name', 'setting', 'charge_type', 'rate', 'active', 'created_at', 'updated_at']


class DutySerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the Duty model."""

    class Meta:
        model = Duty
        fields = ['pk', 'metal_type', 'duty', 'markup', 'description', 'active', 'created_at', 'updated_at']


class StampSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the Stamp model."""

    class Meta:
        model = Stamp
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class ACExecutiveSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the ACExecutive model."""

    class Meta:
        model = ACExecutive
        fields = ['pk', 'name', 'code', 'email', 'phone', 'active', 'created_at', 'updated_at']


class TermsSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the Terms model."""

    class Meta:
        model = Terms
        fields = ['pk', 'name', 'days', 'description', 'active', 'created_at', 'updated_at']


class CourierServiceSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the CourierService model."""

    class Meta:
        model = CourierService
        fields = ['pk', 'name', 'contact_person', 'phone', 'email', 'tracking_url', 'active', 'created_at', 'updated_at']