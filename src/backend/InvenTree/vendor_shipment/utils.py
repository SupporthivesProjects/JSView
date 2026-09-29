"""Helper functions for the 'vendor_shipment' app.

These replicate the PostgreSQL functions used by the legacy Go server, using
the Django ORM against the local database tables:

  * ``fn_po_vendorstatus(vendorid, opcl)``    -> :func:`get_vendor_po_list`
  * ``fn_vendor_style(poid, opcl)``           -> :func:`get_vendor_style_list`
  * ``fn_tbvendorship1_vendorpo(vendorid)``   -> :func:`get_confirm_pending_invoices`
  * ``fn_tbvendorship_data(vendorid, vsid)``  -> :func:`get_confirm_pending_data`
"""

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from purchase_order.models import POCostCard, PurchaseOrder, PurchaseOrderLine

from .models import VendorShipment, VendorShipmentLine

ZERO = Decimal('0')


def _po_status_maps(po_ids):
    """Ordered vs received quantity per ``(poid, original cost card id)``.

    Returns two dicts keyed by ``(poid, costcard_id)``:

    * ``ordered``  — sum of ``PurchaseOrderLine.qty``
    * ``received`` — sum of ``VendorShipmentLine.pcs``

    Shipment lines point at a :class:`POCostCard` snapshot, so the original
    cost card id is resolved through ``costcardid__costcard_id`` to make the
    comparison against the PO lines possible.
    """
    po_ids = list(po_ids)
    ordered = {}
    received = {}

    if not po_ids:
        return ordered, received

    for row in (
        PurchaseOrderLine.objects
        .filter(poid_id__in=po_ids, costcardid__isnull=False)
        .values('poid_id', 'costcardid_id')
        .annotate(total=Sum('qty'))
    ):
        ordered[(row['poid_id'], row['costcardid_id'])] = row['total'] or 0

    for row in (
        VendorShipmentLine.objects
        .filter(poid_id__in=po_ids, costcardid__costcard__isnull=False)
        .values('poid_id', 'costcardid__costcard_id')
        .annotate(total=Sum('pcs'))
    ):
        key = (row['poid_id'], row['costcardid__costcard_id'])
        received[key] = received.get(key, 0) + (row['total'] or 0)

    return ordered, received


def get_vendor_po_list(vendorid=None, is_open=True):
    """Replicate ``fn_po_vendorstatus``.

    Returns a list of ``{'poid', 'pono'}`` for the given vendor.

    * ``is_open=True``  -> purchase orders which are not fully shipped
      (received qty < ordered qty for at least one cost card)
    * ``is_open=False`` -> purchase orders which are fully shipped
    """
    po_qs = PurchaseOrder.objects.filter(potype='ORDER', active=True)

    if vendorid:
        po_qs = po_qs.filter(vendorid_id=vendorid)

    po_map = {po.pk: po.pono for po in po_qs.only('pk', 'pono')}

    if not po_map:
        return []

    ordered, received = _po_status_maps(po_map.keys())

    with_lines = {key[0] for key in ordered}
    open_po_ids = {
        key[0]
        for key, qty in ordered.items()
        if received.get(key, 0) < qty
    }

    selected = open_po_ids if is_open else (with_lines - open_po_ids)

    return [
        {'poid': po_id, 'pono': po_map[po_id]}
        for po_id in sorted(selected)
    ]


def get_vendor_style_list(poid, is_open=True):
    """Replicate ``fn_vendor_style``.

    Returns a list of ``{'costcardid', 'styleno', 'costcard'}`` for the styles
    of a purchase order. ``costcardid`` is the :class:`POCostCard` snapshot id
    (the value stored on :class:`VendorShipmentLine`), while ``costcard`` is
    the original ``costcard.CostCard`` id.

    * ``is_open=True``  -> styles which are not fully shipped
    * ``is_open=False`` -> styles which are fully shipped
    """
    if not poid:
        return []

    snapshots = list(
        POCostCard.objects
        .filter(poid_id=poid, active=True)
        .select_related('costcard')
        .order_by('id')
    )

    if not snapshots:
        return []

    ordered = {}
    for row in (
        PurchaseOrderLine.objects
        .filter(poid_id=poid, costcardid__isnull=False)
        .values('costcardid_id')
        .annotate(total=Sum('qty'))
    ):
        ordered[row['costcardid_id']] = row['total'] or 0

    received = {}
    for row in (
        VendorShipmentLine.objects
        .filter(poid_id=poid, costcardid__costcard__isnull=False)
        .values('costcardid__costcard_id')
        .annotate(total=Sum('pcs'))
    ):
        received[row['costcardid__costcard_id']] = row['total'] or 0

    result = []

    for snapshot in snapshots:
        costcard_id = snapshot.costcard_id
        ordered_qty = ordered.get(costcard_id, 0)
        received_qty = received.get(costcard_id, 0)

        if (received_qty < ordered_qty) != is_open:
            continue

        style_no = snapshot.our_style_no
        if not style_no and snapshot.costcard:
            style_no = snapshot.costcard.our_style_no

        result.append({
            'costcardid': snapshot.pk,
            'styleno': style_no or '',
            'costcard': costcard_id,
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
    purchase order, the ordered quantity and the frozen PO cost card values
    so the confirmation screen can compare received vs ordered.
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
        costcard_id = costcard.costcard_id if costcard else None
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


def update_confirm_flags(entries):
    """Bulk update the ``confrm`` flag of shipment lines.

    ``entries`` is a list of ``{'tableid': <line pk>, 'confrm': <bool>}``.
    A truthy ``confrm`` marks the line as confirmed; any falsy / missing value
    resets it to the pending state (``NULL``), matching the legacy semantics
    where ``confrm IS NULL`` means "not confirmed yet".

    Returns the number of lines that were updated.
    """
    if not entries:
        return 0

    def _to_pk(entry):
        try:
            return int(entry.get('tableid'))
        except (AttributeError, TypeError, ValueError):
            return None

    ids = [pk for pk in (_to_pk(entry) for entry in entries) if pk is not None]

    if not ids:
        return 0

    lines = {
        line.pk: line
        for line in VendorShipmentLine.objects.filter(pk__in=ids)
    }

    updated = []

    for entry in entries:
        pk = _to_pk(entry)

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
