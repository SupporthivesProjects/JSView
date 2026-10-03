"""DRF serializers for the 'requisition' app."""

from decimal import ROUND_HALF_UP, Decimal

from rest_framework import serializers

from InvenTree.serializers import InvenTreeModelSerializer

from .models import FluteEntry, FluteEntryLine, MetalSent


class FluteEntryLineSerializer(InvenTreeModelSerializer):
    """Read serializer for a Flute Entry line."""

    class Meta:
        model = FluteEntryLine

        fields = [
            'pk',
            'flute_entry',
            'purchase_order',
            'cost_card',
            'cts',
            'stone_type',
            'sets',
            'stone_place',
            'rate',
            'amount',
            'cost_card_rate',
            'active',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'pk',
            'flute_entry',
            'created_at',
            'updated_at',
        ]


class FluteEntryLineCreateSerializer(InvenTreeModelSerializer):
    """Serializer for validating and creating Flute Entry lines.

    'flute_entry' is a normal writable field here, but API clients never
    send it: the view injects the parent entry's pk before validation.
    This is required because InvenTreeModelSerializer runs the model's
    full_clean(), which fails if the required FK is missing.
    """

    class Meta:
        model = FluteEntryLine

        fields = [
            'pk',
            'flute_entry',
            'purchase_order',
            'cost_card',
            'cts',
            'stone_type',
            'sets',
            'stone_place',
            'rate',
            'amount',
            'cost_card_rate',
            'active',
        ]

        read_only_fields = ['pk']

    def validate(self, data):
        """Auto-calculate amount (cts x rate) when it is not supplied."""

        if 'amount' not in self.initial_data:
            cts = data.get('cts', Decimal('0'))
            rate = data.get('rate', Decimal('0'))

            data['amount'] = (cts * rate).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP,
            )

        return super().validate(data)


class FluteEntrySerializer(InvenTreeModelSerializer):
    """Flute Entry header with its active lines nested (read-only)."""

    lines = serializers.SerializerMethodField()

    class Meta:
        model = FluteEntry

        fields = [
            'pk',
            'invoice_no',
            'flute_date',
            'prepby',
            'active',
            'lines',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'pk',
            'prepby',
            'lines',
            'created_at',
            'updated_at',
        ]

    def get_lines(self, obj):
        """Return active lines, using the prefetched list when available."""

        lines = getattr(obj, 'active_lines', None)

        if lines is None:
            lines = obj.lines.filter(active=True)

        return FluteEntryLineSerializer(
            lines,
            many=True,
            context=self.context,
        ).data


class MetalSentSerializer(InvenTreeModelSerializer):

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
            'pk',
            'metal_sent_no',
            'prepby',
            'created_at',
            'updated_at',
        ]