"""Admin class definitions for the 'properties' app."""

from django.contrib import admin

from . import models


@admin.register(models.DiamondStone)
class DiamondStoneAdmin(admin.ModelAdmin):
    """Admin class for the DiamondStone model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(models.DiamondCut)
class DiamondCutAdmin(admin.ModelAdmin):
    """Admin class for the DiamondCut model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(models.DiamondShape)
class DiamondShapeAdmin(admin.ModelAdmin):
    """Admin class for the DiamondShape model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(models.DiamondColor)
class DiamondColorAdmin(admin.ModelAdmin):
    """Admin class for the DiamondColor model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(models.DiamondSize)
class DiamondSizeAdmin(admin.ModelAdmin):
    """Admin class for the DiamondSize model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(models.DiamondQuality)
class DiamondQualityAdmin(admin.ModelAdmin):
    """Admin class for the DiamondQuality model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(models.ColorStone)
class ColorStoneAdmin(admin.ModelAdmin):
    """Admin class for the ColorStone model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(models.ColorStoneCut)
class ColorStoneCutAdmin(admin.ModelAdmin):
    """Admin class for the ColorStoneCut model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(models.ColorStoneShape)
class ColorStoneShapeAdmin(admin.ModelAdmin):
    """Admin class for the ColorStoneShape model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(models.ColorStoneColor)
class ColorStoneColorAdmin(admin.ModelAdmin):
    """Admin class for the ColorStoneColor model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)


@admin.register(models.ColorStoneSize)
class ColorStoneSizeAdmin(admin.ModelAdmin):
    """Admin class for the ColorStoneSize model."""

    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)
    list_filter = ('active',)
