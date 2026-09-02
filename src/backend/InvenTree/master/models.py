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
        indexes = [
            models.Index(fields=['active']),
        ]

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
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return f'{self.metal_type.name} - {self.name}'



class JewelryCategory(MasterFieldsMixin):
    """Jewelry category master."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the jewelry category.'))
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Description'), help_text=_('Optional description of the jewelry category.'))

    class Meta:
        verbose_name = _('Jewelry Category')
        verbose_name_plural = _('Jewelry Categories')
        ordering = ['name']
        indexes = [models.Index(fields=['active'])]

    def __str__(self):
        return self.name


class JewelrySubCategory(MasterFieldsMixin):
    """Jewelry sub-category master."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the jewelry sub-category.'))
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Description'), help_text=_('Optional description of the jewelry sub-category.'))
    category = models.ForeignKey( JewelryCategory,on_delete=models.SET_NULL,null=True, blank=True,related_name='subcategories', verbose_name=_('Category'), help_text=_('Optional jewelry category associated with this sub-category.'))

    class Meta:
        verbose_name = _('Jewelry Sub Category')
        verbose_name_plural = _('Jewelry Sub Categories')
        ordering = ['name']
        indexes = [models.Index(fields=['active']), models.Index(fields=['category'])]

    def __str__(self):
        return self.name



class Setting(MasterFieldsMixin):
    """Jewelry setting type (e.g. Prong, Bezel, Pave)."""
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the jewelry setting type.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the jewelry setting type.'))

    class Meta:
        verbose_name = _('Setting')
        verbose_name_plural = _('Settings')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name



class LabourSetting(MasterFieldsMixin):
    """Labour charge configuration for a jewelry setting."""

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

    name = models.CharField(max_length=100, verbose_name=_('Name'), help_text=_('Name of the labour setting.'))
    setting = models.ForeignKey(Setting, on_delete=models.SET_NULL, null=True, blank=True, related_name='labour_settings', verbose_name=_('Setting'), help_text=_('Jewelry setting associated with this labour configuration.'))
    charge_type = models.CharField(max_length=20, choices=CHARGE_TYPE_CHOICES, default=CHARGE_TYPE_FIXED, verbose_name=_('Charge Type'), help_text=_('Method used to calculate the labour charge.'))
    rate = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0'), validators=[MinValueValidator(0)], verbose_name=_('Rate'), help_text=_('Labour charge rate based on the selected charge type.'))

    class Meta:
        verbose_name = _('Labour Setting')
        verbose_name_plural = _('Labour Settings')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name

    

class MetalRate(MasterFieldsMixin):
    """Dated metal rate for a MetalType / MetalPurity."""

    metal_type = models.ForeignKey(MetalType, on_delete=models.CASCADE, related_name='rates', verbose_name=_('Metal Type'), help_text=_('Metal type for which this rate applies.'))
    rate = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_('Rate'), help_text=_('Metal rate applicable for the selected date.'))
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
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return f'{self.metal_type.name} @ {self.date}'


class FindingType(MasterFieldsMixin):
    """Jewelry finding type (e.g. Chain, Clasp, Hook, Jump Ring)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Finding Item'), help_text=_('Name of the jewelry finding item.'))
    type = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Type'), help_text=_('Type or specification of the finding, e.g. CABLE - 30.'))
    weight = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0'), validators=[MinValueValidator(0)], verbose_name=_('Finding Wt.'), help_text=_('Weight of the finding in grams.'))
    metal = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Finding Metal'), help_text=_('Metal of the finding, e.g. 14 KT Gold.'))
    price = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(0)], verbose_name=_('Finding Price'), help_text=_('Price of the finding.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the finding.'))

    class Meta:
        verbose_name = _('Finding Type')
        verbose_name_plural = _('Finding Types')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['type']),
            models.Index(fields=['active']),
        ]

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
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class Duty(MasterFieldsMixin):
    """Import / export duty rate."""

    metal_type = models.ForeignKey(MetalType, on_delete=models.CASCADE, related_name='duties', verbose_name=_('Metal Type'), help_text=_('Metal type for which this duty applies.'))
    duty = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_('Duty'), help_text=_('Duty percentage applicable to the selected metal type.'))
    markup = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_('Markup'), help_text=_('Markup value applicable to the selected metal type.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the duty configuration.'))

    class Meta:
        verbose_name = _('Duty')
        verbose_name_plural = _('Duties')
        ordering = ['metal_type']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        
        return f'{self.metal_type.name} - {self.duty}%'


class Stamp(MasterFieldsMixin):
    """Hallmark / stamp type (e.g. BIS Hallmark, 916)."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the hallmark or stamp.'))
    image = models.ImageField(upload_to=stamp_image, blank=True, null=True, verbose_name=_('Image'), help_text=_('Optional image representing the hallmark or stamp.'))
    description = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Description'), help_text=_('Optional description of the stamp.'))
    customers = models.ManyToManyField( Company,blank=True,related_name='stamps',verbose_name=_('Customers'),help_text=_('Customers assigned to this stamp.'))

    class Meta:
        verbose_name = _('Stamp')
        verbose_name_plural = _('Stamps')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

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
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class Terms(MasterFieldsMixin):
    """Payment terms (e.g. Net 30) assigned to vendors."""

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'), help_text=_('Name of the payment terms.'))
    days = models.PositiveIntegerField(default=0, verbose_name=_('Days'), help_text=_('Number of days allowed under these payment terms.'))
    vendors = models.ManyToManyField(Company, blank=True, related_name='payment_terms', verbose_name=_('Vendors'), help_text=_('Vendors to whom these payment terms apply.'))
    description = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Description'), help_text=_('Optional description of the payment terms.'))

    class Meta:
        verbose_name = _('Terms')
        verbose_name_plural = _('Terms')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

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
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name



class Templates(MasterFieldsMixin):
    """Email/attachment template used by POMail formats (stores template code or a path)."""

    name = models.CharField(max_length=150, verbose_name=_('Name'), help_text=_('Name of the template.'))
    subject = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Subject'), help_text=_('Email subject line to use with this template.'))
    template = models.TextField(blank=True, null=True, verbose_name=_('Template'), help_text=_('Template content — inline HTML/code, or a path/reference to a report template.'))

    class Meta:
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')
        ordering = ['name']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class POMail(MasterFieldsMixin):
    """P.O. Mail configuration — maps recipient formats (Vendor, Diamond Office, etc.) to Templates."""
    
    name = models.CharField(max_length=150, verbose_name=_('Name'), help_text=_('Name of the P.O. Mail configuration.'))
    format1 = models.OneToOneField(Templates, on_delete=models.SET_NULL, null=True, blank=True, related_name='format1', verbose_name=_('Format 1'), help_text=_('Template used for Vendor.'))
    format2 = models.OneToOneField(Templates, on_delete=models.SET_NULL, null=True, blank=True, related_name='format2', verbose_name=_('Format 2'), help_text=_('Template used for Diamond Office.'))
    format3 = models.OneToOneField(Templates, on_delete=models.SET_NULL, null=True, blank=True, related_name='format3', verbose_name=_('Format 3'), help_text=_('Template used for Color Stone Office.'))
    format4 = models.OneToOneField(Templates, on_delete=models.SET_NULL, null=True, blank=True, related_name='format4', verbose_name=_('Format 4'), help_text=_('Template used for New York Office.'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'), help_text=_('Display order of this configuration.'))
    
    class Meta:
        verbose_name = _('P.O. Mail')
        verbose_name_plural = _('P.O. Mails')
        ordering = ['order']
        indexes = [
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name