import mimetypes
import re
from decimal import Decimal
from functools import lru_cache
from io import BytesIO

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template import Context, Template
from django.template.loader import get_template

from common.settings import get_global_setting

from .models import POMail

COMPANY_PROFILE = {
    'name': '',
    'logo_url': '',
    'address_line1': '',
    'address_line2': '',
    'phone': '',
    'email': '',
    'website': '',
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


def pdf_attachment(template_name):
    def build(context):
        from weasyprint import HTML

        return HTML(string=get_template(template_name).render(context)).write_pdf()

    return build


def excel_attachment(key, columns):
    def build(context):
        from openpyxl import Workbook

        book = Workbook()
        sheet = book.active
        sheet.append([title for title, _field in columns])

        for row in context[key]:
            sheet.append([row[field] for _title, field in columns])

        buffer = BytesIO()
        book.save(buffer)

        return buffer.getvalue()

    return build


ATTACHMENTS = {
    'po_vendor_pdf': ('P.O. Vendor PDF', 'PO_{po_number}.pdf', pdf_attachment('master/purchase_pdfs/vendor.html')),
    'po_vendor_costcard_pdf': ('P.O. Vendor Cost Card PDF', 'PO_{po_number}_CostCard.pdf', pdf_attachment('master/purchase_pdfs/vendor_costcard.html')),
    'po_self_pdf': ('P.O. Self PDF', 'PO_{po_number}_Self.pdf', pdf_attachment('master/purchase_pdfs/self.html')),
    'po_self_costcard_pdf': ('P.O. Self Cost Card PDF', 'PO_{po_number}_Self_CostCard.pdf', pdf_attachment('master/purchase_pdfs/self_costcard.html')),
    'stone_diamond_xlsx': (
        'Stone Requisition Details [Diamond] Excel',
        'Diamond_Requisition_{po_number}.xlsx',
        excel_attachment('diamonds', [('Shape', 'shape'), ('Size', 'size'), ('Color', 'color'), ('Clarity', 'clarity'), ('Pcs', 'pcs'), ('Weight', 'weight')]),
    ),
    'stone_color_xlsx': (
        'Stone Requisition Details [Color Stone] Excel',
        'ColorStone_Requisition_{po_number}.xlsx',
        excel_attachment('stones', [('Stone', 'name'), ('Shape', 'shape'), ('Size', 'size'), ('Colour', 'colour'), ('Quality', 'quality'), ('Pcs', 'pcs'), ('Weight', 'weight')]),
    ),
}


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


def label(value):
    if value is None or value == '':
        return ''

    return getattr(value, 'name', None) or str(value)


def dec(obj, name):
    return Decimal(getattr(obj, name, 0) or 0)


def money(value):
    amount = getattr(value, 'amount', value)

    if amount is None or amount == '':
        return ''

    return f'{Decimal(amount):,.2f}'


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
        qty = Decimal(line.qty or 0)
        weight = dec(card, 'net_weight')
        purity = getattr(card, 'metal_purity', None)
        description = card_description(card) or line.styleno

        if line.vstyleno and line.styleno:
            description = f'{description} (our style {line.styleno})'

        items.append({
            'code': line.vstyleno or line.styleno,
            'description': description,
            'metal': label(getattr(purity, 'metal_type', None)),
            'purity': getattr(card, 'karat', '') or label(purity),
            'size': size_text(line),
            'net_weight': f'{weight:.2f}' if weight else '',
            'weight_value': weight * qty,
            'quantity': f'{qty:g}',
            'amount': money(dec(card, 'fob') * qty),
            'amount_value': dec(card, 'fob') * qty,
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
        qty = Decimal(line.qty or 0)

        for stone_line in stone_lines(card):
            if getattr(stone_line, 'etype', '') != etype:
                continue

            key = tuple(label(getattr(stone_line, field, '')) for field in STONE_KEYS)
            row = grouped.setdefault(key, {'pcs': 0, 'cts': Decimal(0)})
            row['pcs'] += int(getattr(stone_line, 'pcs', 0) or 0) * int(qty)
            row['cts'] += dec(stone_line, 'cts') * qty

    return [
        {
            'stone': key[0],
            'shape': key[1],
            'size': key[2],
            'colour': key[3],
            'quality': key[4],
            'pcs': row['pcs'],
            'cts': row['cts'],
        }
        for key, row in sorted(grouped.items())
    ]


def cost_rows(pairs):
    rows = []

    for line, card in pairs:
        qty = Decimal(line.qty or 0)
        rows.append({
            'style': line.styleno,
            'quantity': qty,
            'metal': dec(card, 'metal_amount') * qty,
            'stones': dec(card, 'stone_amount') * qty,
            'labour': dec(card, 'labour_amount') * qty,
            'total': dec(card, 'final_amount') * qty,
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


def attachment_label(template):
    codes = split_emails(template.attachments) if template else []

    return ', '.join(ATTACHMENTS[code][0] for code in codes if code in ATTACHMENTS)


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
            'attachments': attachment_label(template),
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

    if vendor is not None:
        lines = [line for line in lines if line_vendor(order, line) == vendor]

    pairs = line_cards(order, lines)
    items = order_items(order, pairs)
    vendors = order_vendors(order, lines)
    supplier = vendor or (vendors[0] if vendors else None)
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
    total_qty = sum((Decimal(item['quantity']) for item in items), Decimal(0))

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
        'total_net_weight': f'{total_weight:.2f}',
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
                'weight': f"{row['cts']:.2f}",
            }
            for row in diamonds
        ],
        'total_diamond_pcs': sum(row['pcs'] for row in diamonds),
        'total_diamond_ct': f"{sum((row['cts'] for row in diamonds), Decimal(0)):.2f}",
        'stones': [
            {
                'name': row['stone'],
                'shape': row['shape'],
                'size': row['size'],
                'colour': row['colour'],
                'quality': row['quality'],
                'pcs': row['pcs'],
                'weight': f"{row['cts']:.2f}",
            }
            for row in colour_stones
        ],
        'total_color_pcs': sum(row['pcs'] for row in colour_stones),
        'total_color_ct': f"{sum((row['cts'] for row in colour_stones), Decimal(0)):.2f}",
        'ny_eta': ship_date,
        'ny_address': company_address_text,
        'costs': [
            {
                'style': row['style'],
                'quantity': f"{row['quantity']:g}",
                'metal': money(row['metal']),
                'stones': money(row['stones']),
                'labour': money(row['labour']),
                'total': money(row['total']),
            }
            for row in costs
        ],
        'total_qty': f'{total_qty:g}',
        'total_metal': money(sum((row['metal'] for row in costs), Decimal(0))),
        'total_stones': money(sum((row['stones'] for row in costs), Decimal(0))),
        'total_labour': money(sum((row['labour'] for row in costs), Decimal(0))),
        'ny_total': money(sum((row['total'] for row in costs), Decimal(0))),
        'company_name': company_name,
        'company_logo_url': COMPANY_PROFILE['logo_url'],
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

    if not code and template and template.template:
        with template.template.open('rb') as handle:
            code = handle.read().decode('utf-8')

    if code:
        return Template(code).render(Context(context))

    return get_template(DEFAULT_TEMPLATES[key]).render(context)


def render_subject(template, context):
    subject = (template.subject or '').strip() if template else ''

    if subject:
        return ' '.join(Template(subject).render(Context(context)).split())

    return f"Purchase {context['po_type']} {context['po_number']}"


def deliver(key, template, entered, context, subject_text):
    recipients = split_emails(entered)

    if not recipients:
        return False, {'key': key, 'email': entered, 'error': 'No recipient email.'}

    try:
        for recipient in recipients:
            validate_email(recipient)
    except ValidationError:
        return False, {'key': key, 'email': entered, 'error': 'Invalid email address.'}

    try:
        context = dict(context, attachment_names=attachment_label(template))
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

        for code in split_emails(template.attachments if template else ''):
            if code not in ATTACHMENTS:
                continue

            _label, filename, builder = ATTACHMENTS[code]
            name = filename.format(**context)
            message.attach(name, builder(context), mimetypes.guess_type(name)[0] or 'application/octet-stream')

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

        template = format_template(mail, field)

        if template is None:
            failed.append({'key': key, 'email': entered, 'error': 'No active template for this mail type.'})
            continue

        if key == 'vendor' and len(vendors) > 1:
            targets = [(company_email(item), item) for item in vendors]
        elif key == 'vendor' and vendors:
            targets = [(entered, vendors[0])]
        else:
            targets = [(entered, None)]

        for recipient, vendor in targets:
            context = dict(build_context(order, vendor), custom_message=selection.get('message') or '')
            ok, record = deliver(key, template, recipient, context, selection.get('subject'))
            (sent if ok else failed).append(record)

    return {'sent': sent, 'failed': failed}