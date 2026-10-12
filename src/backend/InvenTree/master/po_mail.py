import re
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template import Context, Template
from django.template.loader import get_template
from django.templatetags.static import static
from common.settings import get_global_setting
from .models import POMail

LOGO_STATIC_PATH = 'logos/logo_for_excel_sheet.png'
CENT = Decimal('0.01')

COMPANY_PROFILE = {
    'name': 'Jewel Source Inc.',
    'address_line1': '45 West 45th Street, 9th Floor',
    'address_line2': 'New York, NY 10036, USA',
    'phone': '1-212-3910312',
    'email': 'sarju@jewelsourceinc.com',
    'website': 'www.jsiview.com',
    'reg_line': '',
    'gstin': '',
}

FORMATS = (
    ('vendor', 'format1', 'Vendor'),
    ('diamond_office', 'format2', 'Diamond Office'),
    ('color_stone_office', 'format3', 'Color Stone Office'),
    ('new_york_office', 'format4', 'New York Office'),
)

FORMAT_FIELDS = {key: field for key, field, _label in FORMATS}

DEFAULT_TEMPLATES = {
    key: f'master/purchase_emails/{key}.html' for key, _field, _label in FORMATS
}

STONE_KEYS = ('stone', 'shape', 'mm_size', 'colour', 'quality')


def logo_url(base_url):
    try:
        path = static(LOGO_STATIC_PATH)
    except Exception:
        path = f"{settings.STATIC_URL or '/static/'}{LOGO_STATIC_PATH}"

    if path.startswith(('http://', 'https://')):
        return path

    base = (base_url or getattr(settings, 'SITE_URL', '') or '').rstrip('/')

    if not base:
        return ''

    return f"{base}{path if path.startswith('/') else '/' + path}"


@lru_cache(maxsize=1)
def purchase_order_model():
    for model in apps.get_models():
        if model.__name__ == 'PurchaseOrder' and any(
            field.name == 'pono' for field in model._meta.get_fields()
        ):
            return model

    raise LookupError('Purchase order model with a pono field was not found.')


def get_order(pk):
    try:
        value = int(pk)
    except (TypeError, ValueError):
        return None

    return (
        purchase_order_model()
        .objects.select_related('vendorid', 'customerid', 'termsid', 'prepby')
        .filter(pk=value)
        .first()
    )


def order_choices(search='', potype='', limit=50):
    queryset = purchase_order_model().objects.filter(active=True, canc_dt__isnull=True).select_related(
        'vendorid', 'customerid'
    )

    if search:
        queryset = queryset.filter(pono__icontains=search)

    if potype:
        queryset = queryset.filter(potype=potype.upper())

    return [
        {
            'id': order.pk,
            'po_number': order.pono,
            'po_type': order.potype,
            'po_date': fmt_date(order.podate),
            'customer': order.customerid.name if order.customerid else '',
            'vendor': order.vendorid.name if order.vendorid else '',
        }
        for order in queryset.order_by('-podate', '-npono')[:limit]
    ]


def order_blocked(order):
    if order.canc_dt:
        return 'Purchase order is cancelled.'

    if not order.active:
        return 'Purchase order is inactive.'

    return ''


def active_mail(pk=None):
    queryset = POMail.objects.filter(active=True).select_related(
        'format1', 'format2', 'format3', 'format4'
    )

    if pk:
        try:
            return queryset.filter(pk=int(pk)).first()
        except (TypeError, ValueError):
            return None

    return queryset.order_by('order').first()


def format_template(mail, field):
    template = getattr(mail, field, None) if mail else None

    if template is not None and template.active:
        return template

    return None


def split_emails(value):
    return [item.strip() for item in re.split(r'[;,]', value or '') if item.strip()]


def unique_emails(value):
    seen = set()
    result = []

    for item in split_emails(value):
        marker = item.lower()

        if marker not in seen:
            seen.add(marker)
            result.append(item)

    return result


def label(value):
    if value is None or value == '':
        return ''

    return getattr(value, 'name', None) or str(value)


def to_decimal(value):
    value = getattr(value, 'amount', value)

    if value is None or value == '':
        return Decimal(0)

    return Decimal(str(value))


def dec(obj, name):
    return to_decimal(getattr(obj, name, None))


def rounded(value, places=CENT):
    return value.quantize(places, rounding=ROUND_HALF_UP)


def fixed(value):
    return f'{rounded(value)}'


def number(value):
    return format(value.normalize(), 'f')


def money(value):
    amount = getattr(value, 'amount', value)

    if amount is None or amount == '':
        return ''

    return f'{rounded(Decimal(str(amount))):,.2f}'


def fmt_date(value):
    return value.strftime('%d %b %Y') if value else ''


def company_email(company):
    if company is None:
        return ''

    return (getattr(company, 'email', '') or '').strip()


