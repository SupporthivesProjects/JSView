"""Models for the 'properties' app — diamond and color stone property tables.

These mirror the client's tbmaster lookup values:
- DIASTONE, DIACUT, DIASHAPE, DIACOLOR, DIASIZE, DIAQUALITY -> Diamond models
- COL* variants                                         -> ColorStone models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class PropertiesFieldsMixin(models.Model):
    """Common fields for properties tables (mirrors master.MasterFieldsMixin)."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'), help_text=_('Date and time when this record was created.'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'), help_text=_('Date and time when this record was last updated.'))
    active = models.BooleanField(default=True, verbose_name=_('Active'), help_text=_('Whether this record is currently active.'))

    class Meta:
        abstract = True


class DiamondStone(PropertiesFieldsMixin):
    """Diamond stone type (e.g. Natural, Lab Grown)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the diamond stone type.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the diamond stone type.'))

    class Meta:
        verbose_name = _('Diamond Stone')
        verbose_name_plural = _('Diamond Stones')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class DiamondCut(PropertiesFieldsMixin):
    """Diamond cut type (e.g. Round Brilliant, Princess)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the diamond cut type.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the diamond cut type.'))

    class Meta:
        verbose_name = _('Diamond Cut')
        verbose_name_plural = _('Diamond Cuts')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class DiamondShape(PropertiesFieldsMixin):
    """Diamond shape (e.g. Round, Pear, Emerald)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the diamond shape.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the diamond shape.'))

    class Meta:
        verbose_name = _('Diamond Shape')
        verbose_name_plural = _('Diamond Shapes')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class DiamondColor(PropertiesFieldsMixin):
    """Diamond color grade (e.g. D, E, F)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the diamond color grade.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the diamond color grade.'))

    class Meta:
        verbose_name = _('Diamond Color')
        verbose_name_plural = _('Diamond Colors')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class DiamondSize(PropertiesFieldsMixin):
    """Diamond size (in mm)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the diamond size.'))
    mm_size = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name=_('Size (mm)'), help_text=_('Diamond size in millimeters.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the diamond size.'))

    class Meta:
        verbose_name = _('Diamond Size')
        verbose_name_plural = _('Diamond Sizes')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class DiamondQuality(PropertiesFieldsMixin):
    """Diamond quality grade (e.g. VVS1, VS1, SI1)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the diamond quality grade.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the diamond quality grade.'))

    class Meta:
        verbose_name = _('Diamond Quality')
        verbose_name_plural = _('Diamond Qualities')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class ColorStone(PropertiesFieldsMixin):
    """Color stone type (e.g. Ruby, Sapphire, Emerald)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the color stone type.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the color stone type.'))

    class Meta:
        verbose_name = _('Color Stone')
        verbose_name_plural = _('Color Stones')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class ColorStoneCut(PropertiesFieldsMixin):
    """Color stone cut type."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the color stone cut type.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the color stone cut type.'))

    class Meta:
        verbose_name = _('Color Stone Cut')
        verbose_name_plural = _('Color Stone Cuts')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class ColorStoneShape(PropertiesFieldsMixin):
    """Color stone shape."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the color stone shape.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the color stone shape.'))

    class Meta:
        verbose_name = _('Color Stone Shape')
        verbose_name_plural = _('Color Stone Shapes')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class ColorStoneColor(PropertiesFieldsMixin):
    """Color stone color (e.g. Red, Blue, Green)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the color stone color.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the color stone color.'))

    class Meta:
        verbose_name = _('Color Stone Color')
        verbose_name_plural = _('Color Stone Colors')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class ColorStoneSize(PropertiesFieldsMixin):
    """Color stone size (in mm)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the color stone size.'))
    mm_size = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name=_('Size (mm)'), help_text=_('Color stone size in millimeters.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the color stone size.'))

    class Meta:
        verbose_name = _('Color Stone Size')
        verbose_name_plural = _('Color Stone Sizes')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name
