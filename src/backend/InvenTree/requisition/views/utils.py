"""Shared helpers for requisition views."""

from purchase_order.models import PurchaseOrderLine


def parse_po_ids(request):
    """Return a de-duplicated list of integer PO ids from ?po=1&po=2 or ?po=1,2."""

    ids = []

    for value in request.query_params.getlist('po'):
        for part in value.split(','):
            part = part.strip()

            if part.isdigit() and int(part) not in ids:
                ids.append(int(part))

    return ids


def get_po_lines(po_ids):
    return (
        PurchaseOrderLine.objects
        .filter(poid__pk__in=po_ids)
        .select_related(
            'poid',
            'poid__prepby',
            'poid__acexeid',
            'costcardid',
            'costcardid__vendor',
            'costcardid__customer',
            'costcardid__sub_category',
            'costcardid__metal_purity',
            'costcardid__metal_purity__metal_type',
        )
        .order_by('poid_id', 'pk')
    )


def group_by_po(po_lines, po_ids):
    grouped = {pk: [] for pk in po_ids}

    for line in po_lines:
        grouped[line.poid_id].append(line)

    return grouped