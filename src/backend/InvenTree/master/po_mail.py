import re
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.db.models import Q
from django.template import Context, Template
from django.template.loader import get_template

from common.settings import get_global_setting
from order.models import PurchaseOrder

from .models import POMail, Terms

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


def get_order(po_number):
    value = str(po_number or '').strip()

    if not value:
        return None

    return PurchaseOrder.objects.select_related('supplier').filter(reference=value).first()


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


def company_email(company):
    if company is None:
        return ''

    return (getattr(company, 'email', '') or '').strip()


def vendor_email(order):
    contact = getattr(order, 'contact', None)
    return ((getattr(contact, 'email', '') or '').strip()) or company_email(order.supplier)


def customer_email(order):
    return company_email(getattr(order, 'customer', None))


def party(company, email):
    if company is None:
        return None

    return {'id': company.pk, 'name': company.name, 'email': email}


def subject_context(order):
    supplier = order.supplier

    return {
        'po_number': order.reference,
        'po_date': fmt_date(getattr(order, 'creation_date', None)),
        'supplier_name': supplier.name if supplier else '',
        'company_name': get_global_setting('INVENTREE_COMPANY_NAME') or COMPANY_PROFILE['name'],
    }


def mail_options(order, mail):
    vendor = vendor_email(order)
    customer = customer_email(order)
    context = subject_context(order)
    formats = []

    for key, field, label in FORMATS:
        template = format_template(mail, field)
        formats.append({
            'key': key,
            'label': label,
            'active': template is not None,
            'template': template.pk if template else None,
            'template_name': template.name if template else None,
            'subject': render_subject(template, context) if template else '',
            'email': vendor if key == 'vendor' else customer,
        })

    return {
        'order': order.pk,
        'po_number': order.reference,
        'mail': mail.pk if mail else None,
        'vendor': party(order.supplier, vendor),
        'customer': party(getattr(order, 'customer', None), customer),
        'vendor_email': vendor,
        'customer_email': customer,
        'formats': formats,
    }


def money(value):
    amount = getattr(value, 'amount', value)

    if amount is None or amount == '':
        return ''

    return f'{Decimal(amount):,.2f}'


def fmt_date(value):
    return value.strftime('%d %b %Y') if value else ''


def order_items(order):
    items = []

    for line in order.lines.select_related('part__part'):
        supplier_part = line.part
        part = getattr(supplier_part, 'part', None)
        price = line.purchase_price
        quantity = Decimal(line.quantity or 0)
        price_amount = Decimal(getattr(price, 'amount', 0) or 0) if price else Decimal(0)
        weight = getattr(part, 'weight', None)

        items.append({
            'code': getattr(supplier_part, 'SKU', '') or '',
            'description': getattr(part, 'name', '') or '',
            'metal': getattr(part, 'metal', '') or '',
            'purity': getattr(part, 'purity', '') or '',
            'size': getattr(part, 'size', '') or '',
            'net_weight': f'{Decimal(weight):.2f}' if weight else '',
            'weight_value': Decimal(weight) * quantity if weight else Decimal(0),
            'quantity': f'{quantity:g}',
            'amount': money(quantity * price_amount),
            'amount_value': quantity * price_amount,
        })

    return items


def build_context(order):
    supplier = order.supplier
    items = order_items(order)
    computed_total = sum((item['amount_value'] for item in items), Decimal(0))
    total = order.total_price if getattr(order, 'total_price', None) else computed_total
    total_weight = sum((item['weight_value'] for item in items), Decimal(0))

    terms = (
        Terms.objects.filter(active=True)
        .filter(Q(all_vendors=True) | Q(vendors=supplier))
        .distinct()
        .order_by('name')
        .first()
    )

    contact = getattr(order, 'contact', None)
    address = getattr(order, 'address', None)
    supplier_address = getattr(supplier, 'primary_address', None)
    creator = getattr(order, 'created_by', None)
    base_url = (get_global_setting('INVENTREE_BASE_URL') or '').rstrip('/')
    company_name = get_global_setting('INVENTREE_COMPANY_NAME') or COMPANY_PROFILE['name']
    po_date = fmt_date(getattr(order, 'creation_date', None))
    delivery_date = fmt_date(getattr(order, 'target_date', None))
    currency = getattr(order, 'currency', '') or ''
    grand_total = money(total)

    return {
        'po_number': order.reference,
        'po_date': po_date,
        'delivery_date': delivery_date,
        'confirm_by_date': delivery_date,
        'payment_terms': terms.name if terms else '',
        'currency': currency,
        'preheader': f'New purchase order {order.reference} from {company_name}.',
        'supplier_name': supplier.name if supplier else '',
        'supplier_contact': getattr(contact, 'name', '') or (supplier.name if supplier else ''),
        'supplier_address': str(supplier_address) if supplier_address else '',
        'supplier_gstin': '',
        'delivery_address': str(address) if address else '',
        'items': items,
        'total_net_weight': f'{total_weight:.2f}',
        'subtotal': grand_total,
        'gst_percent': '0',
        'gst_amount': '0.00',
        'grand_total': grand_total,
        'order_notes': getattr(order, 'description', '') or '',
        'weight_tolerance': '',
        'po_view_url': f'{base_url}/web/purchasing/purchase-order/{order.pk}' if base_url else '',
        'buyer_name': (creator.get_full_name() or creator.get_username()) if creator else '',
        'buyer_email': getattr(creator, 'email', '') if creator else '',
        'buyer_phone': '',
        'attachment_names': '',
        'stones_needed_by': delivery_date,
        'total_stone_ct': '',
        'total_stone_pcs': '',
        'diamonds': [],
        'stones': [],
        'ny_eta': delivery_date,
        'ny_address': str(address) if address else '',
        'costs': [],
        'total_qty': f"{sum((Decimal(item['quantity']) for item in items), Decimal(0)):g}",
        'total_metal': '',
        'total_stones': '',
        'total_labour': '',
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
    text = (template.template or '').strip() if template else ''

    if text and text.endswith('.html') and '<' not in text and '\n' not in text:
        return get_template(text).render(context)

    if text:
        return Template(text).render(Context(context))

    return get_template(DEFAULT_TEMPLATES[key]).render(context)


def render_subject(template, context):
    subject = (template.subject or '').strip() if template else ''

    if subject:
        return ' '.join(Template(subject).render(Context(context)).split())

    return f"Purchase Order {context['po_number']}"


def send_selected(order, mail, selections):
    base_context = build_context(order)
    defaults = {item['key']: item['email'] for item in mail_options(order, mail)['formats']}
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

        recipients = split_emails(entered)

        if not recipients:
            failed.append({'key': key, 'email': entered, 'error': 'No recipient email.'})
            continue

        try:
            for recipient in recipients:
                validate_email(recipient)
        except ValidationError:
            failed.append({'key': key, 'email': entered, 'error': 'Invalid email address.'})
            continue

        context = dict(base_context, custom_message=selection.get('message') or '')

        try:
            html = render_body(template, key, context)
            subject = ' '.join((selection.get('subject') or '').split()) or render_subject(template, context)
            message = EmailMultiAlternatives(
                subject,
                f"Purchase Order {context['po_number']} from {context['company_name']}. "
                'Please view this email in an HTML-capable client.',
                settings.DEFAULT_FROM_EMAIL,
                recipients,
            )
            message.attach_alternative(html, 'text/html')
            message.send()
            sent.append({'key': key, 'email': ', '.join(recipients), 'subject': subject})
        except Exception as exc:
            failed.append({'key': key, 'email': ', '.join(recipients), 'error': str(exc)})

    return {'sent': sent, 'failed': failed}