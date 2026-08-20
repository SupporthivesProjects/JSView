"""Admin class definitions for the 'cards' app."""

from django.contrib import admin

from cards import models


@admin.register(models.StonePlace)
class StonePlaceAdmin(admin.ModelAdmin):
    """Admin class for the StonePlace model."""

    list_display = ('name', 'description', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('active',)


class CostCardDiamondLineInline(admin.TabularInline):
    """Inline admin for CostCardDiamondLine rows on a CostCard."""

    model = models.CostCardDiamondLine
    extra = 0
    autocomplete_fields = ('stone', 'shape', 'mm_size', 'color', 'cut', 'quality', 'setting', 'stone_place')


class CostCardColorStoneLineInline(admin.TabularInline):
    """Inline admin for CostCardColorStoneLine rows on a CostCard."""

    model = models.CostCardColorStoneLine
    extra = 0
    autocomplete_fields = ('stone', 'shape', 'mm_size', 'color', 'cut', 'quality', 'setting', 'stone_place')


class CostCardFinishLineInline(admin.TabularInline):
    """Inline admin for CostCardFinishLine rows on a CostCard."""

    model = models.CostCardFinishLine
    extra = 0
    autocomplete_fields = ('finish_type',)


@admin.register(models.CostCard)
class CostCardAdmin(admin.ModelAdmin):
    """Admin class for the CostCard model."""

    list_display = (
        'cost_card_no', 'our_style_no', 'vendor', 'customer', 'category',
        'sub_category', 'final_amount', 'active', 'created_at', 'updated_at',
    )
    search_fields = ('cost_card_no', 'our_style_no', 'vendor_style_no')
    autocomplete_fields = ('vendor', 'customer', 'category', 'sub_category', 'metal_purity', 'finding_type')
    list_filter = ('active', 'category', 'sub_category')
    inlines = [CostCardDiamondLineInline, CostCardColorStoneLineInline, CostCardFinishLineInline]


@admin.register(models.CostCardDiamondLine)
class CostCardDiamondLineAdmin(admin.ModelAdmin):
    """Admin class for the CostCardDiamondLine model."""

    list_display = ('cost_card', 'stone', 'shape', 'pcs', 'cts', 'rate', 'amount', 'active', 'created_at')
    search_fields = ('cost_card__cost_card_no', 'cost_card__our_style_no')
    autocomplete_fields = ('cost_card', 'stone', 'shape', 'mm_size', 'color', 'cut', 'quality', 'setting', 'stone_place', 'rate_source')
    list_filter = ('active', 'shape', 'quality')


@admin.register(models.CostCardColorStoneLine)
class CostCardColorStoneLineAdmin(admin.ModelAdmin):
    """Admin class for the CostCardColorStoneLine model."""

    list_display = ('cost_card', 'stone', 'shape', 'pcs', 'cts', 'rate', 'amount', 'active', 'created_at')
    search_fields = ('cost_card__cost_card_no', 'cost_card__our_style_no')
    autocomplete_fields = ('cost_card', 'stone', 'shape', 'mm_size', 'color', 'cut', 'quality', 'setting', 'stone_place', 'rate_source')
    list_filter = ('active', 'shape', 'quality')


@admin.register(models.CostCardFinishLine)
class CostCardFinishLineAdmin(admin.ModelAdmin):
    """Admin class for the CostCardFinishLine model."""

    list_display = ('cost_card', 'finish_type', 'rate', 'active', 'created_at', 'updated_at')
    search_fields = ('cost_card__cost_card_no', 'finish_type__name')
    autocomplete_fields = ('cost_card', 'finish_type')
    list_filter = ('active', 'finish_type')