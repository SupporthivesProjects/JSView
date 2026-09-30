"""Models for the 'vendor_shipment' app.

Maps the two legacy client tables:

  * ``tbvendorship1`` -> :class:`VendorShipment` (shipment header)
  * ``tbvendorship2`` -> :class:`VendorShipmentLine` (shipment lines)

A shipment header and all of its lines are created together in a single
transaction (see ``serializers.VendorShipmentCreateSerializer``).
"""

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from company.models import Company
from master.models import CourierService
from purchase_order.models import POCostCard, PurchaseOrder


class VendorShipmentFieldsMixin(models.Model):
    """Common fields shared by the vendor shipment tables."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
        help_text=_('Date and time when this record was created.'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At'),
        help_text=_('Date and time when this record was last updated.'),
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Whether this record is currently active.'),
    )

    class Meta:
        abstract = True


class VendorShipment(VendorShipmentFieldsMixin):
    """Vendor shipment header — maps to tbvendorship1."""

    vsno = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Vendor Shipment No'),
        help_text=_('Vendor invoice / shipment number.'),
    )
    vsdate = models.DateField(
        verbose_name=_('Shipment Date'),
        help_text=_('Date the vendor shipped the items.'),
    )
    vendorid = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='vendor_shipments',
        limit_choices_to={'is_supplier': True},
        verbose_name=_('Vendor'),
        help_text=_('Vendor this shipment was received from.'),
    )
    courierid = models.ForeignKey(
        CourierService,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='shipments',
        verbose_name=_('Courier'),
        help_text=_('Courier service used for this shipment.'),
    )
    trackref = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Tracking Reference'),
        help_text=_('Courier tracking reference for this shipment.'),
    )
    luser = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Last User'),
        help_text=_('Username of the last person to modify this shipment.'),
    )

    class Meta:
        verbose_name = _('Vendor Shipment')
        verbose_name_plural = _('Vendor Shipments')
        ordering = ['-id']
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['vsno']),
            models.Index(fields=['vsdate']),
            models.Index(fields=['vendorid']),
        ]

    def __str__(self):
        return self.vsno or f'VS-{self.pk}'


class VendorShipmentLine(VendorShipmentFieldsMixin):
    """Vendor shipment line — maps to tbvendorship2."""

    vendorshipid = models.ForeignKey(
        VendorShipment,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_('Vendor Shipment'),
        help_text=_('Shipment header this line belongs to.'),
    )
    poid = models.ForeignKey(
        PurchaseOrder,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='shipment_lines',
        verbose_name=_('Purchase Order'),
        help_text=_('Purchase order this item was shipped against.'),
    )
    costcardid = models.ForeignKey(
        POCostCard,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='shipment_lines',
        verbose_name=_('PO Cost Card'),
        help_text=_('PO cost card (style) this item was shipped against.'),
    )
    pcs = models.IntegerField(
        default=0,
        verbose_name=_('Pcs'),
        help_text=_('Number of pieces received.'),
    )
    metalwt = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0'),
        verbose_name=_('Metal Wt.'),
        help_text=_('Metal weight received, in grams.'),
    )
    diawt = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0'),
        verbose_name=_('Dia. Wt.'),
        help_text=_('Diamond weight received, in carats.'),
    )
    stplace = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Stone Place'),
        help_text=_('Stone placement for this line (Center/Side/Halo).'),
    )
    colwt = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0'),
        verbose_name=_('Col. Wt.'),
        help_text=_('Color stone weight received, in carats.'),
    )
    labour = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name=_('Labour'),
        help_text=_('Labour cost of the received item.'),
    )
    finding = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name=_('Finding'),
        help_text=_('Finding cost of the received item.'),
    )
    triounce = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name=_('Troy Ounce'),
        help_text=_('Troy ounce rate applied to this received item.'),
    )
    confrm = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_('Confirmed'),
        help_text=_('NULL = pending confirmation, True = confirmed.'),
    )

    class Meta:
        verbose_name = _('Vendor Shipment Line')
        verbose_name_plural = _('Vendor Shipment Lines')
        ordering = ['vendorshipid', 'id']
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['vendorshipid']),
            models.Index(fields=['poid']),
            models.Index(fields=['costcardid']),
            models.Index(fields=['confrm']),
        ]

    def __str__(self):
        return f'{self.vendorshipid} - {self.poid_id or ""}/{self.costcardid_id or ""}'
