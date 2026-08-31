from django.db import transaction

from rest_framework import serializers as drf_serializers

from InvenTree.serializers import InvenTreeModelSerializer

from data_exporter.mixins import DataExportSerializerMixin
from importer.registry import register_importer

from .models import (
    CostCard,
    CostCardColorStoneLine,
    CostCardDiamondLine,
    CostCardFinishLine,
    StonePlace,
)


@register_importer()
class StonePlaceSerializer(
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = StonePlace
        fields = [
            'pk',
            'name',
            'description',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class CostCardDiamondLineSerializer(
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = CostCardDiamondLine
        fields = [
            'pk',
            'cost_card',
            'stone',
            'shape',
            'mm_size',
            'color',
            'cut',
            'quality',
            'setting',
            'stone_place',
            'rate_source',
            'pointer',
            'sieve_size',
            'pcs',
            'cts',
            'default_rate',
            'pc',
            'rate',
            'amount',
            'labour_rate',
            'labour_amount',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class CostCardColorStoneLineSerializer(
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = CostCardColorStoneLine
        fields = [
            'pk',
            'cost_card',
            'stone',
            'shape',
            'mm_size',
            'color',
            'cut',
            'quality',
            'setting',
            'stone_place',
            'rate_source',
            'pointer',
            'sieve_size',
            'pcs',
            'cts',
            'default_rate',
            'pc',
            'rate',
            'amount',
            'labour_rate',
            'labour_amount',
            'active',
            'created_at',
            'updated_at',
        ]


@register_importer()
class CostCardFinishLineSerializer(
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    class Meta:
        model = CostCardFinishLine
        fields = [
            'pk',
            'cost_card',
            'finish_type',
            'rate',
            'active',
            'created_at',
            'updated_at',
        ]


class NestedDiamondLineSerializer(drf_serializers.ModelSerializer):
    id = drf_serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CostCardDiamondLine
        fields = [
            'id',
            'stone',
            'shape',
            'mm_size',
            'color',
            'cut',
            'quality',
            'setting',
            'stone_place',
            'rate_source',
            'pointer',
            'sieve_size',
            'pcs',
            'cts',
            'default_rate',
            'pc',
            'rate',
            'amount',
            'labour_rate',
            'labour_amount',
            'active',
        ]


class NestedColorStoneLineSerializer(drf_serializers.ModelSerializer):
    id = drf_serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CostCardColorStoneLine
        fields = [
            'id',
            'stone',
            'shape',
            'mm_size',
            'color',
            'cut',
            'quality',
            'setting',
            'stone_place',
            'rate_source',
            'pointer',
            'sieve_size',
            'pcs',
            'cts',
            'default_rate',
            'pc',
            'rate',
            'amount',
            'labour_rate',
            'labour_amount',
            'active',
        ]


class NestedFinishLineSerializer(drf_serializers.ModelSerializer):
    id = drf_serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CostCardFinishLine
        fields = [
            'id',
            'finish_type',
            'rate',
            'active',
        ]


@register_importer()
class CostCardSerializer(
    DataExportSerializerMixin,
    InvenTreeModelSerializer,
):
    diamond_lines = NestedDiamondLineSerializer(
        many=True,
        required=False,
    )

    colorstone_lines = NestedColorStoneLineSerializer(
        many=True,
        required=False,
    )

    finish_lines = NestedFinishLineSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = CostCard
        fields = [
            'pk',
            'cost_card_no',
            'our_style_no',
            'vendor_style_no',
            'vendor',
            'customer',
            'category',
            'sub_category',
            'metal_purity',
            'karat',
            'metal_grams',
            'finding_type',
            'finding_price',
            'gross_weight',
            'net_weight',
            'troy_ounce_price',
            'height_mm',
            'height_inch',
            'length_mm',
            'length_inch',
            'width_mm',
            'width_inch',
            'shank_size_mm',
            'shank_size_inch',
            'drape_length_mm',
            'drape_length_inch',
            'design_note',
            'special_note',
            'remarks',
            'front_view',
            'side_view',
            'back_view',
            'labour_finish_amount',
            'labour_diamond_amount',
            'labour_colorstone_amount',
            'metal_loss_pct',
            'metal_loss_amount',
            'metal_amount',
            'dia_pcs',
            'dia_cts',
            'dia_amount',
            'col_pcs',
            'col_cts',
            'col_amount',
            'stone_pcs',
            'stone_cts',
            'stone_amount',
            'labour_amount',
            'dia_handling_pct',
            'dia_handling_amount',
            'col_handling_pct',
            'col_handling_amount',
            'vendor_markup_pct',
            'vendor_markup_amount',
            'fob',
            'duty_pct',
            'duty_amount',
            'margin_pct',
            'margin_amount',
            'final_amount',
            'remarks_full',
            'diamond_lines',
            'colorstone_lines',
            'finish_lines',
            'active',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'pk',
            'cost_card_no',
            'front_view',
            'side_view',
            'back_view',
            'created_at',
            'updated_at',
        ]

    @transaction.atomic
    def create(self, validated_data):
        diamond_lines = validated_data.pop('diamond_lines', None)
        colorstone_lines = validated_data.pop('colorstone_lines', None)
        finish_lines = validated_data.pop('finish_lines', None)

        cost_card = CostCard.objects.create(**validated_data)

        if diamond_lines is not None:
            self._sync_lines(
                cost_card,
                CostCardDiamondLine,
                'diamond_lines',
                diamond_lines,
                False,
            )

        if colorstone_lines is not None:
            self._sync_lines(
                cost_card,
                CostCardColorStoneLine,
                'colorstone_lines',
                colorstone_lines,
                False,
            )

        if finish_lines is not None:
            self._sync_lines(
                cost_card,
                CostCardFinishLine,
                'finish_lines',
                finish_lines,
                False,
            )

        return cost_card

    @transaction.atomic
    def update(self, instance, validated_data):
        diamond_lines = validated_data.pop('diamond_lines', None)
        colorstone_lines = validated_data.pop('colorstone_lines', None)
        finish_lines = validated_data.pop('finish_lines', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if diamond_lines is not None:
            self._sync_lines(
                instance,
                CostCardDiamondLine,
                'diamond_lines',
                diamond_lines,
                True,
            )

        if colorstone_lines is not None:
            self._sync_lines(
                instance,
                CostCardColorStoneLine,
                'colorstone_lines',
                colorstone_lines,
                True,
            )

        if finish_lines is not None:
            self._sync_lines(
                instance,
                CostCardFinishLine,
                'finish_lines',
                finish_lines,
                True,
            )

        return instance

    @staticmethod
    def _sync_lines(
        cost_card,
        model_cls,
        related_name,
        lines_data,
        allow_delete,
    ):
        existing = {
            obj.pk: obj
            for obj in getattr(
                cost_card,
                related_name,
            ).all()
        }

        seen_ids = set()

        for raw_data in lines_data:
            data = dict(raw_data)

            line_id = data.pop('id', None)
            data.pop('cost_card', None)

            if line_id is not None:
                line_instance = existing.get(line_id)

                if line_instance is None:
                    raise drf_serializers.ValidationError(
                        {
                            'id': (
                                f'{model_cls.__name__} with id '
                                f'{line_id} does not belong to '
                                f'CostCard {cost_card.pk}.'
                            )
                        }
                    )

                for attr, value in data.items():
                    setattr(line_instance, attr, value)

                line_instance.cost_card = cost_card
                line_instance.save()
                seen_ids.add(line_id)

            else:
                model_cls.objects.create(
                    cost_card=cost_card,
                    **data,
                )

        if allow_delete:
            for line_id, line_instance in existing.items():
                if line_id not in seen_ids:
                    line_instance.delete()


class CostCardImageSerializer(InvenTreeModelSerializer):
    class Meta:
        model = CostCard
        fields = [
            'pk',
            'front_view',
            'side_view',
            'back_view',
        ]