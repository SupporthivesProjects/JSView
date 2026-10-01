"""Helper functions for the 'vendor_shipment' app.

These replicate the PostgreSQL functions used by the legacy Go server, using
the Django ORM against the local database tables:

  * ``fn_po_vendorstatus(vendorid, opcl)``    -> :func:`get_vendor_po_list`
  * ``fn_vendor_style(poid, opcl)``           -> :func:`get_vendor_style_list`
  * ``fn_tbvendorship1_vendorpo(vendorid)``   -> :func:`get_confirm_pending_invoices`
  * ``fn_tbvendorship_data(vendorid, vsid)``  -> :func:`get_confirm_pending_data`

Both ``fn_po_vendorstatus`` and ``fn_vendor_style`` compare the ordered
quantity (``tbpo2.qty`` -> :class:`PurchaseOrderLine.qty`) against the received
quantity stored on the shipment lines (``tbvendorship2.pcs`` ->
:class:`VendorShipmentLine.pcs`), matching on ``(poid, costcardid)``.

``tbpo2.costcardid`` references the original cost card (``tbcostcard1`` ->
:class:`costcard.models.CostCard`), *not* the PO snapshot
(``tbpocostcard1`` / :class:`purchase_order.models.POCostCard`). The FK on
:class:`VendorShipmentLine` therefore points at :class:`CostCard` directly.
"""

from decimal import Decimal

from django.db import transaction
from django.db.models import Case, F, IntegerField, Sum, When

from purchase_order.models import PurchaseOrder, PurchaseOrderLine

from .models import VendorShipment, VendorShipmentLine

ZERO = Decimal('0')


def _received_pcs(po_ids, require_diawt=False):
    """Sum of shipped pieces keyed by ``(poid, costcard_id)``.

    Mirrors the legacy correlated sub-select. When ``require_diawt`` is set
    the sum reproduces the ``fn_vendor_style`` expression
    ``SUM(CASE WHEN diawt IS NULL THEN 0 ELSE pcs END)``; otherwise
    ``fn_po_vendorstatus`` simply sums ``pcs``.
    """
    received = {}
    po_ids = list(po_ids)

    if not po_ids:
        return received

    qs = VendorShipmentLine.objects.filter(
        poid_id__in=po_ids,
        costcardid__isnull=False,
    )

    if require_diawt:
        qs = qs.annotate(
            counted=Case(
                When(diawt__isnull=True, then=0),
                default=F('pcs'),
                output_field=IntegerField(),
            )
        )
        rows = qs.values('poid_id', 'costcardid_id').annotate(total=Sum('counted'))
    else:
        rows = qs.values('poid_id', 'costcardid_id').annotate(total=Sum('pcs'))

    for row in rows:
        received[(row['poid_id'], row['costcardid_id'])] = row['total'] or 0

    return received


def _balance(ordered, received):
    """``balpcs`` — ``max(0, ordered - received)`` (legacy clamp)."""
    balance = ordered - received
    return 0 if balance < 0 else balance


def get_vendor_po_list(vendorid=None, is_open=True):
    """Replicate ``fn_po_vendorstatus``.

    Returns a list of ``{'poid', 'pono'}`` for the given vendor.

    The ordered vs received comparison is evaluated per purchase order line
    (i.e. per ``costcardid``), exactly like the legacy query: a PO qualifies
    for the open list when at least one of its lines still has a balance, and
    for the closed list when at least one of its lines is fully received.
    The ``GROUP BY poid, pono`` in the SQL simply de-duplicates the result.

    * ``is_open=True``  -> lines with ``balpcs > 0``
    * ``is_open=False`` -> lines with ``balpcs = 0``
    """
    po_qs = PurchaseOrder.objects.filter(potype='ORDER', active=True)

    if vendorid:
        po_qs = po_qs.filter(vendorid_id=vendorid)

    po_map = {po.pk: po.pono for po in po_qs.only('pk', 'pono')}

    if not po_map:
        return []

    received = _received_pcs(po_map.keys())

    selected = set()

    for line in (
        PurchaseOrderLine.objects
        .filter(poid_id__in=po_map.keys())
        .only('poid_id', 'costcardid_id', 'qty')
    ):
        balance = _balance(
            line.qty,
            received.get((line.poid_id, line.costcardid_id), 0),
        )

        if (balance != 0) == is_open:
            selected.add(line.poid_id)

    return [
        {'poid': po_id, 'pono': po_map[po_id]}
        for po_id in sorted(selected)
    ]


def get_vendor_style_list(poid, is_open=True):
    """Replicate ``fn_vendor_style``.

    Returns a list of ``{'costcardid', 'styleno'}`` for the styles of a
    purchase order. ``costcardid`` is the original
    :class:`costcard.models.CostCard` id (the value stored on
    :class:`VendorShipmentLine`).

    The received quantity only counts shipment lines which carry a diamond
    weight (``CASE WHEN diawt IS NULL THEN 0 ELSE pcs END``), matching the
    legacy function.

    * ``is_open=True``  -> styles with ``balpcs > 0``
    * ``is_open=False`` -> styles with ``balpcs = 0``
    """
    if not poid:
        return []

    lines = (
        PurchaseOrderLine.objects
        .filter(poid_id=poid, costcardid__isnull=False)
        .select_related('costcardid')
        .order_by('costcardid_id', 'styleno')
    )

    received = _received_pcs([poid], require_diawt=True)

    result = []
    seen = set()

    for line in lines:
        balance = _balance(
            line.qty,
            received.get((line.poid_id, line.costcardid_id), 0),
        )

        if (balance != 0) != is_open:
            continue

        costcard_id = line.costcardid_id
        styleno = line.styleno or line.costcardid.our_style_no

        key = (costcard_id, styleno)

        if key in seen:
            continue

        seen.add(key)

        result.append({
            'costcardid': costcard_id,
            'styleno': styleno or '',
        })

    return result


