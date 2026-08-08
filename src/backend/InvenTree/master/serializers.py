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
    Setting,
    Stamp,
    Terms,
)


class MetalTypeSerializer(InvenTreeModelSerializer):
    """Serializer for the MetalType model."""

    class Meta:
        model = MetalType
        fields = ['pk', 'name', 'description', 'active']


class MetalPuritySerializer(InvenTreeModelSerializer):
    """Serializer for the MetalPurity model."""

    class Meta:
        model = MetalPurity
        fields = ['pk', 'metal_type', 'name', 'purity', 'karat', 'active']


class SettingSerializer(InvenTreeModelSerializer):
    """Serializer for the Setting model."""

    class Meta:
        model = Setting
        fields = ['pk', 'name', 'description', 'active']


class LabourSettingSerializer(InvenTreeModelSerializer):
    """Serializer for the LabourSetting model."""

    class Meta:
        model = LabourSetting
        fields = ['pk', 'name', 'code', 'cfpon', 'loss', 'vendor', 'active']


class MetalRateSerializer(InvenTreeModelSerializer):
    """Serializer for the MetalRate model."""

    class Meta:
        model = MetalRate
        fields = ['pk', 'metal_type', 'rate_date', 'rate', 'active']


class FindingTypeSerializer(InvenTreeModelSerializer):
    """Serializer for the FindingType model."""

    class Meta:
        model = FindingType
        fields = ['pk', 'name', 'description', 'active']


class FinishTypeSerializer(InvenTreeModelSerializer):
    """Serializer for the FinishType model."""

    class Meta:
        model = FinishType
        fields = ['pk', 'name', 'description', 'active']


class DutySerializer(InvenTreeModelSerializer):
    """Serializer for the Duty model."""

    class Meta:
        model = Duty
        fields = ['pk', 'name', 'duty_percent', 'markup_percent', 'description', 'active']


class StampSerializer(InvenTreeModelSerializer):
    """Serializer for the Stamp model."""

    class Meta:
        model = Stamp
        fields = ['pk', 'name', 'description', 'active']


class ACExecutiveSerializer(InvenTreeModelSerializer):
    """Serializer for the ACExecutive model."""

    class Meta:
        model = ACExecutive
        fields = ['pk', 'name', 'code', 'email', 'phone', 'address', 'active']


class TermsSerializer(InvenTreeModelSerializer):
    """Serializer for the Terms model."""

    class Meta:
        model = Terms
        fields = ['pk', 'name', 'days', 'description', 'active']


class CourierServiceSerializer(InvenTreeModelSerializer):
    """Serializer for the CourierService model."""

    class Meta:
        model = CourierService
        fields = ['pk', 'name', 'contact_person', 'phone', 'email', 'tracking_url', 'active']


class POMailSerializer(InvenTreeModelSerializer):
    """Serializer for the POMail model."""

    class Meta:
        model = POMail
        fields = ['pk', 'purchase_order', 'format1_email', 'format2_email', 'format3_email', 'format4_email', 'active']