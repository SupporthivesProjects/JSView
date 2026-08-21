from django.db import models
from django.utils.translation import gettext_lazy as _

from company.models import Company
from master.models import Stamp, ACExecutive, Terms


class POFieldsMixin(models.Model):
    """Common fields for purchase order tables."""

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


class PurchaseOrder(POFieldsMixin):
    """Purchase Order header — maps to tbpo1."""

    POTYPE_CHOICES = [
        ('REQUEST', _('Request')),
        ('ORDER', _('Order')),
    ]

    # Self-referential link: REQUEST → ORDER flow
    linkid = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='linked_orders',
        verbose_name=_('Linked PO'),
        help_text=_('Parent PO when this is an ORDER converted from a REQUEST.'),
    )

    potype = models.CharField(
        max_length=20,
        choices=POTYPE_CHOICES,
        default='ORDER',
        verbose_name=_('PO Type'),
        help_text=_('Type of purchase order: REQUEST or ORDER.'),
    )

    pono = models.CharField(
        max_length=100,
        blank=True,
        editable=False,
        verbose_name=_('PO Number'),
        help_text=_('Auto-generated purchase order number.'),
    )

    npono = models.IntegerField(
        default=0,
        editable=False,
        verbose_name=_('Sequential PO No'),
        help_text=_('Sequential number used in PO number generation.'),
    )

    nyear = models.IntegerField(
        default=0,
        editable=False,
        verbose_name=_('PO Year'),
        help_text=_('Year component of the PO number.'),
    )

    podate = models.DateField(
        verbose_name=_('PO Date'),
        help_text=_('Date when the purchase order was created.'),
    )

    prepby = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Prepared By'),
        help_text=_('Name of the person who prepared this PO.'),
    )

    ddate = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Delivery Date'),
        help_text=_('Expected delivery date.'),
    )

    vcsdate = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Vendor Confirmed Ship Date'),
        help_text=_('Date confirmed by the vendor for shipping.'),
    )

    esdstone = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('ESD Stone'),
        help_text=_('Expected stone delivery date.'),
    )

    customerid = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='customer_pos',
        verbose_name=_('Customer'),
        help_text=_('Customer this PO is placed against.'),
    )

    customer_pono = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Customer PO No'),
        help_text=_('Customer reference PO number.'),
    )

    pocategory = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('PO Category'),
        help_text=_('Category of the purchase order (e.g. Production, Sample).'),
    )

    rem = models.TextField(
        blank=True,
        verbose_name=_('Remarks'),
        help_text=_('Remarks for this purchase order.'),
    )

    note = models.TextField(
        blank=True,
        verbose_name=_('Notes'),
        help_text=_('Internal notes for this purchase order.'),
    )

    stampid = models.ForeignKey(
        Stamp,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='purchase_orders',
        verbose_name=_('Stamp'),
        help_text=_('Hallmark / stamp type for this PO.'),
    )

    acexeid = models.ForeignKey(
        ACExecutive,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='purchase_orders',
        verbose_name=_('A/C Executive'),
        help_text=_('Accounts executive responsible for this PO.'),
    )

    vendorid = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='vendor_pos',
        verbose_name=_('Vendor'),
        help_text=_('Vendor this PO is placed with.'),
    )

    tqty = models.IntegerField(
        default=0,
        verbose_name=_('Total Qty'),
        help_text=_('Total quantity across all line items.'),
    )

    termsid = models.ForeignKey(
        Terms,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='purchase_orders',
        verbose_name=_('Terms'),
        help_text=_('Payment terms for this PO.'),
    )

    luser = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Last User'),
        help_text=_('Username of the last person to modify this PO.'),
    )

    # Cancellation fields
    canc_dt = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Cancelled Date'),
        help_text=_('Date when this PO was cancelled.'),
    )

    canc_rem = models.TextField(
        blank=True,
        verbose_name=_('Cancel Remarks'),
        help_text=_('Remarks entered when cancelling this PO.'),
    )

    canc_user = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Cancelled By'),
        help_text=_('Username of the person who cancelled this PO.'),
    )

    class Meta:
        verbose_name = _('Purchase Order')
        verbose_name_plural = _('Purchase Orders')
        ordering = ['-podate', '-npono']
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['pono']),
            models.Index(fields=['potype']),
            models.Index(fields=['pocategory']),
            models.Index(fields=['podate']),
            models.Index(fields=['customerid']),
            models.Index(fields=['vendorid']),
        ]

    def __str__(self):
        return f'{self.pono} ({self.get_potype_display()})'

    def save(self, *args, **kwargs):
        from .utils import generate_po_number

        if not self.pono:
            self.pono, self.npono = generate_po_number(
                potype=self.potype,
                pocategory=self.pocategory,
                customerid=self.customerid_id,
                podate=self.podate,
            )
            self.nyear = self.podate.year if self.podate else 0

        # REQUEST → ORDER link logic
        if self.linkid_id and self.potype == 'ORDER':
            # When creating an ORDER linked to a REQUEST, update the
            # REQUEST's linkid to point back to this new ORDER.
            super().save(*args, **kwargs)
            PurchaseOrder.objects.filter(pk=self.linkid_id).update(linkid=self.pk)
            return

        super().save(*args, **kwargs)


class PurchaseOrderLine(POFieldsMixin):
    """Purchase Order line item — maps to tbpo2."""

    poid = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_('Purchase Order'),
        help_text=_('Purchase order this line belongs to.'),
    )

    costcardid = models.ForeignKey(
        'cards.CostCard',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='po_lines',
        verbose_name=_('Cost Card'),
        help_text=_('Cost card associated with this line item.'),
    )

    styleno = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Style No'),
        help_text=_('Internal style number for this line item.'),
    )

    vstyleno = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Vendor Style No'),
        help_text=_('Vendor style number for this line item.'),
    )

    vendorid = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='po_line_vendors',
        verbose_name=_('Vendor'),
        help_text=_('Vendor for this specific line item (overrides PO-level vendor).'),
    )

    qty = models.IntegerField(
        default=0,
        verbose_name=_('Quantity'),
        help_text=_('Quantity ordered on this line.'),
    )

    size = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Size'),
        help_text=_('Comma-separated list of sizes (e.g. "7,8,9").'),
    )

    spcs = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Size Pieces'),
        help_text=_('Comma-separated list of pieces per size (e.g. "100,200,300").'),
    )

    stnoauto = models.IntegerField(
        default=0,
        verbose_name=_('Stone No Auto'),
        help_text=_('Auto-generated stone sequence number.'),
    )

    class Meta:
        verbose_name = _('Purchase Order Line')
        verbose_name_plural = _('Purchase Order Lines')
        ordering = ['poid', 'pk']
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['poid']),
            models.Index(fields=['costcardid']),
            models.Index(fields=['vendorid']),
        ]

    def __str__(self):
        return f'PO {self.poid} - {self.styleno}'
