"""Admin class definitions for the 'master' app."""

from django.contrib import admin

from master import models


@admin.register(models.MetalType)
class MetalTypeAdmin(admin.ModelAdmin):
    """Admin class for the MetalType model."""

    list_display = ('name', 'description', 'active')
    search_fields = ('name', 'description')


@admin.register(models.MetalPurity)
class MetalPurityAdmin(admin.ModelAdmin):
    """Admin class for the MetalPurity model."""

    list_display = ('metal_type', 'name', 'fineness', 'active')
    search_fields = ('name',)
    autocomplete_fields = ('metal_type',)


@admin.register(models.Setting)
class SettingAdmin(admin.ModelAdmin):
    """Admin class for the Setting model."""

    list_display = ('name', 'description', 'active')
    search_fields = ('name', 'description')


@admin.register(models.LabourSetting)
class LabourSettingAdmin(admin.ModelAdmin):
    """Admin class for the LabourSetting model."""

    list_display = ('name', 'setting', 'charge_type', 'rate', 'active')
    search_fields = ('name',)
    autocomplete_fields = ('setting',)


@admin.register(models.MetalRate)
class MetalRateAdmin(admin.ModelAdmin):
    """Admin class for the MetalRate model."""

    list_display = ('metal_type', 'purity', 'date', 'rate', 'active')
    autocomplete_fields = ('metal_type', 'purity')


@admin.register(models.FindingType)
class FindingTypeAdmin(admin.ModelAdmin):
    """Admin class for the FindingType model."""

    list_display = ('name', 'description', 'active')
    search_fields = ('name', 'description')


@admin.register(models.FinishType)
class FinishTypeAdmin(admin.ModelAdmin):
    """Admin class for the FinishType model."""

    list_display = ('name', 'description', 'active')
    search_fields = ('name', 'description')


@admin.register(models.Duty)
class DutyAdmin(admin.ModelAdmin):
    """Admin class for the Duty model."""

    list_display = ('name', 'percentage', 'active')
    search_fields = ('name', 'description')


@admin.register(models.Stamp)
class StampAdmin(admin.ModelAdmin):
    """Admin class for the Stamp model."""

    list_display = ('name', 'description', 'active')
    search_fields = ('name', 'description')


@admin.register(models.ACExecutive)
class ACExecutiveAdmin(admin.ModelAdmin):
    """Admin class for the ACExecutive model."""

    list_display = ('name', 'code', 'email', 'phone', 'active')
    search_fields = ('name', 'code', 'email')
    autocomplete_fields = ('user',)


@admin.register(models.Terms)
class TermsAdmin(admin.ModelAdmin):
    """Admin class for the Terms model."""

    list_display = ('name', 'days', 'active')
    search_fields = ('name', 'description')


@admin.register(models.CourierService)
class CourierServiceAdmin(admin.ModelAdmin):
    """Admin class for the CourierService model."""

    list_display = ('name', 'contact_person', 'phone', 'email', 'active')
    search_fields = ('name', 'contact_person')


@admin.register(models.POMail)
class POMailAdmin(admin.ModelAdmin):
    """Admin class for the POMail model."""

    list_display = ('name', 'vendor', 'email', 'active')
    search_fields = ('name', 'email')
    autocomplete_fields = ('vendor',)