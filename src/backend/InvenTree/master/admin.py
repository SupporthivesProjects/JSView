"""Admin class definitions for the 'master' app."""

from django.contrib import admin

from master import models


@admin.register(models.MetalType)
class MetalTypeAdmin(admin.ModelAdmin):
    """Admin class for the MetalType model."""

    list_display = ('name', 'code', 'description', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('active',)


@admin.register(models.MetalPurity)
class MetalPurityAdmin(admin.ModelAdmin):
    """Admin class for the MetalPurity model."""

    list_display = ('metal_type', 'name', 'purity', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'metal_type__name')
    autocomplete_fields = ('metal_type',)
    list_filter = ('active',)


@admin.register(models.Setting)
class SettingAdmin(admin.ModelAdmin):
    """Admin class for the Setting model."""

    list_display = ('name', 'description', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('active',)


@admin.register(models.LabourSetting)
class LabourSettingAdmin(admin.ModelAdmin):
    """Admin class for the LabourSetting model."""

    list_display = ('name', 'setting', 'charge_type', 'rate', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'setting__name')
    autocomplete_fields = ('setting',)
    list_filter = ('charge_type', 'active')


@admin.register(models.MetalRate)
class MetalRateAdmin(admin.ModelAdmin):
    """Admin class for the MetalRate model."""

    list_display = ('metal_type', 'date', 'rate', 'active', 'created_at', 'updated_at')
    search_fields = ('metal_type__name',)
    autocomplete_fields = ('metal_type',)
    list_filter = ('date', 'active')


@admin.register(models.FindingType)
class FindingTypeAdmin(admin.ModelAdmin):
    """Admin class for the FindingType model."""

    list_display = ('name', 'type', 'weight', 'metal', 'price', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'type', 'metal', 'description')
    list_filter = ('type', 'active')


@admin.register(models.FinishType)
class FinishTypeAdmin(admin.ModelAdmin):
    """Admin class for the FinishType model."""

    list_display = ('name', 'description', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('active',)


@admin.register(models.Duty)
class DutyAdmin(admin.ModelAdmin):
    """Admin class for the Duty model."""

    list_display = ('metal_type', 'duty', 'markup', 'active', 'created_at', 'updated_at')
    search_fields = ('metal_type__name', 'description')
    autocomplete_fields = ('metal_type',)
    list_filter = ('active',)


@admin.register(models.Stamp)
class StampAdmin(admin.ModelAdmin):
    """Admin class for the Stamp model."""

    list_display = ('name', 'description', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'customers__name')
    filter_horizontal = ('customers',)
    list_filter = ('active',)


@admin.register(models.ACExecutive)
class ACExecutiveAdmin(admin.ModelAdmin):
    """Admin class for the ACExecutive model."""

    list_display = ('name', 'code', 'email', 'phone', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'code', 'email', 'phone')
    list_filter = ('active',)


@admin.register(models.Terms)
class TermsAdmin(admin.ModelAdmin):
    """Admin class for the Terms model."""

    list_display = ('name', 'days', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'vendors__name')
    filter_horizontal = ('vendors',)
    list_filter = ('active',)


@admin.register(models.CourierService)
class CourierServiceAdmin(admin.ModelAdmin):
    """Admin class for the CourierService model."""

    list_display = ('name', 'contact_person', 'phone', 'email', 'tracking_url', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'contact_person', 'phone', 'email')
    list_filter = ('active',)


@admin.register(models.JewelryCategory)
class JewelryCategoryAdmin(admin.ModelAdmin):
    """Admin class for the JewelryCategory model."""

    list_display = ('name', 'description', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('active',)


@admin.register(models.JewelrySubCategory)
class JewelrySubCategoryAdmin(admin.ModelAdmin):
    """Admin class for the JewelrySubCategory model."""

    list_display = ('name', 'category', 'description', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'category__name')
    autocomplete_fields = ('category',)
    list_filter = ('active',)


@admin.register(models.Templates)
class TemplatesAdmin(admin.ModelAdmin):
    """Admin class for the Templates model."""

    list_display = ('name', 'subject', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'subject')
    list_filter = ('active',)


@admin.register(models.POMail)
class POMailAdmin(admin.ModelAdmin):
    """Admin class for the POMail model."""

    list_display = ('name', 'order', 'format1', 'format2', 'format3', 'format4', 'active', 'created_at', 'updated_at')
    search_fields = ('name',)
    autocomplete_fields = ('format1', 'format2', 'format3', 'format4')
    list_filter = ('active',)