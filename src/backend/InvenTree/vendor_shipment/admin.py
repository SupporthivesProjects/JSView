from django.contrib import admin

from .models import VendorShipment, VendorShipmentLine


class VendorShipmentLineInline(admin.TabularInline):
    model = VendorShipmentLine
    extra = 0
    fields = [
        'poid', 'costcardid', 'pcs', 'metalwt', 'diawt', 'colwt',
        'stplace', 'labour', 'finding', 'triounce', 'confrm',
    ]


@admin.register(VendorShipment)
class VendorShipmentAdmin(admin.ModelAdmin):
    list_display = [
        'vsno', 'vsdate', 'vendorid', 'courierid', 'trackref', 'active',
    ]
    list_filter = ['active']
    search_fields = ['vsno', 'trackref']
    autocomplete_fields = ['vendorid', 'courierid']
    inlines = [VendorShipmentLineInline]


@admin.register(VendorShipmentLine)
class VendorShipmentLineAdmin(admin.ModelAdmin):
    list_display = [
        'vendorshipid', 'poid', 'costcardid', 'pcs', 'metalwt', 'diawt', 'confrm',
    ]
    list_filter = ['confrm', 'active']
    search_fields = ['poid__pono']
