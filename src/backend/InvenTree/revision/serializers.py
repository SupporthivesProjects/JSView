"""DRF serializers for the 'revision' app."""

from InvenTree.serializers import InvenTreeModelSerializer

from .models import CostCardVersion


class CostCardVersionSerializer(InvenTreeModelSerializer):
    class Meta:
        model = CostCardVersion
        fields = [
            'pk',
            'cost_card',
            'version',
            'data',
            'created_by',
            'created_at',
            'active',
        ]


class CostCardVersionListSerializer(InvenTreeModelSerializer):
    class Meta:
        model = CostCardVersion
        fields = [
            'pk',
            'cost_card',
            'version',
            'created_by',
            'created_at',
            'active',
        ]

