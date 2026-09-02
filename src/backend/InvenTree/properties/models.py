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
    """Diamond size (in mm) and optional sieve size."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the diamond size.'))
    mm_size = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name=_('Size (mm)'), help_text=_('Diamond size in millimeters.'))
    sieve_size = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Sieve Size'), help_text=_('Sieve size corresponding to this diamond size.'))
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
    """Color stone size (in mm) and optional sieve size."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the color stone size.'))
    mm_size = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name=_('Size (mm)'), help_text=_('Color stone size in millimeters.'))
    sieve_size = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Sieve Size'), help_text=_('Sieve size corresponding to this color stone size.'))
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


class ColorStoneQuality(PropertiesFieldsMixin):
    """Color stone quality grade."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the color stone quality grade.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the color stone quality grade.'))

    class Meta:
        verbose_name = _('Color Stone Quality')
        verbose_name_plural = _('Color Stone Qualities')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class DiamondStoneRate(PropertiesFieldsMixin):
    """Weight-per-stone rate for diamonds.

    Maps to tbprice WHERE mtype = 'DIAWEIGHTPERSTONE' in jsidb.
    Combines shape, size, stone type, color, cut, quality and pointer
    to produce a per-piece or per-carat rate.
    """

    shape = models.ForeignKey(
        DiamondShape, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Shape'), help_text=_('Diamond shape.'),
    )
    mm_size = models.ForeignKey(
        DiamondSize, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Size'), help_text=_('Diamond size.'),
    )
    stone = models.ForeignKey(
        DiamondStone, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Stone'), help_text=_('Diamond stone type.'),
    )
    color = models.ForeignKey(
        DiamondColor, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Color'), help_text=_('Diamond color grade.'),
    )
    cut = models.ForeignKey(
        DiamondCut, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Cut'), help_text=_('Diamond cut type.'),
    )
    quality = models.ForeignKey(
        DiamondQuality, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Quality'), help_text=_('Diamond quality grade.'),
    )
    pointer = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        verbose_name=_('Pointer'), help_text=_('Pointer value for rate lookup.'),
    )
    rate = models.DecimalField(
        max_digits=10, decimal_places=4,
        verbose_name=_('Rate'), help_text=_('Rate per piece or per carat.'),
    )
    pc = models.CharField(
        max_length=1, choices=[('P', _('Per Piece')), ('C', _('Per Carat'))],
        default='C', verbose_name=_('P/C'),
        help_text=_('Rate unit: P = Per Piece, C = Per Carat.'),
    )
    customers = models.ManyToManyField(
        'company.Company',
        blank=True,
        related_name='diamond_stone_rates',
        limit_choices_to={'is_customer': True},
        verbose_name=_('Customers'),
        help_text=_('Customers this rate applies to. Leave empty when All Customers is selected.'),
    )
    all_customers = models.BooleanField(
        default=False,
        verbose_name=_('All Customers'),
        help_text=_('If set, this rate applies to every customer (Select All Customers).'),
    )

    class Meta:
        ordering = ['shape', 'mm_size', 'pointer']
        verbose_name = _('Diamond Stone Rate')
        verbose_name_plural = _('Diamond Stone Rates')
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['shape', 'mm_size', 'pointer']),
            models.Index(fields=['all_customers']),
        ]

    def __str__(self):
        parts = []
        if self.shape:
            parts.append(str(self.shape))
        if self.mm_size:
            parts.append(str(self.mm_size))
        if self.pointer:
            parts.append(str(self.pointer))
        return ' / '.join(parts) if parts else f'DiamondStoneRate #{self.pk}'


class ColorStoneRate(PropertiesFieldsMixin):
    """Weight-per-stone rate for color stones.

    Maps to tbprice WHERE mtype = 'COLWEIGHTPERSTONE' in jsidb.
    Combines shape, size, stone type, color, cut, quality and pointer
    to produce a per-piece or per-carat rate.
    """

    shape = models.ForeignKey(
        ColorStoneShape, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Shape'), help_text=_('Color stone shape.'),
    )
    mm_size = models.ForeignKey(
        ColorStoneSize, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Size'), help_text=_('Color stone size.'),
    )
    stone = models.ForeignKey(
        ColorStone, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Stone'), help_text=_('Color stone type.'),
    )
    color = models.ForeignKey(
        ColorStoneColor, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Color'), help_text=_('Color stone color.'),
    )
    cut = models.ForeignKey(
        ColorStoneCut, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Cut'), help_text=_('Color stone cut type.'),
    )
    quality = models.ForeignKey(
        ColorStoneQuality, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rates',
        verbose_name=_('Quality'), help_text=_('Color stone quality grade.'),
    )
    pointer = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        verbose_name=_('Pointer'), help_text=_('Pointer value for rate lookup.'),
    )
    rate = models.DecimalField(
        max_digits=10, decimal_places=4,
        verbose_name=_('Rate'), help_text=_('Rate per piece or per carat.'),
    )
    pc = models.CharField(
        max_length=1, choices=[('P', _('Per Piece')), ('C', _('Per Carat'))],
        default='C', verbose_name=_('P/C'),
        help_text=_('Rate unit: P = Per Piece, C = Per Carat.'),
    )
    customers = models.ManyToManyField(
        'company.Company',
        blank=True,
        related_name='color_stone_rates',
        limit_choices_to={'is_customer': True},
        verbose_name=_('Customers'),
        help_text=_('Customers this rate applies to. Leave empty when All Customers is selected.'),
    )
    all_customers = models.BooleanField(
        default=False,
        verbose_name=_('All Customers'),
        help_text=_('If set, this rate applies to every customer (Select All Customers).'),
    )

    class Meta:
        ordering = ['shape', 'mm_size', 'pointer']
        verbose_name = _('Color Stone Rate')
        verbose_name_plural = _('Color Stone Rates')
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['shape', 'mm_size', 'pointer']),
            models.Index(fields=['all_customers']),
        ]

    def __str__(self):
        parts = []
        if self.shape:
            parts.append(str(self.shape))
        if self.mm_size:
            parts.append(str(self.mm_size))
        if self.pointer:
            parts.append(str(self.pointer))
        return ' / '.join(parts) if parts else f'ColorStoneRate #{self.pk}'
