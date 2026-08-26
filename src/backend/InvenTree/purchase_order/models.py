from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from company.models import Company
from master.models import (
    JewelryCategory,
    JewelrySubCategory,
    MetalPurity,
    Stamp,
    ACExecutive,
    Terms,
)


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

    def save(self, *args, **kwargs):
        """Save the line, then create a frozen POCostCard snapshot (ORDER only)."""
        super().save(*args, **kwargs)

        # Import inside function to avoid circular imports
        from .utils import create_po_costcard_snapshot

        create_po_costcard_snapshot(self)


class POCostCard(POFieldsMixin):
    """Frozen snapshot of a cards.CostCard header attached to a Purchase Order.

    Maps to tbpocostcard1 in the legacy client database. Snapshot rows are
    created automatically when a PurchaseOrderLine is saved for an ORDER-type
    PO (Purchase REQUESTs use the original CostCard directly).
    """

    poid = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='po_costcards',
        verbose_name=_('Purchase Order'),
        help_text=_('Purchase order this snapshot belongs to.'),
    )

    costcard = models.ForeignKey(
        'cards.CostCard',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='po_snapshots',
        verbose_name=_('Original Cost Card'),
        help_text=_('Original CostCard reference (may be deleted later).'),
    )

    # ---- Frozen header fields (copied from CostCard at snapshot time) ----
    costcardno = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Cost Card No'),
        help_text=_('Snapshot of the original cost card number.'),
    )
    our_style_no = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Our Style No'),
        help_text=_('Snapshot of the internal style number.'),
    )
    vendor_style_no = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('Vendor Style No'),
        help_text=_('Snapshot of the vendor style number.'),
    )
    vendor = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='po_costcard_vendors',
        verbose_name=_('Vendor'),
        help_text=_('Snapshot vendor for this piece.'),
    )
    customer = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='po_costcard_customers',
        verbose_name=_('Customer'),
        help_text=_('Snapshot customer for this piece.'),
    )
    karat = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Kt'),
        help_text=_('Snapshot karat value, e.g. 14KT, 18KT.'),
    )
    metal_grams = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Metal Grams'),
        help_text=_('Snapshot weight of metal used, in grams.'),
    )
    net_weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name=_('Net Weight'),
        help_text=_('Snapshot net weight of the piece.'),
    )
    gross_weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name=_('Gross Weight'),
        help_text=_('Snapshot gross weight of the piece.'),
    )
    troy_ounce_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Troy Ounce Price'),
        help_text=_('Snapshot metal price per troy ounce.'),
    )
    finding_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Finding Price'),
        help_text=_('Snapshot finding price.'),
    )

    # ---- Frozen cost tab fields ----
    metal_loss_pct = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Metal Loss %'),
        help_text=_('Snapshot metal loss percentage.'),
    )
    metal_loss_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Metal Loss Amount'),
        help_text=_('Snapshot metal loss amount.'),
    )
    metal_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Metal Amount'),
        help_text=_('Snapshot metal amount.'),
    )
    dia_pcs = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name=_('Dia. Pcs'),
        help_text=_('Snapshot total diamond piece count.'),
    )
    dia_cts = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Dia. Cts'),
        help_text=_('Snapshot total diamond carat weight.'),
    )
    dia_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Dia. Amount'),
        help_text=_('Snapshot total diamond cost.'),
    )
    col_pcs = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name=_('Col. Pcs'),
        help_text=_('Snapshot total color stone piece count.'),
    )
    col_cts = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Col. Cts'),
        help_text=_('Snapshot total color stone carat weight.'),
    )
    col_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Col. Amount'),
        help_text=_('Snapshot total color stone cost.'),
    )
    stone_pcs = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name=_('Tot. Stone Pcs'),
        help_text=_('Snapshot combined stone piece count.'),
    )
    stone_cts = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Tot. Stone Cts'),
        help_text=_('Snapshot combined stone carat weight.'),
    )
    stone_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Tot. Stone Amount'),
        help_text=_('Snapshot combined stone cost.'),
    )
    labour_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Labour Amount'),
        help_text=_('Snapshot total labour cost.'),
    )
    dia_handling_pct = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Dia. Handl. Charges %'),
        help_text=_('Snapshot diamond handling percentage.'),
    )
    dia_handling_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Dia. Handl. Amount'),
        help_text=_('Snapshot diamond handling amount.'),
    )
    col_handling_pct = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Col. Handl. Charges %'),
        help_text=_('Snapshot color stone handling percentage.'),
    )
    col_handling_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Col. Handl. Amount'),
        help_text=_('Snapshot color stone handling amount.'),
    )
    vendor_markup_pct = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Vendor Markup %'),
        help_text=_('Snapshot vendor markup percentage.'),
    )
    vendor_markup_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Vendor Markup Amount'),
        help_text=_('Snapshot vendor markup amount.'),
    )
    fob = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('F.O.B'),
        help_text=_('Snapshot free-on-board amount.'),
    )
    duty_pct = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Duty %'),
        help_text=_('Snapshot duty percentage.'),
    )
    duty_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Duty Amount'),
        help_text=_('Snapshot duty amount.'),
    )
    margin_pct = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Margin %'),
        help_text=_('Snapshot profit margin percentage.'),
    )
    margin_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Margin Amount'),
        help_text=_('Snapshot profit margin amount.'),
    )
    final_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        blank=True,
        verbose_name=_('Final Amount'),
        help_text=_('Snapshot final computed cost.'),
    )

    # ---- Frozen classification FKs (SET_NULL so snapshot survives) ----
    category = models.ForeignKey(
        JewelryCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='po_costcards',
        verbose_name=_('Jewelry Category'),
        help_text=_('Snapshot jewelry category.'),
    )
    sub_category = models.ForeignKey(
        JewelrySubCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='po_costcards',
        verbose_name=_('Jewelry Sub Category'),
        help_text=_('Snapshot jewelry sub-category.'),
    )
    metal_purity = models.ForeignKey(
        MetalPurity,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='po_costcards',
        verbose_name=_('Metal Purity'),
        help_text=_('Snapshot metal purity grade.'),
    )

    stnoauto = models.IntegerField(
        default=0,
        verbose_name=_('Stone No Auto'),
        help_text=_('Auto-generated stone sequence number copied from the PO line.'),
    )

    class Meta:
        ordering = ['poid', 'id']
        verbose_name = _('PO Cost Card')
        verbose_name_plural = _('PO Cost Cards')
        unique_together = ['poid', 'costcard']
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['poid']),
            models.Index(fields=['costcard']),
        ]

    def __str__(self):
        return f'{self.poid} - {self.costcardno or self.our_style_no}'


