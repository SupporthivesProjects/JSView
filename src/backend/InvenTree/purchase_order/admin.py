from django.contrib import admin

from .models import (
    POCostCard,
    POCostCardLine,
    PurchaseOrder,
    PurchaseOrderLine,
)


class PurchaseOrderLineInline(admin.TabularInline):
    model = PurchaseOrderLine
    extra = 0
    fields = ['costcardid', 'styleno', 'vstyleno', 'vendorid', 'qty', 'size', 'spcs']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = [
        'pono', 'potype', 'pocategory', 'podate',
        'customerid', 'vendorid', 'tqty', 'active',
    ]
    list_filter = ['potype', 'pocategory', 'active']
    search_fields = ['pono', 'customer_pono']
    inlines = [PurchaseOrderLineInline]


@admin.register(PurchaseOrderLine)
class PurchaseOrderLineAdmin(admin.ModelAdmin):
    list_display = [
        'poid', 'costcardid', 'styleno', 'vstyleno', 'qty',
    ]
    list_filter = ['active']
    search_fields = ['styleno', 'vstyleno']


class POCostCardLineInline(admin.TabularInline):
    model = POCostCardLine
    extra = 0
    fields = ['etype', 'stone', 'shape', 'pcs', 'cts', 'rate', 'amount']


@admin.register(POCostCard)
class POCostCardAdmin(admin.ModelAdmin):
    list_display = [
        'poid', 'costcardno', 'our_style_no',
        'vendor', 'final_amount', 'active',
    ]
    list_filter = ['active']
    inlines = [POCostCardLineInline]


@admin.register(POCostCardLine)
class POCostCardLineAdmin(admin.ModelAdmin):
    list_display = [
        'po_costcard', 'etype', 'stone',
        'shape', 'pcs', 'cts', 'rate', 'amount',
    ]
    list_filter = ['etype', 'active']
