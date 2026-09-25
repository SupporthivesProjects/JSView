from decimal import ROUND_HALF_UP, Decimal

from django.shortcuts import get_object_or_404

import django_filters.rest_framework.filters as rest_filters
from django_filters.rest_framework.filterset import FilterSet
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveAPI, RetrieveUpdateDestroyAPI

from . import serializers as po_serializers
from .models import PurchaseOrder, PurchaseOrderLine


class PurchaseOrderPagination(LimitOffsetPagination):
    """Default pagination for purchase order list endpoints."""

    default_limit = 10
    max_limit = 100


class PurchaseOrderFilter(FilterSet):
    """Filters for the PurchaseOrder list endpoint.

    Besides the exact-match fields, each table column has its own text filter,
    so that several columns can be searched at once (combined with AND).
    """

    class Meta:
        model = PurchaseOrder
        fields = [
            'potype', 'pocategory', 'customerid', 'vendorid',
            'stampid', 'acexeid', 'termsid', 'prepby', 'active',
        ]

    pono_search = rest_filters.CharFilter(field_name='pono', lookup_expr='icontains')

    # Matches against the ISO date text, e.g. "2026-09" or "2026-09-17"
    podate_search = rest_filters.CharFilter(
        field_name='podate', lookup_expr='icontains',
    )

    customer_search = rest_filters.CharFilter(
        field_name='customerid__name', lookup_expr='icontains',
    )

    vendor_search = rest_filters.CharFilter(
        field_name='vendorid__name', lookup_expr='icontains',
    )

    pocategory_search = rest_filters.CharFilter(
        field_name='pocategory', lookup_expr='icontains',
    )

    tqty_search = rest_filters.CharFilter(method='filter_tqty_search')

    def filter_tqty_search(self, queryset, name, value):
        """Exact match on total quantity; non-numeric input matches nothing."""
        value = value.strip()

        if not value.isdigit():
            return queryset.none()

        return queryset.filter(tqty=int(value))

    prepby_search = rest_filters.CharFilter(
        field_name='prepby__username', lookup_expr='icontains',
    )


class PurchaseOrderList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating PurchaseOrder objects."""

    queryset = PurchaseOrder.objects.select_related(
        'linkid', 'customerid', 'vendorid', 'stampid', 'acexeid', 'termsid', 'prepby',
    ).prefetch_related('lines').all()
    serializer_class = po_serializers.PurchaseOrderSerializer
    pagination_class = PurchaseOrderPagination
    filter_backends = SEARCH_ORDER_FILTER
    filterset_class = PurchaseOrderFilter
    search_fields = ['pono', 'customer_pono', 'rem', 'note', 'prepby__username']
    ordering_fields = ['podate', 'npono', 'createdat', 'tqty']
    ordering = ['-podate', '-npono']


class PurchaseOrderDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single PurchaseOrder object."""

    queryset = PurchaseOrder.objects.select_related(
        'linkid', 'customerid', 'vendorid', 'stampid', 'acexeid', 'termsid', 'prepby',
    ).prefetch_related('lines').all()
    serializer_class = po_serializers.PurchaseOrderSerializer


class PurchaseOrderLineList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating PurchaseOrderLine objects."""

    queryset = PurchaseOrderLine.objects.select_related(
        'poid', 'costcardid', 'vendorid',
    ).all()
    serializer_class = po_serializers.PurchaseOrderLineSerializer
    pagination_class = PurchaseOrderPagination
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['poid', 'costcardid', 'vendorid', 'active']
    search_fields = ['styleno', 'vstyleno']
    ordering_fields = ['pk', 'qty']
    ordering = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        po_pk = self.kwargs.get('pk')
        if po_pk is not None:
            queryset = queryset.filter(poid_id=po_pk)
        return queryset


class PurchaseOrderLineDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single PurchaseOrderLine object."""

    queryset = PurchaseOrderLine.objects.select_related(
        'poid', 'costcardid', 'vendorid',
    ).all()
    serializer_class = po_serializers.PurchaseOrderLineSerializer


