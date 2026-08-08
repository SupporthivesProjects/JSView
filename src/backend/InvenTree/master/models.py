from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from company.models import Company


class MetalType(models.Model):
    """Metal type (e.g. Gold, Silver, Platinum)."""

    class Meta:
        verbose_name = _('Metal Type')
        verbose_name_plural = _('Metal Types')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    description = models.CharField(max_length=250, blank=True, verbose_name=_('Description'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class MetalPurity(models.Model):
    """Purity / fineness grade for a MetalType."""

    class Meta:
        verbose_name = _('Metal Purity')
        verbose_name_plural = _('Metal Purities')
        ordering = ['metal_type', 'name']
        constraints = [
            models.UniqueConstraint(fields=['metal_type', 'name'], name='unique_metal_type_purity_name')
        ]

    def __str__(self):
        return f'{self.metal_type.name} - {self.name}'

    metal_type = models.ForeignKey(MetalType, on_delete=models.CASCADE, related_name='purities', verbose_name=_('Metal Type'))
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    fineness = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_('Fineness (%)'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class Setting(models.Model):
    """Stone-setting style (e.g. Prong, Bezel, Pave)."""

    class Meta:
        verbose_name = _('Setting')
        verbose_name_plural = _('Settings')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    description = models.CharField(max_length=250, blank=True, verbose_name=_('Description'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class LabourSetting(models.Model):
    """Labour charge rule, optionally tied to a Setting."""

    CHARGE_TYPE_FIXED = 'fixed'
    CHARGE_TYPE_PER_GRAM = 'per_gram'
    CHARGE_TYPE_PER_PIECE = 'per_piece'
    CHARGE_TYPE_PERCENTAGE = 'percentage'

    CHARGE_TYPE_CHOICES = [
        (CHARGE_TYPE_FIXED, _('Fixed')),
        (CHARGE_TYPE_PER_GRAM, _('Per Gram')),
        (CHARGE_TYPE_PER_PIECE, _('Per Piece')),
        (CHARGE_TYPE_PERCENTAGE, _('Percentage')),
    ]

    class Meta:
        verbose_name = _('Labour Setting')
        verbose_name_plural = _('Labour Settings')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    setting = models.ForeignKey(Setting, on_delete=models.SET_NULL, related_name='labour_settings', null=True, blank=True, verbose_name=_('Setting'))
    charge_type = models.CharField(max_length=20, choices=CHARGE_TYPE_CHOICES, default=CHARGE_TYPE_FIXED, verbose_name=_('Charge Type'))
    rate = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0'), validators=[MinValueValidator(0)], verbose_name=_('Rate'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class MetalRate(models.Model):
    """Dated metal rate for a MetalType / MetalPurity."""

    class Meta:
        verbose_name = _('Metal Rate')
        verbose_name_plural = _('Metal Rates')
        ordering = ['-date', 'metal_type']
        constraints = [
            models.UniqueConstraint(fields=['metal_type', 'purity', 'date'], name='unique_metal_rate_per_day')
        ]

    def __str__(self):
        return f'{self.metal_type.name} ({self.purity.name}) @ {self.date}'

    metal_type = models.ForeignKey(MetalType, on_delete=models.CASCADE, related_name='rates', verbose_name=_('Metal Type'))
    purity = models.ForeignKey(MetalPurity, on_delete=models.CASCADE, related_name='rates', verbose_name=_('Metal Purity'))
    date = models.DateField(verbose_name=_('Date'))
    rate = models.DecimalField(max_digits=15, decimal_places=4, validators=[MinValueValidator(0)], verbose_name=_('Rate'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class FindingType(models.Model):
    """Jewelry finding type (e.g. Clasp, Hook, Jump Ring)."""

    class Meta:
        verbose_name = _('Finding Type')
        verbose_name_plural = _('Finding Types')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    description = models.CharField(max_length=250, blank=True, verbose_name=_('Description'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class FinishType(models.Model):
    """Surface finish type (e.g. Matte, Glossy, Antique)."""

    class Meta:
        verbose_name = _('Finish Type')
        verbose_name_plural = _('Finish Types')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    description = models.CharField(max_length=250, blank=True, verbose_name=_('Description'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class Duty(models.Model):
    """Import / export duty rate."""

    class Meta:
        verbose_name = _('Duty')
        verbose_name_plural = _('Duties')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.percentage}%)'

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    percentage = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal('0'), validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_('Percentage'))
    description = models.CharField(max_length=250, blank=True, verbose_name=_('Description'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class Stamp(models.Model):
    """Hallmark / stamp type (e.g. BIS Hallmark, 916)."""

    class Meta:
        verbose_name = _('Stamp')
        verbose_name_plural = _('Stamps')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    description = models.CharField(max_length=250, blank=True, verbose_name=_('Description'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class ACExecutive(models.Model):
    """Accounts executive responsible for customer/vendor accounts."""

    class Meta:
        verbose_name = _('A/C Executive')
        verbose_name_plural = _('A/C Executives')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    code = models.CharField(max_length=50, blank=True, verbose_name=_('Code'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ac_executive_profiles', verbose_name=_('User'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    phone = models.CharField(max_length=50, blank=True, verbose_name=_('Phone'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class Terms(models.Model):
    """Payment terms (e.g. Net 30)."""

    class Meta:
        verbose_name = _('Terms')
        verbose_name_plural = _('Terms')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    days = models.PositiveIntegerField(default=0, verbose_name=_('Days'))
    description = models.CharField(max_length=250, blank=True, verbose_name=_('Description'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class CourierService(models.Model):
    """Courier / shipping service provider."""

    class Meta:
        verbose_name = _('Courier Service')
        verbose_name_plural = _('Courier Services')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    contact_person = models.CharField(max_length=100, blank=True, verbose_name=_('Contact Person'))
    phone = models.CharField(max_length=50, blank=True, verbose_name=_('Phone'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    tracking_url = models.URLField(max_length=500, blank=True, verbose_name=_('Tracking URL'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))


class POMail(models.Model):
    """Saved mail config/recipient for sending Purchase Orders."""

    class Meta:
        verbose_name = _('P.O. Mail')
        verbose_name_plural = _('P.O. Mails')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    vendor = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='po_mail_entries', null=True, blank=True, limit_choices_to={'is_supplier': True}, verbose_name=_('Vendor'))
    email = models.EmailField(verbose_name=_('Email'))
    description = models.CharField(max_length=250, blank=True, verbose_name=_('Description'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))