def company_address(company):
    if company is None:
        return ''

    address = getattr(company, 'address', '') or ''

    if address:
        return str(address)

    return ', '.join(
        part for part in (company.city, company.state, company.country) if part
    )


def party(company):
    if company is None:
        return None

    return {
        'id': company.pk,
        'code': company.code,
        'name': company.name,
        'email': company_email(company),
        'contact': company.contact,
        'phone': company.phone,
        'tax_id': company.tax_id,
        'address': company_address(company),
    }


def line_vendor(order, line):
    return line.vendorid or order.vendorid


def order_lines(order):
    return list(order.lines.filter(active=True).select_related('costcardid'))


def line_cards(order, lines):
    snapshots = {
        snapshot.costcard_id: snapshot
        for snapshot in order.po_costcards.filter(active=True)
        .select_related('metal_purity__metal_type', 'category', 'sub_category')
        .prefetch_related('lines')
    }

    return [(line, snapshots.get(line.costcardid_id) or line.costcardid) for line in lines]


def order_vendors(order, lines):
    vendors = []
    seen = set()

    for line in lines:
        vendor = line_vendor(order, line)

        if vendor is not None and vendor.pk not in seen:
            seen.add(vendor.pk)
            vendors.append(vendor)

    if not vendors and order.vendorid is not None:
        vendors.append(order.vendorid)

    return vendors


def vendor_emails(vendors):
    return ', '.join(dict.fromkeys(email for email in map(company_email, vendors) if email))


def size_text(line):
    sizes = split_emails(line.size)
    pieces = split_emails(line.spcs)

    if sizes and len(sizes) == len(pieces):
        return ', '.join(f'{size} ({count})' for size, count in zip(sizes, pieces))

    return line.size or ''


def card_description(card):
    sub_category = label(getattr(card, 'sub_category', None))
    category = label(getattr(card, 'category', None))

    return sub_category or category


def order_items(order, pairs):
    items = []

    for line, card in pairs:
        qty = dec(line, 'qty')
        weight = dec(card, 'net_weight')
        purity = getattr(card, 'metal_purity', None)
        description = card_description(card) or line.styleno

        if line.vstyleno and line.styleno and description != line.styleno:
            description = f'{description} (our style {line.styleno})'

        amount = rounded(dec(card, 'fob') * qty)

        items.append({
            'code': line.vstyleno or line.styleno,
            'description': description,
            'metal': label(getattr(purity, 'metal_type', None)),
            'purity': getattr(card, 'karat', '') or label(purity),
            'size': size_text(line),
            'net_weight': fixed(weight) if weight else '',
            'weight_value': weight * qty,
            'quantity': number(qty),
            'quantity_value': qty,
            'amount': money(amount),
            'amount_value': amount,
        })

    return items


def stone_lines(card):
    related = getattr(card, 'lines', None)

    if related is None or not hasattr(related, 'all'):
        return []

    return list(related.all())


def stone_rows(pairs, etype):
    grouped = {}

    for line, card in pairs:
        qty = dec(line, 'qty')

        for stone_line in stone_lines(card):
            if getattr(stone_line, 'etype', '') != etype:
                continue

            key = tuple(label(getattr(stone_line, field, '')) for field in STONE_KEYS)
            row = grouped.setdefault(key, {'pcs': Decimal(0), 'cts': Decimal(0)})
            row['pcs'] += dec(stone_line, 'pcs') * qty
            row['cts'] += dec(stone_line, 'cts') * qty

    return [
        {
            'stone': key[0],
            'shape': key[1],
            'size': key[2],
            'colour': key[3],
            'quality': key[4],
            'pcs': int(rounded(row['pcs'], Decimal(1))),
            'cts': rounded(row['cts']),
        }
        for key, row in sorted(grouped.items())
    ]


def cost_rows(pairs):
    rows = []

    for line, card in pairs:
        qty = dec(line, 'qty')
        metal = rounded(dec(card, 'metal_amount') * qty)
        stones = rounded(dec(card, 'stone_amount') * qty)
        labour = rounded(dec(card, 'labour_amount') * qty)
        total = rounded(dec(card, 'final_amount') * qty)

        rows.append({
            'style': line.styleno,
            'quantity': qty,
            'metal': metal,
            'stones': stones,
            'labour': labour,
            'other': total - metal - stones - labour,
            'total': total,
        })

    return rows


def subject_context(order):
    vendors = order_vendors(order, order_lines(order))

    return {
        'po_number': order.pono,
        'po_type': order.get_potype_display(),
        'po_date': fmt_date(order.podate),
        'supplier_name': vendors[0].name if vendors else '',
        'customer_name': order.customerid.name if order.customerid else '',
        'company_name': get_global_setting('INVENTREE_COMPANY_NAME') or COMPANY_PROFILE['name'],
    }


