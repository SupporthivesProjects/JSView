"""Admin class definitions for the 'requisition' app."""

from django.contrib import admin

from requisition import models


@admin.register(models.FluteEntry)
class FluteEntryAdmin(admin.ModelAdmin):
    """Admin class for the FluteEntry model."""

    list_display = (
        'invoice_no',
        'flute_date',
        'prepby',
        'active',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'invoice_no',
        'prepby__username',
    )
    autocomplete_fields = (
        'prepby',
    )
    list_filter = (
        'flute_date',
        'active',
    )


@admin.register(models.FluteEntryLine)
class FluteEntryLineAdmin(admin.ModelAdmin):
    """Admin class for the FluteEntryLine model."""

    list_display = (
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
    )
    search_fields = (
        'flute_entry__invoice_no',
        'purchase_order__pono',
        'cost_card__our_style_no',
    )
    autocomplete_fields = (
        'flute_entry',
        'purchase_order',
        'cost_card',
        'stone_place',
    )
    list_filter = (
        'stone_type',
        'active',
    )


@admin.register(models.MetalSent)
class MetalSentAdmin(admin.ModelAdmin):
    """Admin class for the MetalSent model."""

    list_display = (
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
    )
    search_fields = (
        'invoice_no',
        'purchase_order__pono',
    )
    autocomplete_fields = (
        'purchase_order',
        'prepby',
    )
    list_filter = (
        'metal_sent_date',
        'active',
    )