# ---------------------------------------------------------------------------
# PO print / report API
#
# Four printable formats are served from a single read-only endpoint:
#
#   vendor          simple PO sheet, order value hidden
#   self            simple PO sheet, order value visible
#   vendor_costcard cost breakdown sheet, amounts hidden
#   self_costcard   cost breakdown sheet, all amounts visible
# ---------------------------------------------------------------------------

PO_PRINT_TYPES = ['vendor', 'self', 'vendor_costcard', 'self_costcard']

PO_PRINT_TYPE_ERROR = (
    'Invalid type. Must be one of: vendor, self, vendor_costcard, self_costcard'
)

ZERO = Decimal('0.00')


def _iso(value) -> str | None:
    """ISO-8601 string for a date value (None-safe)."""
    return value.isoformat() if value else None


def _user_display(user) -> str:
    """Human readable name for a user (empty string when unset)."""
    if not user:
        return ''

    return user.get_full_name() or user.get_username()


def _image_url(request, image) -> str | None:
    """Absolute URL for an ImageField value.

    Images are always returned as URLs (never base64), as required by the
    print views.
    """
    if not image:
        return None

    try:
        return request.build_absolute_uri(image.url)
    except ValueError:
        return None


def _money(value) -> Decimal:
    """Quantise a numeric value to two decimal places."""
    if value in (None, ''):
        return ZERO

    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _number(value):
    """Coerce a text field holding a number back to an int (or leave as-is)."""
    if isinstance(value, str) and value.strip():
        try:
            return int(value)
        except ValueError:
            return value

    return value


def _name_of(value) -> str:
    """String form of a lookup record (None-safe)."""
    return str(value) if value else ''


def _company_display(company, prefer_code: bool = False) -> str:
    """Display name for a Company.

    Customer codes are the short ledger codes printed on the client PO sheet
    (e.g. ``ASC``), so prefer ``code`` and fall back to ``name``.
    """
    if not company:
        return ''

    if prefer_code and company.code:
        return company.code

    return company.name


def _stone_line_from_snapshot(line) -> dict:
    """Normalise a frozen POCostCardLine (values already stored as strings)."""
    return {
        'etype': line.etype,
        'shape': line.shape or '',
        'cut': line.cut or '',
        'mm_size': line.mm_size or '',
        'sieve_size': line.sieve_size or '',
        'stone': line.stone or '',
        'colour': line.colour or '',
        'pointer': line.pointer,
        'pcs': line.pcs or 0,
        'cts': line.cts or Decimal('0'),
        'pc': line.pc or '',
        'rate': line.rate,
        'amount': line.amount,
        'setting': line.setting or '',
        'labour_rate': line.labour_rate,
        'labour_amount': line.labour_amount,
    }


def _stone_line_from_costcard(line, etype: str) -> dict:
    """Normalise a live CostCard stone line (FK lookups flattened to strings)."""
    return {
        'etype': etype,
        'shape': _name_of(line.shape),
        'cut': _name_of(line.cut),
        'mm_size': _name_of(line.mm_size),
        'sieve_size': line.sieve_size or '',
        'stone': _name_of(line.stone),
        'colour': _name_of(line.color),
        'pointer': line.pointer,
        'pcs': line.pcs or 0,
        'cts': line.cts or Decimal('0'),
        'pc': line.pc or '',
        'rate': line.rate,
        'amount': line.amount,
        'setting': _name_of(line.setting),
        'labour_rate': line.labour_rate,
        'labour_amount': line.labour_amount,
    }


