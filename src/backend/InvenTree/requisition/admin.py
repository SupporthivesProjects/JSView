"""Admin class definitions for the 'requisition' app."""

from django.contrib import admin

from requisition import models


@admin.register(models.MetalSent)
class MetalSentAdmin(admin.ModelAdmin):
    """Admin class for the MetalSent model."""

    list_display = ('metal_sent_no', 'invoice_no', 'metal_sent_date', 'purchase_order', 'triounce', 'metal_gms', 'metal_amount', 'prepby', 'active', 'created_at', 'updated_at')
    search_fields = ('invoice_no', 'purchase_order__pono')
    autocomplete_fields = ('purchase_order', 'prepby')
    list_filter = ('metal_sent_date', 'active')