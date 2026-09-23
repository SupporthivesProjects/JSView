"""DRF serializers for the 'requisition' app."""

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin
from importer.mixins import DataImportSerializerMixin
from importer.registry import register_importer

from .models import MetalSent


@register_importer()
class MetalSentSerializer(
    DataImportSerializerMixin,
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = MetalSent
        fields = [
            'pk',
            'metal_sent_no',
            'invoice_no',
            'metal_sent_date',
            'purchase_order',
            'triounce',
            'metal_gms',
            'metal_amount',
            'prepby',
            'active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'metal_sent_no',
            'prepby',
        ]