def _snapshot_cost_data(snapshot) -> dict:
    """Normalised cost-card data taken from a frozen POCostCard snapshot."""
    lines = list(snapshot.lines.all())
    costcard = snapshot.costcard

    return {
        'costcard': costcard,
        'cc_no': snapshot.costcardno or '',
        'style_no': snapshot.our_style_no or '',
        'v_style_no': snapshot.vendor_style_no or '',
        'customer': _company_display(snapshot.customer, prefer_code=True),
        'vendor': _company_display(snapshot.vendor),
        'vendor_address': (snapshot.vendor.address or '') if snapshot.vendor else '',
        'category': snapshot.category.name if snapshot.category else '',
        'sub_category': snapshot.sub_category.name if snapshot.sub_category else '',
        'metal_type': snapshot.metal_purity.name if snapshot.metal_purity else '',
        'troy_oz': snapshot.troy_ounce_price or Decimal('0'),
        'kt': _number(snapshot.karat),
        'net_wt': snapshot.net_weight or Decimal('0'),
        'loss_pct': snapshot.metal_loss_pct or Decimal('0'),
        'metal_amount': _money(snapshot.metal_amount),
        'stone_pcs': snapshot.stone_pcs or 0,
        'stone_cts': snapshot.stone_cts or Decimal('0'),
        'stone_amount': _money(snapshot.stone_amount),
        'labour_amount': _money(snapshot.labour_amount),
        'markup_pct': snapshot.vendor_markup_pct or Decimal('0'),
        'duty_pct': snapshot.duty_pct or Decimal('0'),
        'margin_pct': snapshot.margin_pct or Decimal('0'),
        'fob': _money(snapshot.fob),
        'design_instruction': (costcard.design_note or '') if costcard else '',
        'stone_lines': [
            _stone_line_from_snapshot(line)
            for line in lines
            if line.etype != 'FINISHTYPE'
        ],
        'finish_lines': [
            {'finish': line.stone or '', 'rate': line.rate, 'amount': line.amount}
            for line in lines
            if line.etype == 'FINISHTYPE'
        ],
    }


def _live_cost_data(card) -> dict:
    """Normalised cost-card data taken from a live (unfrozen) CostCard.

    Purchase REQUESTs never freeze a snapshot, so their print sheets are built
    straight from the live cost card.
    """
    return {
        'costcard': card,
        'cc_no': card.cost_card_no or '',
        'style_no': card.our_style_no or '',
        'v_style_no': card.vendor_style_no or '',
        'customer': _company_display(card.customer, prefer_code=True),
        'vendor': _company_display(card.vendor),
        'vendor_address': (card.vendor.address or '') if card.vendor else '',
        'category': card.category.name if card.category else '',
        'sub_category': card.sub_category.name if card.sub_category else '',
        'metal_type': card.metal_purity.name if card.metal_purity else '',
        'troy_oz': card.troy_ounce_price or Decimal('0'),
        'kt': _number(card.karat),
        'net_wt': card.net_weight or Decimal('0'),
        'loss_pct': card.metal_loss_pct or Decimal('0'),
        'metal_amount': _money(card.metal_amount),
        'stone_pcs': card.stone_pcs or 0,
        'stone_cts': card.stone_cts or Decimal('0'),
        'stone_amount': _money(card.stone_amount),
        'labour_amount': _money(card.labour_amount),
        'markup_pct': card.vendor_markup_pct or Decimal('0'),
        'duty_pct': card.duty_pct or Decimal('0'),
        'margin_pct': card.margin_pct or Decimal('0'),
        'fob': _money(card.fob),
        'design_instruction': card.design_note or '',
        'stone_lines': [
            _stone_line_from_costcard(line, 'DIAMOND')
            for line in card.diamond_lines.all()
        ] + [
            _stone_line_from_costcard(line, 'COLOURSTONE')
            for line in card.colorstone_lines.all()
        ],
        'finish_lines': [
            {'finish': _name_of(line.finish_type), 'rate': line.rate, 'amount': line.rate}
            for line in card.finish_lines.all()
        ],
    }


def _cost_data_for_po(po) -> list[dict]:
    """Normalised cost-card data for every printable line of ``po``.

    Prefers the frozen POCostCard snapshot (created when an ORDER line with a
    cost card is saved) and falls back to the live cost card when no snapshot
    exists. Order follows the PO line order, and each cost card is only
    emitted once even when several lines reference it.
    """
    snapshots = {
        snapshot.costcard_id: snapshot
        for snapshot in po.po_costcards.select_related(
            'costcard', 'vendor', 'customer', 'category', 'sub_category', 'metal_purity',
        ).prefetch_related('lines')
        if snapshot.costcard_id
    }

    blocks = []
    seen = set()

    for line in po.lines.select_related('costcardid').all():
        card = line.costcardid

        if not card or card.pk in seen:
            continue

        seen.add(card.pk)
        snapshot = snapshots.get(card.pk)
        blocks.append(
            _snapshot_cost_data(snapshot) if snapshot else _live_cost_data(card)
        )

    # Snapshots whose original cost card was deleted still hold printable data.
    for card_id, snapshot in snapshots.items():
        if card_id not in seen:
            seen.add(card_id)
            blocks.append(_snapshot_cost_data(snapshot))

    return blocks