class POCostCardLine(POFieldsMixin):
    """Frozen snapshot of a stone/finish line — maps to tbpocostcard2.

    Stores NAME strings rather than FKs: even if the original property
    record is deleted later, the snapshot must retain the data.
    For FINISHTYPE lines, the finish type name is stored in ``stone``.
    """

    ETYPE_CHOICES = [
        ('DIAMOND', _('Diamond')),
        ('COLOURSTONE', _('Colour Stone')),
        ('FINISHTYPE', _('Finish Type')),
    ]

    po_costcard = models.ForeignKey(
        POCostCard,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_('PO Cost Card'),
        help_text=_('PO cost card snapshot this line belongs to.'),
    )
    etype = models.CharField(
        max_length=20,
        choices=ETYPE_CHOICES,
        verbose_name=_('Line Type'),
        help_text=_('Which tab this frozen line came from: DIAMOND, COLOURSTONE or FINISHTYPE.'),
    )

    # ---- Frozen property names (strings, not FKs) ----
    stone = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Stone'), help_text=_('Frozen stone name (finish type name for FINISHTYPE lines).'))
    shape = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Shape'), help_text=_('Frozen shape name.'))
    cut = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Cut'), help_text=_('Frozen cut name.'))
    colour = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Colour'), help_text=_('Frozen colour name.'))
    quality = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Quality'), help_text=_('Frozen quality name.'))
    mm_size = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('MM Size'), help_text=_('Frozen size name.'))
    sieve_size = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Sieve Size'), help_text=_('Frozen sieve size.'))
    setting = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Setting'), help_text=_('Frozen setting name.'))
    stone_place = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Stone Place'), help_text=_('Frozen stone placement name.'))

    # ---- Frozen numeric values ----
    pointer = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name=_('Pointer'), help_text=_('Frozen pointer value.'))
    pcs = models.PositiveIntegerField(default=0, verbose_name=_('Pcs'), help_text=_('Frozen piece count.'))
    cts = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'), blank=True, verbose_name=_('Cts'), help_text=_('Frozen carat weight.'))
    rate = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0'), blank=True, verbose_name=_('Rate'), help_text=_('Frozen rate applied.'))
    pc = models.CharField(max_length=1, choices=[('P', _('Per Piece')), ('C', _('Per Carat'))], default='C', verbose_name=_('P/C'), help_text=_('Frozen rate unit: P = Per Piece, C = Per Carat.'))
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), blank=True, verbose_name=_('Amount'), help_text=_('Frozen line amount.'))
    labour_rate = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0'), blank=True, verbose_name=_('L.Rate'), help_text=_('Frozen labour rate.'))
    labour_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'), blank=True, verbose_name=_('L.Amount'), help_text=_('Frozen labour amount.'))
    default_rate = models.BooleanField(default=True, verbose_name=_('D.R.'), help_text=_('Frozen D.R. flag (rate pulled from rate table).'))

    class Meta:
        ordering = ['po_costcard', 'id']
        verbose_name = _('PO Cost Card Line')
        verbose_name_plural = _('PO Cost Card Lines')
        indexes = [
            models.Index(fields=['active']),
            models.Index(fields=['po_costcard']),
            models.Index(fields=['etype']),
        ]

    def __str__(self):
        return f'{self.po_costcard} - {self.get_etype_display()}: {self.stone or self.shape or ""}'
