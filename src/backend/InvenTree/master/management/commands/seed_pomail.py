from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.loader import get_template

from master.models import POMail, Templates

MAIL_NAME = 'Default P.O. Mail'
MAIL_ORDER = 1

FORMATS = [
    {
        'field': 'format1',
        'name': 'PO Vendor Mail',
        'subject': 'Purchase {{ po_type }} {{ po_number }} - {{ company_name }}',
        'attachments': 'po_vendor_pdf,po_vendor_costcard_pdf',
        'file': 'master/purchase_emails/vendor.html',
    },
    {
        'field': 'format2',
        'name': 'PO Diamond Office Mail',
        'subject': 'Diamond Requisition - PO {{ po_number }} ({{ supplier_name }})',
        'attachments': 'stone_diamond_xlsx',
        'file': 'master/purchase_emails/diamond_office.html',
    },
    {
        'field': 'format3',
        'name': 'PO Color Stone Office Mail',
        'subject': 'Color Stone Requisition - PO {{ po_number }} ({{ supplier_name }})',
        'attachments': 'stone_color_xlsx',
        'file': 'master/purchase_emails/color_stone_office.html',
    },
    {
        'field': 'format4',
        'name': 'PO New York Office Mail',
        'subject': 'Purchase {{ po_type }} {{ po_number }} - {{ customer_name }}',
        'attachments': 'po_self_pdf,po_self_costcard_pdf',
        'file': 'master/purchase_emails/new_york_office.html',
    },
]


def design_source(spec):
    try:
        source = get_template(spec['file']).template.source
    except Exception:
        return ''

    return source if source.strip() else ''


class Command(BaseCommand):
    help = 'Update the default P.O. Mail and its four templates in place.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        with transaction.atomic():
            mail = POMail.objects.filter(name=MAIL_NAME).first()

            if mail is None:
                mail = POMail.objects.create(name=MAIL_NAME, order=MAIL_ORDER, active=True)
                self.stdout.write(f'created P.O. Mail {mail.name}')

            for spec in FORMATS:
                template = getattr(mail, spec['field'])
                created = template is None

                if created:
                    template = Templates(name=spec['name'], recipients='')

                template.subject = template.subject or spec['subject']
                template.attachments = spec['attachments']
                template.code = design_source(spec) or template.code
                template.template = None
                template.active = True
                template.save()

                setattr(mail, spec['field'], template)

                self.stdout.write(
                    f"{'created' if created else 'updated'} {spec['field']} {template.name}: "
                    f"{template.attachments} | code {len(template.code or '')} chars"
                )

            mail.active = True
            mail.save()

            if options['dry_run']:
                transaction.set_rollback(True)
                self.stdout.write('dry run: all changes rolled back')


# python manage.py seed_pomail --dry-run
# python manage.py seed_pomail