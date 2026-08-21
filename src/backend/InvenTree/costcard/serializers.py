from rest_framework import serializers as drf_serializers

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin

from .models import (
    CostCard,
    CostCardColorStoneLine,
    CostCardDiamondLine,
    CostCardFinishLine,
    StonePlace,
)

# ---------------------------------------------------------------------------
# Master-like reference data
# ---------------------------------------------------------------------------


class StonePlaceSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the StonePlace model."""

    class Meta:
        model = StonePlace
        fields = ['pk', 'name', 'description', 'active', 'created_at', 'updated_at']


# ---------------------------------------------------------------------------
# Standalone line serializers - used by the dedicated line endpoints
# (list all lines for a cost card, edit/delete a single existing row).
# ---------------------------------------------------------------------------


class CostCardDiamondLineSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the CostCardDiamondLine model (standalone endpoint)."""

    class Meta:
        model = CostCardDiamondLine
        fields = [
            'pk', 'cost_card', 'stone', 'shape', 'mm_size', 'color', 'cut', 'quality',
            'setting', 'stone_place', 'rate_source', 'pointer', 'sieve_size', 'pcs', 'cts',
            'default_rate', 'pc', 'rate', 'amount', 'labour_rate', 'labour_amount',
            'active', 'created_at', 'updated_at',
        ]


class CostCardColorStoneLineSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the CostCardColorStoneLine model (standalone endpoint)."""

    class Meta:
        model = CostCardColorStoneLine
        fields = [
            'pk', 'cost_card', 'stone', 'shape', 'mm_size', 'color', 'cut', 'quality',
            'setting', 'stone_place', 'rate_source', 'pointer', 'sieve_size', 'pcs', 'cts',
            'default_rate', 'pc', 'rate', 'amount', 'labour_rate', 'labour_amount',
            'active', 'created_at', 'updated_at',
        ]


class CostCardFinishLineSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """Serializer for the CostCardFinishLine model (standalone endpoint)."""

    class Meta:
        model = CostCardFinishLine
        fields = ['pk', 'cost_card', 'finish_type', 'rate', 'active', 'created_at', 'updated_at']


# ---------------------------------------------------------------------------
# Nested line serializers - embedded inside CostCardSerializer only.
# No 'cost_card' field (it's implied by the parent), and 'id' is optional
# so an update payload can mix: existing rows to edit (send id), new rows
# to add (omit id), and rows that were removed on the tab simply aren't
# included and get deleted server-side.
# ---------------------------------------------------------------------------


class NestedDiamondLineSerializer(drf_serializers.ModelSerializer):
    """Nested (writable) diamond line, used only inside CostCardSerializer."""

    id = drf_serializers.IntegerField(required=False)

    class Meta:
        model = CostCardDiamondLine
        fields = [
            'id', 'stone', 'shape', 'mm_size', 'color', 'cut', 'quality',
            'setting', 'stone_place', 'rate_source', 'pointer', 'sieve_size', 'pcs', 'cts',
            'default_rate', 'pc', 'rate', 'amount', 'labour_rate', 'labour_amount', 'active',
        ]


class NestedColorStoneLineSerializer(drf_serializers.ModelSerializer):
    """Nested (writable) color stone line, used only inside CostCardSerializer."""

    id = drf_serializers.IntegerField(required=False)

    class Meta:
        model = CostCardColorStoneLine
        fields = [
            'id', 'stone', 'shape', 'mm_size', 'color', 'cut', 'quality',
            'setting', 'stone_place', 'rate_source', 'pointer', 'sieve_size', 'pcs', 'cts',
            'default_rate', 'pc', 'rate', 'amount', 'labour_rate', 'labour_amount', 'active',
        ]


class NestedFinishLineSerializer(drf_serializers.ModelSerializer):
    """Nested (writable) finish type line, used only inside CostCardSerializer."""

    id = drf_serializers.IntegerField(required=False)

    class Meta:
        model = CostCardFinishLine
        fields = ['id', 'finish_type', 'rate', 'active']


# ---------------------------------------------------------------------------
# Main Cost Card serializer
# ---------------------------------------------------------------------------


class CostCardSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """
    Serializer for the CostCard model.

    Accepts the whole tabbed form in one request:
      - General / Measurement / Instructions / Cost fields as flat fields
      - diamond_lines / colorstone_lines / finish_lines as nested lists

    Front/Side/Back view images are intentionally NOT writable here -
    upload those via the dedicated multipart endpoint
    `PATCH /api/cards/cost-card/<pk>/images/` (see CostCardImageUpload in
    api.py), since mixing file uploads with nested JSON arrays in one
    multipart request is unreliable across HTTP clients.
    """

    diamond_lines = NestedDiamondLineSerializer(many=True, required=False)
    colorstone_lines = NestedColorStoneLineSerializer(many=True, required=False)
    finish_lines = NestedFinishLineSerializer(many=True, required=False)

    class Meta:
        model = CostCard
        fields = [
            'pk',
            # General
            'cost_card_no', 'our_style_no', 'vendor_style_no', 'vendor', 'customer',
            'category', 'sub_category', 'metal_purity', 'karat', 'metal_grams',
            'finding_type', 'finding_price', 'gross_weight', 'net_weight', 'troy_ounce_price',
            'height_mm', 'height_inch', 'length_mm', 'length_inch', 'width_mm', 'width_inch',
            'shank_size_mm', 'shank_size_inch', 'drape_length_mm', 'drape_length_inch',
            'design_note', 'special_note', 'remarks',
            # Images (read-only here; use the dedicated image upload endpoint to write)
            'front_view', 'side_view', 'back_view',
            # Labour Details
            'labour_finish_amount', 'labour_diamond_amount', 'labour_colorstone_amount',
            # Cost
            'metal_loss_pct', 'metal_loss_amount', 'metal_amount',
            'dia_pcs', 'dia_cts', 'dia_amount',
            'col_pcs', 'col_cts', 'col_amount',
            'stone_pcs', 'stone_cts', 'stone_amount',
            'labour_amount',
            'dia_handling_pct', 'dia_handling_amount',
            'col_handling_pct', 'col_handling_amount',
            'vendor_markup_pct', 'vendor_markup_amount',
            'fob',
            'duty_pct', 'duty_amount',
            'margin_pct', 'margin_amount',
            'final_amount',
            # Remarks (detail tab)
            'remarks_full',
            # Nested tabs
            'diamond_lines', 'colorstone_lines', 'finish_lines',
            # Common
            'active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['cost_card_no','front_view', 'side_view', 'back_view']

    def create(self, validated_data):
        diamond_lines_data = validated_data.pop('diamond_lines', [])
        colorstone_lines_data = validated_data.pop('colorstone_lines', [])
        finish_lines_data = validated_data.pop('finish_lines', [])

        cost_card = CostCard.objects.create(**validated_data)

        self._sync_lines(cost_card, CostCardDiamondLine, 'diamond_lines', diamond_lines_data)
        self._sync_lines(cost_card, CostCardColorStoneLine, 'colorstone_lines', colorstone_lines_data)
        self._sync_lines(cost_card, CostCardFinishLine, 'finish_lines', finish_lines_data)

        return cost_card

    def update(self, instance, validated_data):
        diamond_lines_data = validated_data.pop('diamond_lines', None)
        colorstone_lines_data = validated_data.pop('colorstone_lines', None)
        finish_lines_data = validated_data.pop('finish_lines', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Only touch a tab's lines if that tab's data was actually included
        # in the payload - this lets the frontend PATCH e.g. just the
        # Diamond tab without wiping Color Stone / Finish Type rows.
        if diamond_lines_data is not None:
            self._sync_lines(instance, CostCardDiamondLine, 'diamond_lines', diamond_lines_data)
        if colorstone_lines_data is not None:
            self._sync_lines(instance, CostCardColorStoneLine, 'colorstone_lines', colorstone_lines_data)
        if finish_lines_data is not None:
            self._sync_lines(instance, CostCardFinishLine, 'finish_lines', finish_lines_data)

        return instance

    @staticmethod
    def _sync_lines(cost_card, model_cls, related_name, lines_data):
        """
        Reconcile a cost card's child lines (diamond/colorstone/finish)
        against the submitted list for one tab:
          - a row with an 'id' matching an existing line -> updated in place
          - a row without an 'id' -> created new
          - an existing row whose 'id' is missing from the payload -> deleted

        This mirrors how the UI works: the tab's table is the full,
        current set of rows for that tab, rebuilt from the '+' button and
        row deletes, then submitted as-is.
        """
        existing = {obj.pk: obj for obj in getattr(cost_card, related_name).all()}
        seen_ids = set()

        for line_data in lines_data:
            line_id = line_data.pop('id', None)

            if line_id and line_id in existing:
                line_instance = existing[line_id]
                for attr, value in line_data.items():
                    setattr(line_instance, attr, value)
                line_instance.save()
                seen_ids.add(line_id)
            else:
                model_cls.objects.create(cost_card=cost_card, **line_data)

        for line_id, line_instance in existing.items():
            if line_id not in seen_ids:
                line_instance.delete()


class CostCardImageSerializer(InvenTreeModelSerializer):
    """
    Serializer for the dedicated Images tab endpoint. Handles multipart
    uploads of front_view / side_view / back_view independently of the
    main JSON create/update call.
    """

    class Meta:
        model = CostCard
        fields = ['pk', 'front_view', 'side_view', 'back_view']