def _modified_by(card, po) -> str:
    """User who last modified the cost card, falling back to the PO preparer."""
    if card is not None:
        version = card.versions.order_by('-version').first()

        if version and version.created_by:
            return _user_display(version.created_by)

    return _user_display(po.prepby)


def build_po_header(po, request) -> dict:
    """PO header block shared by all four print formats."""
    stamp = po.stampid

    return {
        'pono': po.pono,
        'podate': _iso(po.podate),
        'ddate': _iso(po.ddate),
        'pocategory': po.pocategory or '',
        'customer': _company_display(po.customerid, prefer_code=True),
        'vendor': _company_display(po.vendorid),
        'vendor_address': (po.vendorid.address or '') if po.vendorid else '',
        'prepby': _user_display(po.prepby),
        'acexe': po.acexeid.name if po.acexeid else '',
        'terms': po.termsid.name if po.termsid else '',
        'stamp': stamp.name if stamp else '',
        'stamp_image': _image_url(request, stamp.image) if stamp else None,
        'rem': po.rem or '',
    }


def build_simple_lines(po, include_order_value: bool) -> tuple[list[dict], dict]:
    """Line + totals block for the simple ``vendor`` / ``self`` formats.

    The order value is only revealed for the ``self`` format; the vendor sheet
    must never expose it.
    """
    snapshots = {
        snapshot.costcard_id: snapshot
        for snapshot in po.po_costcards.select_related('metal_purity').all()
        if snapshot.costcard_id
    }

    lines = []
    total_qty = 0
    metal_value = ZERO
    labour_value = ZERO
    order_value = ZERO

    for index, line in enumerate(po.lines.select_related('costcardid').all(), start=1):
        card = line.costcardid
        source = snapshots.get(card.pk) if card else None

        if source is None:
            source = card

        lines.append({
            'sr': index,
            'style_no': line.styleno or '',
            'v_style_no': line.vstyleno or '',
            'qty': line.qty or 0,
            'size': line.size or '',
            'size_pcs': line.spcs or '',
            'metal_color_kt': source.metal_purity.name if source and source.metal_purity else '',
        })

        total_qty += line.qty or 0

        if source is not None:
            metal_value += source.metal_amount or Decimal('0')
            labour_value += source.labour_amount or Decimal('0')
            order_value += source.final_amount or Decimal('0')

    totals = {
        'total_qty': total_qty,
        'metal_value': _money(metal_value),
        'labour_value': _money(labour_value),
    }

    if include_order_value:
        totals['order_value'] = _money(order_value)

    return lines, totals