def default_email(template, key, vendor):
    if template is not None and template.recipients:
        return template.recipients

    if key == 'vendor':
        return vendor

    return ''


def mail_options(order, mail):
    vendors = order_vendors(order, order_lines(order))
    vendor = vendor_emails(vendors)
    customer = company_email(order.customerid)
    context = subject_context(order)
    formats = []

    for key, field, label_text in FORMATS:
        template = format_template(mail, field)
        formats.append({
            'key': key,
            'label': label_text,
            'active': template is not None,
            'template': template.pk if template else None,
            'template_name': template.name if template else None,
            'subject': render_subject(template, context) if template else '',
            'email': default_email(template, key, vendor),
            'attachments': '',
        })

    return {
        'order': order.pk,
        'po_number': order.pono,
        'po_type': order.potype,
        'cancelled': bool(order.canc_dt),
        'mail': mail.pk if mail else None,
        'vendor': party(vendors[0]) if vendors else None,
        'vendors': [party(item) for item in vendors],
        'customer': party(order.customerid),
        'vendor_email': vendor,
        'customer_email': customer,
        'formats': formats,
    }


def build_context(order, vendor=None):
    lines = order_lines(order)

    if isinstance(vendor, (list, tuple, set)):
        selected = list(vendor)
    elif vendor is not None:
        selected = [vendor]
    else:
        selected = []

    if selected:
        selected_ids = {item.pk for item in selected}
        lines = [
            line for line in lines
            if line_vendor(order, line) is not None and line_vendor(order, line).pk in selected_ids
        ]

    pairs = line_cards(order, lines)
    items = order_items(order, pairs)
    vendors = order_vendors(order, lines)
    supplier = selected[0] if selected else (vendors[0] if vendors else None)
    creator = order.prepby
    base_url = (get_global_setting('INVENTREE_BASE_URL') or '').rstrip('/')
    company_name = get_global_setting('INVENTREE_COMPANY_NAME') or COMPANY_PROFILE['name']
    delivery_date = fmt_date(order.ddate)
    stones_needed_by = fmt_date(order.esdstone) or delivery_date
    ship_date = fmt_date(order.vcsdate) or delivery_date
    company_address_text = ', '.join(
        part for part in (COMPANY_PROFILE['address_line1'], COMPANY_PROFILE['address_line2']) if part
    )

    vendor_total = sum((item['amount_value'] for item in items), Decimal(0))
    total_weight = sum((item['weight_value'] for item in items), Decimal(0))
    total_qty = sum((item['quantity_value'] for item in items), Decimal(0))

    diamonds = stone_rows(pairs, 'DIAMOND')
    colour_stones = stone_rows(pairs, 'COLOURSTONE')
    costs = cost_rows(pairs)

    return {
        'po_number': order.pono,
        'po_type': order.get_potype_display(),
        'po_date': fmt_date(order.podate),
        'delivery_date': delivery_date,
        'confirm_by_date': delivery_date,
        'payment_terms': order.termsid.name if order.termsid else '',
        'currency': getattr(supplier, 'currency_code', '') if supplier else '',
        'preheader': f'New purchase {order.get_potype_display().lower()} {order.pono} from {company_name}.',
        'supplier_name': supplier.name if supplier else '',
        'supplier_contact': (supplier.contact or supplier.name) if supplier else '',
        'supplier_address': company_address(supplier),
        'supplier_gstin': supplier.tax_id if supplier else '',
        'customer_name': order.customerid.name if order.customerid else '',
        'customer_po_no': order.customer_pono,
        'delivery_address': company_address_text,
        'items': items,
        'total_net_weight': fixed(total_weight),
        'subtotal': money(vendor_total),
        'gst_percent': '',
        'gst_amount': '',
        'grand_total': money(vendor_total),
        'order_notes': order.rem or '',
        'weight_tolerance': '',
        'po_view_url': f'{base_url}/web/purchasing/purchase-order/{order.pk}' if base_url else '',
        'buyer_name': (creator.get_full_name() or creator.get_username()) if creator else '',
        'buyer_email': creator.email if creator else '',
        'buyer_phone': '',
        'attachment_names': '',
        'stones_needed_by': stones_needed_by,
        'diamonds': [
            {
                'shape': row['shape'],
                'size': row['size'],
                'color': row['colour'],
                'clarity': row['quality'],
                'pcs': row['pcs'],
                'weight': fixed(row['cts']),
            }
            for row in diamonds
        ],
        'total_diamond_pcs': sum(row['pcs'] for row in diamonds),
        'total_diamond_ct': fixed(sum((row['cts'] for row in diamonds), Decimal(0))),
        'stones': [
            {
                'name': row['stone'],
                'shape': row['shape'],
                'size': row['size'],
                'colour': row['colour'],
                'quality': row['quality'],
                'pcs': row['pcs'],
                'weight': fixed(row['cts']),
            }
            for row in colour_stones
        ],
        'total_color_pcs': sum(row['pcs'] for row in colour_stones),
        'total_color_ct': fixed(sum((row['cts'] for row in colour_stones), Decimal(0))),
        'ny_eta': ship_date,
        'ny_address': company_address_text,
        'costs': [
            {
                'style': row['style'],
                'quantity': number(row['quantity']),
                'metal': money(row['metal']),
                'stones': money(row['stones']),
                'labour': money(row['labour']),
                'other': money(row['other']),
                'total': money(row['total']),
            }
            for row in costs
        ],
        'total_qty': number(total_qty),
        'total_metal': money(sum((row['metal'] for row in costs), Decimal(0))),
        'total_stones': money(sum((row['stones'] for row in costs), Decimal(0))),
        'total_labour': money(sum((row['labour'] for row in costs), Decimal(0))),
        'total_other': money(sum((row['other'] for row in costs), Decimal(0))),
        'ny_total': money(sum((row['total'] for row in costs), Decimal(0))),
        'company_name': company_name,
        'company_logo_url': logo_url(base_url),
        'company_address_line1': COMPANY_PROFILE['address_line1'],
        'company_address_line2': COMPANY_PROFILE['address_line2'],
        'company_phone': COMPANY_PROFILE['phone'],
        'company_email': COMPANY_PROFILE['email'],
        'company_website': COMPANY_PROFILE['website'],
        'company_reg_line': COMPANY_PROFILE['reg_line'],
        'company_gstin': COMPANY_PROFILE['gstin'],
        'custom_message': '',
    }


