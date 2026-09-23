# requisition/models.py

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from purchase_order.models import PurchaseOrder


class RequisitionFieldsMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'), help_text=_('Date and time when this record was created.'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'), help_text=_('Date and time when this record was last updated.'))
    active = models.BooleanField(default=True, verbose_name=_('Active'), help_text=_('Whether this record is currently active.'))

    class Meta:
        abstract = True


class MetalSent(RequisitionFieldsMixin):
    metal_sent_no = models.PositiveIntegerField(unique=True, editable=False, verbose_name=_('Metal Sent No.'), help_text=_('Auto-generated sequential number for this metal sent record.'))
    invoice_no = models.CharField(max_length=100, verbose_name=_('Invoice No.'), help_text=_('Invoice number against which this metal was sent.'))
    metal_sent_date = models.DateField(verbose_name=_('Metal Sent Date'), help_text=_('Date on which the metal was sent.'))
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='metal_sent_entries', verbose_name=_('P.O. No'), help_text=_('Purchase order against which this metal was sent.'))
    triounce = models.CharField(max_length=50, blank=True, verbose_name=_('Triounce'), help_text=_('Purity/fineness grade of the metal sent.'))
    metal_gms = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0'), validators=[MinValueValidator(0)], verbose_name=_('Metal Gms.'), help_text=_('Weight of metal sent, in grams.'))
    metal_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(0)], verbose_name=_('Metal Amount'), help_text=_('Value of the metal sent.'))
    prepby = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='prepared_metal_sent_entries', verbose_name=_('Prepared By'), help_text=_('User who created this metal sent record.'))

    class Meta:
        verbose_name = _('Metal Sent')
        verbose_name_plural = _('Metal Sent')
        ordering = ['-metal_sent_date', '-metal_sent_no']
        indexes = [
            models.Index(fields=['invoice_no']),
            models.Index(fields=['metal_sent_date']),
            models.Index(fields=['purchase_order']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return f'Metal Sent #{self.metal_sent_no} - {self.invoice_no}'

    def save(self, *args, **kwargs):
        if not self.metal_sent_no:
            last = MetalSent.objects.order_by('-metal_sent_no').first()
            self.metal_sent_no = (last.metal_sent_no + 1) if last else 1
        super().save(*args, **kwargs)