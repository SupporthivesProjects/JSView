from django.contrib import admin

from .models import PurchaseOrder, PurchaseOrderLine


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