def render_body(template, key, context):
    code = (template.code or '').strip() if template else ''

    if code:
        return Template(code).render(Context(context))

    return get_template(DEFAULT_TEMPLATES[key]).render(context)


def render_subject(template, context):
    subject = (template.subject or '').strip() if template else ''

    if subject:
        return ' '.join(Template(subject).render(Context(context)).split())

    return f"Purchase {context['po_type']} {context['po_number']}"


def deliver(key, template, entered, context, subject_text):
    recipients = unique_emails(entered)

    if not recipients:
        return False, {'key': key, 'email': entered, 'error': 'No recipient email.'}

    try:
        for recipient in recipients:
            validate_email(recipient)
    except ValidationError:
        return False, {'key': key, 'email': entered, 'error': 'Invalid email address.'}

    try:
        html = render_body(template, key, context)
        subject = ' '.join((subject_text or '').split()) or render_subject(template, context)
        message = EmailMultiAlternatives(
            subject,
            f"Purchase {context['po_type']} {context['po_number']} from {context['company_name']}. "
            'Please view this email in an HTML-capable client.',
            settings.DEFAULT_FROM_EMAIL,
            recipients,
        )
        message.attach_alternative(html, 'text/html')
        message.send()
    except Exception as exc:
        return False, {'key': key, 'email': ', '.join(recipients), 'error': str(exc)}

    return True, {
        'key': key,
        'email': ', '.join(recipients),
        'subject': subject,
        'vendor': context['supplier_name'] if key == 'vendor' else None,
    }


def send_selected(order, mail, selections):
    defaults = {item['key']: item['email'] for item in mail_options(order, mail)['formats']}
    vendors = order_vendors(order, order_lines(order))
    sent = []
    failed = []
    handled = set()

    for selection in selections:
        if not isinstance(selection, dict):
            failed.append({'key': None, 'email': '', 'error': 'Invalid selection.'})
            continue

        key = selection.get('key')
        field = FORMAT_FIELDS.get(key)
        entered = selection.get('email') or defaults.get(key, '')

        if field is None:
            failed.append({'key': key, 'email': entered, 'error': 'Unknown mail type.'})
            continue

        if key in handled:
            continue

        handled.add(key)

        template = format_template(mail, field)

        if template is None:
            failed.append({'key': key, 'email': entered, 'error': 'No active template for this mail type.'})
            continue

        if key == 'vendor' and len(vendors) > 1:
            grouped = {}

            for item in vendors:
                address = company_email(item)
                grouped.setdefault(address.lower(), (address, []))[1].append(item)

            targets = [(address, group) for address, group in grouped.values()]
        elif key == 'vendor' and vendors:
            targets = [(entered, [vendors[0]])]
        else:
            targets = [(entered, None)]

        for recipient, vendor_group in targets:
            context = dict(build_context(order, vendor_group), custom_message=selection.get('message') or '')
            ok, record = deliver(key, template, recipient, context, selection.get('subject'))
            (sent if ok else failed).append(record)

    return {'sent': sent, 'failed': failed}