def build_costcard_block(data: dict, po, request, show_amounts: bool) -> dict:
    """Build one printable cost-card sheet.

    ``show_amounts=False`` produces the vendor sheet (amounts, labour rates and
    the pricing summary are hidden); ``show_amounts=True`` produces the full
    internal sheet.
    """
    stone_lines = [
        {
            'etype': line['etype'],
            'shape': line['shape'],
            'cut': line['cut'],
            'mm_size': line['mm_size'],
            'sieve_size': line['sieve_size'],
            'stone': line['stone'],
            'colour': line['colour'],
            'pointer': line['pointer'],
            'pcs': line['pcs'],
            'cts': line['cts'],
            'pc': line['pc'],
            'rate': line['rate'],
            'amount': line['amount'] if show_amounts else None,
            'setting': line['setting'],
            'labour_rate': line['labour_rate'] if show_amounts else None,
            'labour_amount': line['labour_amount'] if show_amounts else None,
        }
        for line in data['stone_lines']
    ]

    # The labour breakdown is derived from the frozen lines, so it stays
    # correct even after the original cost card has been deleted.
    finish_labour = _money(
        sum((line['amount'] or Decimal('0')) for line in data['finish_lines'])
    )
    diamond_labour = _money(
        sum(
            (line['labour_amount'] or Decimal('0'))
            for line in data['stone_lines']
            if line['etype'] == 'DIAMOND'
        )
    )
    colorstone_labour = _money(
        sum(
            (line['labour_amount'] or Decimal('0'))
            for line in data['stone_lines']
            if line['etype'] == 'COLOURSTONE'
        )
    )
    labour_total = data['labour_amount'] or _money(
        finish_labour + diamond_labour + colorstone_labour
    )

    metal = data['metal_amount']
    studding = data['stone_amount']
    other = ZERO
    fob = data['fob'] or _money(metal + studding + labour_total + other)

    markup_pct = data['markup_pct']
    duty_pct = data['duty_pct']
    margin_pct = data['margin_pct']

    after_markup = fob * (1 + markup_pct / 100) if markup_pct else fob
    with_markup = after_markup if markup_pct else ZERO
    with_duty = _money(after_markup * (1 + duty_pct / 100))
    final_price = _money(after_markup * (1 + duty_pct / 100) * (1 + margin_pct / 100))

    summary = {'metal': metal}
    if show_amounts:
        summary['studding'] = studding
    summary['labour'] = labour_total
    summary['none'] = other
    if show_amounts:
        summary['fob'] = fob
        summary['markup_pct'] = markup_pct
        summary['with_markup'] = _money(with_markup)
        summary['duty_pct'] = duty_pct
        summary['with_duty'] = with_duty
        summary['margin_pct'] = margin_pct
        summary['final_price'] = final_price

    card = data['costcard']

    return {
        'cc_no': data['cc_no'],
        'style_no': data['style_no'],
        'v_style_no': data['v_style_no'],
        'customer': data['customer'],
        'vendor': data['vendor'],
        'vendor_address': data['vendor_address'],
        'category': data['category'],
        'sub_category': data['sub_category'],
        'date': _iso(po.podate),
        'modified_by': _modified_by(card, po),
        'images': {
            'front': _image_url(request, card.front_view) if card else None,
            'side': _image_url(request, card.side_view) if card else None,
            'back': _image_url(request, card.back_view) if card else None,
        },
        'metal': {
            'type': data['metal_type'],
            'troy_oz': data['troy_oz'],
            'kt': data['kt'],
            'net_wt': data['net_wt'],
            'loss_pct': data['loss_pct'],
            'metal_amount': metal,
        },
        'stone_lines': stone_lines,
        'stone_totals': {
            'total_pcs': data['stone_pcs'],
            'total_cts': data['stone_cts'],
            'total_amount': studding if show_amounts else None,
        },
        'labour': {
            'finish': finish_labour,
            'diamond': diamond_labour,
            'colorstone': colorstone_labour,
        },
        'summary': summary,
        'design_instruction': data['design_instruction'],
    }


def build_costcards(po, show_amounts: bool, request) -> list[dict]:
    """Printable cost-card sheets for a PO (amounts visible or hidden)."""
    return [
        build_costcard_block(data, po, request, show_amounts)
        for data in _cost_data_for_po(po)
    ]


class POPrintView(RetrieveAPI):
    """Read-only print/report endpoint for a Purchase Order.

    GET /api/purchase-order/po/<pk>/print/?type=<type>

    Returns structured data for the four print formats rendered by the PO
    detail page: ``vendor``, ``self``, ``vendor_costcard`` and
    ``self_costcard``. The React frontend turns this JSON into the print view.
    """

    queryset = PurchaseOrder.objects.all()
    serializer_class = po_serializers.PurchaseOrderSerializer

    def get(self, request, pk):
        """Build the requested print payload (no write operations)."""
        print_type = request.query_params.get('type', '')

        if print_type not in PO_PRINT_TYPES:
            return Response(
                {'error': PO_PRINT_TYPE_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )

        po = get_object_or_404(
            PurchaseOrder.objects.select_related(
                'customerid', 'vendorid', 'stampid', 'acexeid', 'termsid', 'prepby',
            ),
            pk=pk,
        )

        data = {'type': print_type, 'po': build_po_header(po, request)}

        if print_type in ('vendor', 'self'):
            lines, totals = build_simple_lines(
                po, include_order_value=(print_type == 'self')
            )
            data['lines'] = lines
            data['totals'] = totals
        else:
            data['costcards'] = build_costcards(
                po,
                show_amounts=(print_type == 'self_costcard'),
                request=request,
            )

        return Response(data)
