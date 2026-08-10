from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from company.models import Company


def stamp_image(instance, filename):
    return f"stamps/{instance.pk or 'new'}/{filename}"


class MasterFieldsMixin(models.Model):
    """Common fields for master tables."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'), help_text=_('Date and time when this record was created.'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'), help_text=_('Date and time when this record was last updated.'))
    active = models.BooleanField(default=True, verbose_name=_('Active'), help_text=_('Whether this record is currently active.'))

    class Meta:
        abstract = True


class MetalType(MasterFieldsMixin):
    """Metal type (e.g. Gold, Silver, Platinum)."""

    code = models.CharField(max_length=100, unique=True, null=True, verbose_name=_('Code'), help_text=_('Unique code used to identify the metal type.'))
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the metal type.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the metal type.'))

    class Meta:
        verbose_name = _('Metal Type')
        verbose_name_plural = _('Metal Types')
        ordering = ['name']

    def __str__(self):
        return self.name


class MetalPurity(MasterFieldsMixin):
    """Purity / fineness grade for a MetalType."""

    name = models.CharField(max_length=50, verbose_name=_('Name'), help_text=_('Name of the metal purity grade.'))
    metal_type = models.ForeignKey(MetalType, on_delete=models.CASCADE, related_name='purities', verbose_name=_('Metal Type'), help_text=_('Metal type associated with this purity grade.'))
    purity = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_('Purity (%)'), help_text=_('Purity percentage of the metal, from 0 to 100.'))

    class Meta:
        verbose_name = _('Metal Purity')
        verbose_name_plural = _('Metal Purities')
        ordering = ['metal_type', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['metal_type', 'name'],
                name='unique_metal_type_purity_name'
            )
        ]

    def __str__(self):
        return f'{self.metal_type.name} - {self.name}'


class MetalRate(MasterFieldsMixin):
    """Dated metal rate for a MetalType / MetalPurity."""

    metal_type = models.ForeignKey(MetalType, on_delete=models.CASCADE, related_name='rates', verbose_name=_('Metal Type'), help_text=_('Metal type for which this rate applies.'))
    rate = models.DecimalField(max_digits=15, decimal_places=4, validators=[MinValueValidator(0)], verbose_name=_('Rate'), help_text=_('Metal rate applicable for the selected date.'))
    date = models.DateField(verbose_name=_('Date'), help_text=_('Date on which this metal rate is applicable.'))

    class Meta:
        verbose_name = _('Metal Rate')
        verbose_name_plural = _('Metal Rates')
        ordering = ['-date', 'metal_type']
        constraints = [
            models.UniqueConstraint(
                fields=['metal_type', 'date'],
                name='unique_metal_rate_per_day'
            )
        ]

    def __str__(self):
        return f'{self.metal_type.name} @ {self.date}'


class FindingType(MasterFieldsMixin):
    """Jewelry finding type (e.g. Clasp, Hook, Jump Ring)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the jewelry finding type.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the finding type.'))

    class Meta:
        verbose_name = _('Finding Type')
        verbose_name_plural = _('Finding Types')
        ordering = ['name']

    def __str__(self):
        return self.name


class FinishType(MasterFieldsMixin):
    """Surface finish type (e.g. Matte, Glossy, Antique)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the surface finish type.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the finish type.'))

    class Meta:
        verbose_name = _('Finish Type')
        verbose_name_plural = _('Finish Types')
        ordering = ['name']

    def __str__(self):
        return self.name


class Duty(MasterFieldsMixin):
    """Import / export duty rate."""

    # metal_type = models.ForeignKey(MetalType, on_delete=models.CASCADE, related_name='duties', verbose_name=_('Metal Type'), help_text=_('Metal type for which this duty applies.'), null=True, blank=True)
    metal_type = models.ForeignKey(MetalType, on_delete=models.CASCADE, related_name='duties', verbose_name=_('Metal Type'), help_text=_('Metal type for which this duty applies.'))
    duty = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_('Duty'), help_text=_('Duty percentage applicable to the selected metal type.'))
    markup = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_('Markup'), help_text=_('Markup value applicable to the selected metal type.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the duty configuration.'))

    class Meta:
        verbose_name = _('Duty')
        verbose_name_plural = _('Duties')
        ordering = ['metal_type']

    def __str__(self):
        # return f'{self.metal_type.name if self.metal_type else "No Metal Type"} - {self.duty}%'
        return f'{self.metal_type.name} - {self.duty}%'


class Stamp(MasterFieldsMixin):
    """Hallmark / stamp type (e.g. BIS Hallmark, 916)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the hallmark or stamp.'))
    image = models.ImageField(upload_to=stamp_image, verbose_name=_('Image'), help_text=_('Image representing the hallmark or stamp.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the stamp.'))

    class Meta:
        verbose_name = _('Stamp')
        verbose_name_plural = _('Stamps')
        ordering = ['name']

    def __str__(self):
        return self.name


class ACExecutive(MasterFieldsMixin):
    """Accounts executive responsible for customer/vendor accounts."""

    name = models.CharField(max_length=100, verbose_name=_('Name'), help_text=_('Name of the accounts executive.'))
    code = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Code'), help_text=_('Optional code used to identify the accounts executive.'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('Email'), help_text=_('Email address of the accounts executive.'))
    phone = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Phone'), help_text=_('Contact phone number of the accounts executive.'))

    class Meta:
        verbose_name = _('A/C Executive')
        verbose_name_plural = _('A/C Executives')
        ordering = ['name']

    def __str__(self):
        return self.name


class Terms(MasterFieldsMixin):
    """Payment terms (e.g. Net 30)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the payment terms.'))
    days = models.PositiveIntegerField(default=0, verbose_name=_('Days'), help_text=_('Number of days allowed under these payment terms.'))
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Description'), help_text=_('Optional description of the payment terms.'))

    class Meta:
        verbose_name = _('Terms')
        verbose_name_plural = _('Terms')
        ordering = ['name']

    def __str__(self):
        return self.name


class CourierService(MasterFieldsMixin):
    """Courier / shipping service provider."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the courier or shipping service.'))
    contact_person = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Contact Person'), help_text=_('Name of the primary contact person.'))
    phone = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Phone'), help_text=_('Contact phone number for the courier service.'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('Email'), help_text=_('Email address for the courier service.'))
    tracking_url = models.URLField(max_length=500, blank=True, null=True, verbose_name=_('Tracking URL'), help_text=_('URL used to track shipments from this courier service.'))

    class Meta:
        verbose_name = _('Courier Service')
        verbose_name_plural = _('Courier Services')
        ordering = ['name']

    def __str__(self):
        return self.name