def get_confirm_pending_invoices(vendorid=None):
    """Replicate ``fn_tbvendorship1_vendorpo``.

    Returns a list of ``{'vendorshipid', 'vsno'}`` for every shipment of the
    vendor which still has at least one unconfirmed line (``confrm IS NULL``),
    ordered by shipment number.
    """
    qs = VendorShipment.objects.filter(
        active=True,
        lines__confrm__isnull=True,
    )

    if vendorid:
        qs = qs.filter(vendorid_id=vendorid)

    qs = qs.distinct().order_by('vsno', 'pk')

    return [
        {'vendorshipid': shipment.pk, 'vsno': shipment.vsno}
        for shipment in qs
    ]


def get_confirm_pending_data(vendorid=None, vendorshipid=None):
    """Replicate ``fn_tbvendorship_data``.

    Returns the detailed shipment lines of one shipment, joined with the
    purchase order, the ordered quantity and the cost card values so the
    confirmation screen can compare received vs ordered.
    """
    qs = VendorShipment.objects.filter(pk=vendorshipid)

    if vendorid:
        qs = qs.filter(vendorid_id=vendorid)

    header = qs.first()

    if header is None:
        return []

    lines = list(
        header.lines
        .select_related('poid', 'costcardid')
        .order_by('pk')
    )

    po_ids = {line.poid_id for line in lines if line.poid_id}

    po_lines = {}
    if po_ids:
        for po_line in (
            PurchaseOrderLine.objects
            .filter(poid_id__in=po_ids, costcardid__isnull=False)
            .only('pk', 'poid_id', 'costcardid_id', 'qty', 'styleno')
        ):
            po_lines[(po_line.poid_id, po_line.costcardid_id)] = po_line

    result = []

    for line in lines:
        costcard = line.costcardid
        costcard_id = line.costcardid_id
        po_line = po_lines.get((line.poid_id, costcard_id))

        pono = line.poid.pono if line.poid else None
        styleno = po_line.styleno if po_line else ''
        if not styleno and costcard:
            styleno = costcard.our_style_no

        result.append({
            'tableid': line.pk,
            'vendorshipid': line.vendorshipid_id,
            'pono': pono,
            'styleno': styleno or '',
            'pcs': line.pcs,
            'metalwt': line.metalwt,
            'diawt': line.diawt,
            'colwt': line.colwt,
            'labour': line.labour,
            'finding': line.finding,
            'triounce': line.triounce,
            'confrm': line.confrm,
            # aliases kept for parity with the legacy result set
            'purchaseno': pono,
            'coststyle': costcard.our_style_no if costcard else '',
            # ordered / cost card values
            'qty': po_line.qty if po_line else 0,
            'metalgms': costcard.metal_grams if costcard else ZERO,
            'diacts': costcard.dia_cts if costcard else ZERO,
            'colcts': costcard.col_cts if costcard else ZERO,
            'costlabour': costcard.labour_amount if costcard else ZERO,
            'costfinding': costcard.finding_price if costcard else ZERO,
            'touncep': costcard.troy_ounce_price if costcard else ZERO,
        })

    return result


def _entry_pk(entry):
    """Shipment line pk from a confirm-update entry.

    ``tableid`` is the canonical key; the legacy Go client sent the same value
    as ``id``, so that is accepted as a fallback to keep ports working.
    Returns ``None`` when no usable identifier is present.
    """
    for key in ('tableid', 'id'):
        try:
            value = entry.get(key)
        except AttributeError:
            return None

        if value in (None, ''):
            continue

        try:
            return int(value)
        except (TypeError, ValueError):
            continue

    return None


def update_confirm_flags(entries):
    """Bulk update the ``confrm`` flag of shipment lines.

    ``entries`` is a list of ``{'tableid': <line pk>, 'confrm': <bool>}``
    (``id`` is accepted as an alias for ``tableid``).
    A truthy ``confrm`` marks the line as confirmed; any falsy / missing value
    resets it to the pending state (``NULL``), matching the legacy semantics
    where ``confrm IS NULL`` means "not confirmed yet".

    Returns the number of lines that were updated.
    """
    if not entries:
        return 0

    ids = [pk for pk in (_entry_pk(entry) for entry in entries) if pk is not None]

    if not ids:
        return 0

    lines = {
        line.pk: line
        for line in VendorShipmentLine.objects.filter(pk__in=ids)
    }

    updated = []

    for entry in entries:
        pk = _entry_pk(entry)

        if pk is None or pk not in lines:
            continue

        line = lines[pk]
        line.confrm = True if entry.get('confrm') else None
        updated.append(line)

    if not updated:
        return 0

    with transaction.atomic():
        VendorShipmentLine.objects.bulk_update(updated, ['confrm'])

    return len(updated)
