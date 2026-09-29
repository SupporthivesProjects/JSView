from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from costcard.models import CostCard, StonePlace
from purchase_order.models import PurchaseOrder


class RequisitionFieldsMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'), help_text=_('Date and time when this record was created.'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'), help_text=_('Date and time when this record was last updated.'))
    active = models.BooleanField(default=True, verbose_name=_('Active'), help_text=_('Whether this record is currently active.'))

    class Meta:
        abstract = True



class FluteEntry(RequisitionFieldsMixin):
    invoice_no = models.CharField(max_length=100, verbose_name=_('Invoice No.'), help_text=_('Invoice number for this flute entry.'))
    flute_date = models.DateField(verbose_name=_('Flute Date'), help_text=_('Date of the flute entry.'))
    prepby = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='prepared_flute_entries', verbose_name=_('Prepared By'), help_text=_('User who created this flute entry.'))

    class Meta:
        verbose_name = _('Flute Entry')
        verbose_name_plural = _('Flute Entries')
        ordering = ['-flute_date', '-id']
        indexes = [
            models.Index(fields=['invoice_no']),
            models.Index(fields=['flute_date']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return f'{self.invoice_no} - {self.flute_date}'


class FluteEntryLine(RequisitionFieldsMixin):
    flute_entry = models.ForeignKey(FluteEntry, on_delete=models.CASCADE, related_name='lines', verbose_name=_('Flute Entry'), help_text=_('Flute entry header for this line.'))
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='flute_entry_lines', verbose_name=_('P.O. No.'), help_text=_('Purchase order selected for this flute entry line.'))
    cost_card = models.ForeignKey(CostCard, on_delete=models.PROTECT, related_name='flute_entry_lines', verbose_name=_('Our Style No.'), help_text=_('Cost card/style selected for this flute entry line.'))
    cts = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0'), verbose_name=_('Cts.'), help_text=_('Stone weight in carats.'))
    stone_type = models.CharField(max_length=50, choices=[('diamond', _('Diamond')), ('color_stone', _('Color Stone'))], default='diamond', verbose_name=_('Stone Type'), help_text=_('Type of stone for this flute entry line.'))
    sets = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), verbose_name=_('Sets'), help_text=_('Number of sets.'))
    stone_place = models.ForeignKey(StonePlace, on_delete=models.PROTECT, null=True, blank=True, related_name='flute_entry_lines', verbose_name=_('Stone Place'), help_text=_('Stone placement on the jewelry piece.'))
    rate = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0'), verbose_name=_('Rate'), help_text=_('Rate applied for this flute entry line.'))
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), verbose_name=_('Amount'), help_text=_('Amount for this flute entry line.'))
    cost_card_rate = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), verbose_name=_('Cost Card Rate'), help_text=_('Cost card rate for the selected style.'))

    class Meta:
        verbose_name = _('Flute Entry Line')
        verbose_name_plural = _('Flute Entry Lines')
        ordering = ['id']
        indexes = [
            models.Index(fields=['flute_entry']),
            models.Index(fields=['purchase_order']),
            models.Index(fields=['cost_card']),
            models.Index(fields=['stone_type']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return f'{self.flute_entry.invoice_no} - {self.cost_card.our_style_no}'

    
class MetalSent(RequisitionFieldsMixin):
    metal_sent_no = models.PositiveIntegerField(unique=True, editable=False, verbose_name=_('Metal Sent No.'), help_text=_('Auto-generated sequential number for this metal sent record.'))
    invoice_no = models.CharField(max_length=100, verbose_name=_('Invoice No.'), help_text=_('Invoice number against which this metal was sent.'))
    metal_sent_date = models.DateField(verbose_name=_('Metal Sent Date'), help_text=_('Date on which the metal was sent.'))
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='metal_sent_entries', verbose_name=_('P.O. No'), help_text=_('Purchase order against which this metal was sent.'))
    triounce = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), verbose_name=_('Triounce'), help_text=_('Purity/fineness grade of the metal sent.'))
    metal_gms = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), verbose_name=_('Metal Gms.'), help_text=_('Weight of metal sent, in grams. Can be negative for returns/adjustments.'))
    metal_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), verbose_name=_('Metal Amount'), help_text=_('Value of the metal sent. Can be negative for returns/adjustments.'))
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


