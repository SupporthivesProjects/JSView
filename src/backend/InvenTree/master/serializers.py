"""DRF serializers for the 'master' app."""

from InvenTree.serializers import InvenTreeModelSerializer

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
    POMail,
    POMailTemplate,
    Setting,
    Stamp,
    Terms,
)


class MetalTypeSerializer(InvenTreeModelSerializer):
    """Serializer for the MetalType model."""

    class Meta:
        model = MetalType
        fields = ['pk', 'code', 'name', 'description', 'active', 'created_at', 'updated_at']


class MetalPuritySerializer(InvenTreeModelSerializer):
    """Serializer for the MetalPurity model."""

    class Meta:
        model = MetalPurity
        fields = ['pk', 'metal_type', 'name', 'fineness', 'active', 'created_at', 'updated_at']


class SettingSerializer(InvenTreeModelSerializer):
    """Serializer for the Setting model."""

    class Meta:
        model = Setting
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class LabourSettingSerializer(InvenTreeModelSerializer):
    """Serializer for the LabourSetting model."""

    class Meta:
        model = LabourSetting
        fields = ['pk', 'name', 'setting', 'charge_type', 'rate', 'active', 'created_at', 'updated_at']


class MetalRateSerializer(InvenTreeModelSerializer):
    """Serializer for the MetalRate model."""

    class Meta:
        model = MetalRate
        fields = ['pk', 'metal_type', 'purity', 'date', 'rate', 'active', 'created_at', 'updated_at']


class FindingTypeSerializer(InvenTreeModelSerializer):
    """Serializer for the FindingType model."""

    class Meta:
        model = FindingType
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class FinishTypeSerializer(InvenTreeModelSerializer):
    """Serializer for the FinishType model."""

    class Meta:
        model = FinishType
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class DutySerializer(InvenTreeModelSerializer):
    """Serializer for the Duty model."""

    class Meta:
        model = Duty
        fields = ['pk', 'name', 'percentage', 'description', 'active', 'created_at', 'updated_at']


class StampSerializer(InvenTreeModelSerializer):
    """Serializer for the Stamp model."""

    class Meta:
        model = Stamp
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


class ACExecutiveSerializer(InvenTreeModelSerializer):
    """Serializer for the ACExecutive model."""

    class Meta:
        model = ACExecutive
        fields = ['pk', 'name', 'code', 'user', 'email', 'phone', 'active', 'created_at', 'updated_at']


class TermsSerializer(InvenTreeModelSerializer):
    """Serializer for the Terms model."""

    class Meta:
        model = Terms
        fields = ['pk', 'name', 'days', 'description', 'active', 'created_at', 'updated_at']


class CourierServiceSerializer(InvenTreeModelSerializer):
    """Serializer for the CourierService model."""

    class Meta:
        model = CourierService
        fields = ['pk', 'name', 'contact_person', 'phone', 'email', 'tracking_url', 'active', 'created_at', 'updated_at']


class POMailTemplateSerializer(InvenTreeModelSerializer):
    """Serializer for the POMailTemplate model."""

    class Meta:
        model = POMailTemplate
        fields = ['pk', 'name', 'subject', 'body', 'active', 'created_at', 'updated_at']


class POMailSerializer(InvenTreeModelSerializer):
    """Serializer for the POMail model."""

    class Meta:
        model = POMail
        fields = ['pk', 'name', 'vendor', 'template', 'email', 'description', 'active', 'created_at', 'updated_at']