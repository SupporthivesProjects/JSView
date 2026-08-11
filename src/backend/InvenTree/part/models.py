from __future__ import annotations

import hashlib
import inspect
import math
import os
import re
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import TypedDict, cast

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import F, Q, QuerySet, Sum, UniqueConstraint
from django.db.models.functions import Coalesce
from django.db.models.signals import post_delete, post_save
from django.db.utils import IntegrityError
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import structlog
from django_cleanup import cleanup
from djmoney.contrib.exchange.exceptions import MissingRate
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money
from mptt.managers import TreeManager
from mptt.models import TreeForeignKey

import common.currency
import common.models
import InvenTree.conversion
import InvenTree.fields
import InvenTree.helpers
import InvenTree.models
import InvenTree.ready
import InvenTree.tasks
import part.helpers as part_helpers
import part.settings as part_settings
import report.mixins
import users.models
from build import models as BuildModels
from build.status_codes import BuildStatusGroups
from common.currency import currency_code_default
from common.icons import validate_icon
from common.settings import get_global_setting
from InvenTree import helpers, validators
from InvenTree.exceptions import log_error
from InvenTree.fields import InvenTreeURLField
from InvenTree.helpers import decimal2string, normalize
from order import models as OrderModels
from order.status_codes import (
    PurchaseOrderStatus,
    PurchaseOrderStatusGroups,
    SalesOrderStatusGroups,
    TransferOrderStatusGroups,
)
from stock import models as StockModels

logger = structlog.get_logger('inventree')

class PartCategory(
    InvenTree.models.PluginValidationMixin,
    InvenTree.models.InvenTreeParameterMixin,
    InvenTree.models.MetadataMixin,
    InvenTree.models.PathStringMixin,
    InvenTree.models.InvenTreeTree,
):

    ITEM_PARENT_KEY = 'category'
    EXTRA_PATH_FIELDS = ['icon']
    IMPORT_ID_FIELDS = ['pathstring', 'name']
    default_location = TreeForeignKey('stock.StockLocation', related_name='default_categories', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Default Location'), help_text=_('Default location for parts in this category'),)
    structural = models.BooleanField(default=False, verbose_name=_('Structural'), help_text=_('Parts may not be directly assigned to a structural category, ' 'but may be assigned to child categories.'),)
    default_keywords = models.CharField(null=True, blank=True, max_length=250, verbose_name=_('Default keywords'), help_text=_('Default keywords for parts in this category'),)
    _icon = models.CharField(blank=True, null=True, max_length=100, verbose_name=_('Icon'), help_text=_('Icon (optional)'), validators=[validate_icon], db_column='icon',)

    def delete(self, *args, **kwargs):
        super().delete(
            delete_children=kwargs.get('delete_child_categories', False),
            delete_items=kwargs.get('delete_parts', False),
        )

    @property
    def icon(self):
        if self._icon:
            return self._icon

        if default_icon := get_global_setting('PART_CATEGORY_DEFAULT_ICON', cache=True):
            return default_icon

        return ''

    @icon.setter
    def icon(self, value):
        default_icon = get_global_setting('PART_CATEGORY_DEFAULT_ICON', cache=True)

        if not self._icon and value == default_icon:
            return

        self._icon = value

    @staticmethod
    def get_api_url():
        return reverse('api-part-category-list')

    def get_absolute_url(self):
        return helpers.pui_url(f'/part/category/{self.id}')

    def clean(self):
        if self.pk and self.structural and self.partcount(False, False) > 0:
            raise ValidationError(
                _(
                    'You cannot make this part category structural because some parts '
                    'are already assigned to it!'
                )
            )
        super().clean()

    def get_parts(self, cascade=True) -> set[Part]:
        if cascade:
            queryset = Part.objects.filter(category__in=self.getUniqueChildren(include_self=True))
        else:
            queryset = Part.objects.filter(category=self.pk)

        return queryset

    @property
    def item_count(self):
        return self.partcount()

    def get_items(self, cascade=False):
        return self.get_parts(cascade=cascade)

    def partcount(self, cascade=True, active=False):
        query = self.get_parts(cascade=cascade)

        if active:
            query = query.filter(active=True)

        return query.count()

    def prefetch_parts_parameters(self, cascade=True):
        return (
            self
            .get_parts(cascade=cascade)
            .prefetch_related('parameters_list', 'parameters_list__template')
            .all()
        )

    def get_unique_parameters(self, cascade=True, prefetch=None):
        unique_parameters_names = []

        parts = prefetch or self.prefetch_parts_parameters(cascade=cascade)

        for part in parts:
            for parameter in part.parameters_list.all():
                parameter_name = parameter.template.name
                if parameter_name not in unique_parameters_names:
                    unique_parameters_names.append(parameter_name)

        return sorted(unique_parameters_names)

    def get_parts_parameters(self, cascade=True, prefetch=None):
        category_parameters = []

        parts = prefetch or self.prefetch_parts_parameters(cascade=cascade)

        for part in parts:
            part_parameters = {'pk': part.pk, 'name': part.name, 'description': part.description,}

            if part.IPN:
                part_parameters['IPN'] = part.IPN

            for parameter in part.parameters_list.all():
                parameter_name = parameter.template.name
                parameter_value = parameter.data
                part_parameters[parameter_name] = parameter_value

            category_parameters.append(part_parameters)

        return category_parameters

    @classmethod
    def get_parent_categories(cls):

        root_categories = cls.objects.filter(level=0)

        parent_categories = []
        for category in root_categories:
            parent_categories.append((category.id, category.name))

        return parent_categories

    def get_parameter_templates(self):
        prefetch = PartCategoryParameterTemplate.objects.prefetch_related('category', 'parameter')

        return prefetch.filter(category=self.id)

    def get_subscribers(self, include_parents: bool = True) -> list[User]:
        subscribers = set()

        if include_parents:
            cats = self.get_ancestors(include_self=True)
            queryset = PartCategoryStar.objects.filter(category__in=cats)
        else:
            queryset = PartCategoryStar.objects.filter(category=self)

        for result in queryset:
            subscribers.add(result.user)

        return list(subscribers)

    def is_starred_by(self, user, **kwargs):
        return user in self.get_subscribers(**kwargs)

    def set_starred(self, user, status: bool, **kwargs) -> None:
        if not user:
            return

        if self.is_starred_by(user, **kwargs) == status:
            return

        if status:
            PartCategoryStar.objects.create(category=self, user=user)
        else:

            PartCategoryStar.objects.filter(category=self, user=user).delete()

    class Meta:

        verbose_name = _('Part Category')
        verbose_name_plural = _('Part Categories')

def rename_part_image(instance, filename):
    base = part_helpers.PART_IMAGE_DIR
    fname = os.path.basename(filename)

    return os.path.join(base, fname)

class PartCategoryParameterTemplate(InvenTree.models.InvenTreeMetadataModel):

    category = models.ForeignKey(PartCategory, on_delete=models.CASCADE, related_name='parameter_templates', verbose_name=_('Category'), help_text=_('Part Category'),)
    template = models.ForeignKey(common.models.ParameterTemplate, on_delete=models.CASCADE, related_name='part_categories',)
    default_value = models.CharField(max_length=500, blank=True, verbose_name=_('Default Value'), help_text=_('Default Parameter Value'),)

    @staticmethod
    def get_api_url():
        return reverse('api-part-category-parameter-list')

    def __str__(self):
        if self.default_value:
            return f'{self.category.name} | {self.template.name} | {self.default_value}'
        return f'{self.category.name} | {self.template.name}'

    def clean(self):
        super().clean()

        self.default_value = ('' if self.default_value is None else str(self.default_value.strip()))

        if (
            self.default_value
            and get_global_setting(
                'PARAMETER_ENFORCE_UNITS', True, cache=False, create=False
            )
            and self.template.units
        ):
            try:
                InvenTree.conversion.convert_physical_value(
                    self.default_value, self.template.units
                )
            except ValidationError as e:
                raise ValidationError({'default_value': e.message})

    class Meta:

        verbose_name = _('Part Category Parameter Template')

        constraints = [UniqueConstraint(fields=['category', 'template'], name='unique_category_parameter_pair')]

class PartReportContext(report.mixins.BaseReportContext, TypedDict):

    bom_items: report.mixins.QuerySet[BomItem]
    category: PartCategory | None
    description: str
    IPN: str | None
    name: str
    parameters: dict[str, str]
    part: Part
    qr_data: str
    qr_url: str
    revision: str | None
    test_template_list: report.mixins.QuerySet[PartTestTemplate]
    test_templates: dict[str, PartTestTemplate]

@cleanup.ignore
class Part(
    InvenTree.models.PluginValidationMixin,
    InvenTree.models.InvenTreeParameterMixin,
    InvenTree.models.InvenTreeAttachmentMixin,
    InvenTree.models.InvenTreeBarcodeMixin,
    InvenTree.models.InvenTreeTagsMixin,
    InvenTree.models.InvenTreeNotesMixin,
    report.mixins.InvenTreeReportMixin,
    InvenTree.models.InvenTreeImageMixin,
    InvenTree.models.MetadataMixin,
    InvenTree.models.InvenTreeTree,
):

    NODE_PARENT_KEY = 'variant_of'
    IMAGE_RENAME = rename_part_image
    IMPORT_ID_FIELDS = ['IPN', 'name']
    objects = TreeManager()
    name = models.CharField(max_length=100, blank=False, help_text=_('Part name'), verbose_name=_('Name'))
    is_template = models.BooleanField(default=part_settings.part_template_default, verbose_name=_('Is Template'), help_text=_('Is this part a template part?'),)
    variant_of = models.ForeignKey('part.Part', related_name='variants', null=True, blank=True, limit_choices_to={'is_template': True}, on_delete=models.SET_NULL, help_text=_('Is this part a variant of another part?'), verbose_name=_('Variant Of'),)
    description = models.CharField(max_length=250, blank=True, verbose_name=_('Description'), help_text=_('Part description (optional)'),)
    keywords = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Keywords'), help_text=_('Part keywords to improve visibility in search results'),)
    category = TreeForeignKey(PartCategory, related_name='parts', null=True, blank=True, on_delete=models.DO_NOTHING, verbose_name=_('Category'), help_text=_('Part category'),)
    IPN = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('IPN'), help_text=_('Internal Part Number'),)
    revision = models.CharField(max_length=100, blank=True, null=True, help_text=_('Part revision or version number'), verbose_name=_('Revision'),)
    revision_of = models.ForeignKey('part.Part', related_name='revisions', null=True, blank=True, on_delete=models.SET_NULL, help_text=_('Is this part a revision of another part?'), verbose_name=_('Revision Of'),)
    link = InvenTreeURLField(blank=True, null=True, verbose_name=_('Link'), help_text=_('Link to external URL'), max_length=2000,)
    default_location = TreeForeignKey('stock.StockLocation', on_delete=models.SET_NULL, blank=True, null=True, help_text=_('Where is this item normally stored?'), related_name='default_parts', verbose_name=_('Default Location'),)
    default_expiry = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)], verbose_name=_('Default Expiry'), help_text=_('Expiry time (in days) for stock items of this part'),)
    minimum_stock = models.DecimalField(max_digits=19, decimal_places=6, default=0, validators=[MinValueValidator(0)], verbose_name=_('Minimum Stock'), help_text=_('Minimum allowed stock level'),)
    maximum_stock = models.DecimalField(max_digits=19, decimal_places=6, default=0, validators=[MinValueValidator(0)], verbose_name=_('Maximum Stock'), help_text=_('Maximum allowed stock level'),)
    units = models.CharField(max_length=20, default='', blank=True, null=True, verbose_name=_('Units'), help_text=_('Units of measure for this part'), validators=[validators.validate_physical_units],)
    assembly = models.BooleanField(default=part_settings.part_assembly_default, verbose_name=_('Assembly'), help_text=_('Can this part be built from other parts?'),)
    component = models.BooleanField(default=part_settings.part_component_default, verbose_name=_('Component'), help_text=_('Can this part be used to build other parts?'),)
    trackable = models.BooleanField(default=part_settings.part_trackable_default, verbose_name=_('Trackable'), help_text=_('Does this part have tracking for unique items?'),)
    testable = models.BooleanField(default=False, verbose_name=_('Testable'), help_text=_('Can this part have test results recorded against it?'),)
    purchaseable = models.BooleanField(default=part_settings.part_purchaseable_default, verbose_name=_('Purchaseable'), help_text=_('Can this part be purchased from external suppliers?'),)
    salable = models.BooleanField(default=part_settings.part_salable_default, verbose_name=_('Salable'), help_text=_('Can this part be sold to customers?'),)
    active = models.BooleanField(default=True, verbose_name=_('Active'), help_text=_('Is this part active?'))
    locked = models.BooleanField(default=False, verbose_name=_('Locked'), help_text=_('Locked parts cannot be edited'),)
    virtual = models.BooleanField(default=part_settings.part_virtual_default, verbose_name=_('Virtual'), help_text=_('Is this a virtual part, such as a software product or license?'),)
    consumable = models.BooleanField(default=False, verbose_name=_('Consumable'), help_text=_('Is this part consumable, such as glue or a fastener?'),)
    bom_validated = models.BooleanField(default=False, verbose_name=_('BOM Validated'), help_text=_('Is the BOM for this part valid?'),)
    bom_checksum = models.CharField(max_length=128, blank=True, verbose_name=_('BOM checksum'), help_text=_('Stored BOM checksum'),)
    bom_checked_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('BOM checked by'), related_name='boms_checked',)
    bom_checked_date = models.DateField(blank=True, null=True, verbose_name=_('BOM checked date'))
    creation_date = models.DateField(auto_now_add=True, editable=False, blank=True, null=True, verbose_name=_('Creation Date'),)
    creation_user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Creation User'), related_name='parts_created',)
    responsible_owner = models.ForeignKey(users.models.Owner, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Responsible'), help_text=_('Owner responsible for this part'), related_name='parts_responsible',)
    base_cost = models.DecimalField(max_digits=19, decimal_places=6, default=0, validators=[MinValueValidator(0)], verbose_name=_('base cost'), help_text=_('Minimum charge (e.g. stocking fee)'),)
    multiple = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name=_('multiple'), help_text=_('Sell multiple'),)
    get_price = common.currency.get_price

    @staticmethod
    def get_api_url():
        return reverse('api-part-list')

    def api_instance_filters(self):
        return {'variant_of': {'exclude_tree': self.pk}}

    @classmethod
    def barcode_model_type_code(cls):
        return 'PA'

    def report_context(self) -> PartReportContext:
        return {
            'bom_items': cast(report.mixins.QuerySet['BomItem'], self.get_bom_items()),
            'category': self.category,
            'description': self.description,
            'IPN': self.IPN,
            'name': self.name,
            'parameters': self.parameters_map(),
            'part': self,
            'qr_data': self.barcode,
            'qr_url': self.get_absolute_url(),
            'revision': self.revision,
            'test_template_list': self.getTestTemplates(),
            'test_templates': self.getTestTemplateMap(),
        }

    def check_parameter_delete(self, parameter):
        if self.locked and get_global_setting('PART_ENABLE_LOCKING'):
            raise ValidationError(_('Cannot delete parameters of a locked part'))

    def check_parameter_save(self, parameter):
        if self.locked and get_global_setting('PART_ENABLE_LOCKING'):
            raise ValidationError(_('Cannot modify parameters of a locked part'))

    def delete(self, **kwargs):
        if self.locked and get_global_setting('PART_ENABLE_LOCKING'):
            raise ValidationError(_('Cannot delete this part as it is locked'))

        if self.active:
            raise ValidationError(_('Cannot delete this part as it is still active'))

        if not get_global_setting('PART_ALLOW_DELETE_FROM_ASSEMBLY', cache=False):
            if BomItem.objects.filter(sub_part=self).exists():
                raise ValidationError(
                    _('Cannot delete this part as it is used in an assembly')
                )

        super().delete()

    def save(self, *args, **kwargs):
        _new = False
        if self.pk:
            try:
                previous = Part.objects.get(pk=self.pk)

                if previous.image is not None and self.image != previous.image:

                    n_refs = (Part.objects .filter(image=previous.image) .exclude(pk=self.pk) .count())

                    if n_refs == 0:
                        logger.info("Deleting unused image file '%s'", previous.image)
                        previous.image.delete(save=False)
            except Part.DoesNotExist:
                pass
        else:
            _new = True

        self.full_clean()

        super().save(*args, **kwargs)

        if _new:

            self.ensure_trackable()

    def __str__(self):
        return f'{self.full_name} - {self.description}'

    def get_parts_in_bom(self, **kwargs):
        parts = set()

        for bom_item in self.get_bom_items(**kwargs):
            for part in bom_item.get_valid_parts_for_allocation():
                parts.add(part)

        return parts

    def check_if_part_in_bom(self, other_part, **kwargs):
        return other_part in self.get_parts_in_bom(**kwargs)

    def check_add_to_bom(self, parent, raise_error=False, recursive=True):
        result = True

        try:
            if self.pk == parent.pk:
                raise ValidationError({
                    'sub_part': _(
                        f"Part '{self}' cannot be used in BOM for '{parent}' (recursive)"
                    )
                })

            if self.tree_id == parent.tree_id:
                raise ValidationError({
                    'sub_part': _(
                        f"Part '{self}' cannot be used in BOM for '{parent}' (recursive)"
                    )
                })

            bom_items = self.get_bom_items()

            for item in bom_items.all():

                if item.sub_part == parent:
                    raise ValidationError({
                        'sub_part': _(
                            f"Part '{parent}' is  used in BOM for '{self}' (recursive)"
                        )
                    })

                if recursive:
                    result = result and item.sub_part.check_add_to_bom(parent, recursive=True, raise_error=raise_error)

        except ValidationError as e:
            if raise_error:
                raise e
            else:
                return False

        return result

    def validate_name(self, raise_error=True):
        from plugin import PluginMixinEnum, registry

        if not InvenTree.ready.isReadOnlyCommand():
            for plugin in registry.with_mixin(PluginMixinEnum.VALIDATION):

                try:
                    result = plugin.validate_part_name(self.name, self)
                    if result:
                        return
                except ValidationError as exc:
                    if raise_error:
                        raise ValidationError({'name': exc.message})
                except Exception:
                    log_error('validate_part_name', plugin=plugin.slug)

    def validate_ipn(self, raise_error=True):
        from plugin import PluginMixinEnum, registry

        if not InvenTree.ready.isReadOnlyCommand():
            for plugin in registry.with_mixin(PluginMixinEnum.VALIDATION):
                try:
                    result = plugin.validate_part_ipn(self.IPN, self)

                    if result:

                        break
                except ValidationError as exc:
                    if raise_error:
                        raise ValidationError({'IPN': exc.message})
                except Exception:
                    log_error('validate_part_ipn', plugin=plugin.slug)

        pattern = get_global_setting('PART_IPN_REGEX', '', create=False).strip()

        if pattern:
            match = re.search(pattern, self.IPN)

            if match is None:
                raise ValidationError(_(f'IPN must match regex pattern {pattern}'))

    def validate_revision(self):

        if self.revision_of:
            if self.revision_of == self:
                raise ValidationError({
                    'revision_of': _('Part cannot be a revision of itself')
                })

            if not self.revision:
                raise ValidationError({
                    'revision': _(
                        'Revision code must be specified for a part marked as a revision'
                    )
                })

            if get_global_setting('PART_REVISION_ASSEMBLY_ONLY'):
                if not self.assembly or not self.revision_of.assembly:
                    raise ValidationError({
                        'revision_of': _(
                            'Revisions are only allowed for assembly parts'
                        )
                    })

            if self.revision_of.is_template:
                raise ValidationError({
                    'revision_of': _('Cannot make a revision of a template part')
                })

            if self.variant_of != self.revision_of.variant_of:
                raise ValidationError({
                    'revision_of': _('Parent part must point to the same template')
                })

    def validate_serial_number(
        self,
        serial: str,
        stock_item=None,
        check_duplicates=True,
        raise_error=False,
        **kwargs,
    ):
        from plugin import PluginMixinEnum, registry

        serial = str(serial).strip()

        if not InvenTree.ready.isReadOnlyCommand():

            for plugin in registry.with_mixin(PluginMixinEnum.VALIDATION):

                try:
                    result = False

                    if hasattr(plugin, 'validate_serial_number'):
                        signature = inspect.signature(plugin.validate_serial_number)

                        if 'stock_item' in signature.parameters:

                            result = plugin.validate_serial_number(serial, self, stock_item=stock_item)
                        else:

                            result = plugin.validate_serial_number(serial, self)

                    if result is True:
                        return True
                except ValidationError as exc:
                    if raise_error:

                        raise exc
                    else:
                        return False
                except Exception:
                    log_error('validate_serial_number', plugin=plugin.slug)

        if not check_duplicates:
            return

        from stock.models import StockItem

        if get_global_setting('SERIAL_NUMBER_GLOBALLY_UNIQUE', False):

            parts = Part.objects.all()
        else:

            parts = Part.objects.filter(tree_id=self.tree_id)

        stock = StockItem.objects.filter(part__in=parts, serial=serial)

        if stock_item:

            stock = stock.exclude(pk=stock_item.pk)

        if stock.exists():
            if raise_error:
                raise ValidationError(
                    _('Stock item with this serial number already exists')
                    + ': '
                    + serial
                )
            else:
                return False
        else:

            return True

    def find_conflicting_serial_numbers(self, serials: list) -> list:

        from stock.models import StockItem

        conflicts = []

        if get_global_setting('SERIAL_NUMBER_GLOBALLY_UNIQUE', False):

            parts = Part.objects.all()
        else:

            parts = Part.objects.filter(tree_id=self.tree_id)

        items = StockItem.objects.filter(part__in=parts, serial__in=serials)
        items = items.order_by('serial_int', 'serial')

        for item in items:
            conflicts.append(item.serial)

        for serial in serials:
            if serial in conflicts:

                continue

            try:
                self.validate_serial_number(
                    serial, raise_error=True, check_duplicates=False
                )
            except ValidationError:

                conflicts.append(serial)

        return conflicts

    def get_latest_serial_number(self, allow_plugins=True):
        from plugin import PluginMixinEnum, registry

        if allow_plugins and not InvenTree.ready.isReadOnlyCommand():

            for plugin in registry.with_mixin(PluginMixinEnum.VALIDATION):
                try:
                    result = plugin.get_latest_serial_number(self)
                    if result is not None:
                        return str(result)
                except Exception:
                    log_error('get_latest_serial_number', plugin=plugin.slug)

        stock = (StockModels.StockItem.objects.all().exclude(serial=None).exclude(serial=''))

        if not get_global_setting('SERIAL_NUMBER_GLOBALLY_UNIQUE', False):

            stock = stock.filter(part__tree_id=self.tree_id)

        if not stock.exists():
            return None

        stock = stock.order_by('-serial_int', '-serial', '-pk')

        return stock[0].serial

    def get_next_serial_number(self):
        sn = self.get_latest_serial_number()

        return InvenTree.helpers.increment_serial_number(sn, self)

    @property
    def full_name(self) -> str:
        return part_helpers.render_part_full_name(self)

    def get_absolute_url(self):
        return helpers.pui_url(f'/part/{self.id}')

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        allow_duplicate_ipn = get_global_setting('PART_ALLOW_DUPLICATE_IPN')

        if self.IPN and not allow_duplicate_ipn:
            parts = Part.objects.filter(IPN__iexact=self.IPN)
            parts = parts.exclude(pk=self.pk)

            if parts.exists():
                raise ValidationError({
                    'IPN': _('Duplicate IPN not allowed in part settings')
                })

        if (
            self.revision_of
            and self.revision
            and (
                Part.objects
                .exclude(pk=self.pk)
                .filter(revision_of=self.revision_of, revision=self.revision)
                .exists()
            )
        ):
            raise ValidationError(_('Duplicate part revision already exists.'))

        if (self.revision or self.IPN) and (
            Part.objects
            .exclude(pk=self.pk)
            .filter(name=self.name, revision=self.revision, IPN=self.IPN)
            .exists()
        ):
            raise ValidationError(
                _('Part with this Name, IPN and Revision already exists.')
            )

    def clean(self):
        if self.category is not None and self.category.structural:
            raise ValidationError({
                'category': _('Parts cannot be assigned to structural part categories!')
            })

        self.validate_revision()

        super().clean()

        if type(self.IPN) is str:
            self.IPN = self.IPN.strip()

        self.validate_ipn()

        self.validate_name()

        if self.pk:

            self.ensure_trackable()

    def ensure_trackable(self):
        if self.trackable:
            for part in self.get_used_in():
                if not part.trackable:
                    part.trackable = True
                    part.clean()
                    part.save()

    def get_default_location(self):
        if self.default_location:
            return self.default_location
        elif self.category:

            cats = self.category.get_ancestors(ascending=True, include_self=True)

            for cat in cats:
                if cat.default_location:
                    return cat.default_location

        return None

    @property
    def default_supplier(self):
        return self.supplier_parts.filter(primary=True).first()

    @property
    def category_path(self):
        if self.category:
            return self.category.pathstring
        return ''

    @property
    def available_stock(self):
        total = self.total_stock
        total -= self.allocation_count()

        return max(total, 0)

    def requiring_build_orders(self, include_variants: bool = True):

        if include_variants:

            parts = list(self.get_descendants(include_self=True))
        else:
            parts = [self]

        used_in_parts = set()

        for part in parts:

            used_in_parts.update(part.get_used_in())

        builds = BuildModels.Build.objects.filter(part__in=list(used_in_parts), status__in=BuildStatusGroups.ACTIVE_CODES)

        return builds

    def required_build_order_quantity(self, include_variants: bool = True):

        builds = self.requiring_build_orders(include_variants=include_variants)

        quantity = 0

        if include_variants:
            matching_parts = list(self.get_descendants(include_self=True))
        else:
            matching_parts = [self]

        cached_bom_items: dict = {}

        for build in builds:
            if build.part.pk not in cached_bom_items:

                bom_items = build.part.get_bom_items().filter(sub_part__in=matching_parts)
                cached_bom_items[build.part.pk] = bom_items
            else:
                bom_items = cached_bom_items[build.part.pk]

            for bom_item in bom_items:
                build_line = build.build_lines.filter(bom_item=bom_item).first()

                if not build_line:
                    continue

                line_quantity = max(0, build_line.quantity - build_line.consumed)
                quantity += line_quantity

        return quantity

    def requiring_sales_orders(self, include_variants: bool = True):
        orders = set()

        if include_variants:
            parts = list(self.get_descendants(include_self=True))
        else:
            parts = [self]

        open_lines = OrderModels.SalesOrderLineItem.objects.filter(order__status__in=SalesOrderStatusGroups.OPEN, part__in=parts)

        for line in open_lines:
            orders.add(line.order)

        return orders

    def required_sales_order_quantity(self, include_variants: bool = True):
        if include_variants:
            parts = list(self.get_descendants(include_self=True))
        else:
            parts = [self]

        open_lines = OrderModels.SalesOrderLineItem.objects.filter(order__status__in=SalesOrderStatusGroups.OPEN, part__in=parts)

        quantity = 0

        for line in open_lines:

            if not line:
                continue

            remaining = max(line.quantity - line.shipped, 0)
            quantity += remaining

        return quantity

    def required_order_quantity(self, include_variants: bool = True):
        return self.required_build_order_quantity(
            include_variants=include_variants
        ) + self.required_sales_order_quantity(include_variants=include_variants)

    @property
    def quantity_to_order(self):

        required = self.required_order_quantity()

        required -= max(self.total_stock, self.minimum_stock)

        required -= self.on_order

        required -= self.quantity_being_built

        return max(required, 0)

    @property
    def net_stock(self):
        return self.total_stock - self.allocation_count() + self.on_order

    def get_subscribers(
        self, include_variants: bool = True, include_categories: bool = True
    ) -> list[User]:
        subscribers = set()

        queryset = PartStar.objects.all()

        if include_variants:
            queryset = queryset.filter(part__in=self.get_ancestors(include_self=True))
        else:
            queryset = queryset.filter(part=self)

        for star in queryset:
            subscribers.add(star.user)

        if include_categories and self.category:
            for sub in self.category.get_subscribers():
                subscribers.add(sub)

        return list(subscribers)

    def is_starred_by(self, user, **kwargs):
        return user in self.get_subscribers(**kwargs)

    def set_starred(self, user, status, **kwargs):
        if not user:
            return

        if self.is_starred_by(user, **kwargs) == status:
            return

        if status:
            PartStar.objects.create(part=self, user=user)
        else:

            PartStar.objects.filter(part=self, user=user).delete()

    @property
    def can_build(self):
        import part.filters

        if not self.has_bom:
            return 0

        queryset = self.get_bom_items(include_virtual=False)

        queryset = queryset.filter(BomItem.consumable_filter(consumable=False))

        queryset = part.filters.annotate_bom_item_can_build(queryset)

        can_build_quantity = None

        for value in queryset.values_list('can_build', flat=True):
            if can_build_quantity is None:
                can_build_quantity = value
            else:
                can_build_quantity = min(can_build_quantity, value)

        if can_build_quantity is None:

            return 0

        return int(max(can_build_quantity, 0))

    @property
    def active_builds(self):
        return self.builds.filter(status__in=BuildStatusGroups.ACTIVE_CODES)

    @property
    def quantity_being_built(self, include_variants: bool = True):
        builds = BuildModels.Build.objects.filter(status__in=BuildStatusGroups.ACTIVE_CODES)

        if include_variants:

            builds = builds.filter(part__in=self.get_descendants(include_self=True))
        else:

            builds = builds.filter(part=self)

        quantity = 0

        for build in builds:

            quantity += build.remaining

        return quantity

    @property
    def quantity_in_production(self, include_variants: bool = True):
        quantity = 0

        items = StockModels.StockItem.objects.filter(is_building=True, build__status__in=BuildStatusGroups.ACTIVE_CODES)

        if include_variants:

            items = items.filter(part__in=self.get_descendants(include_self=True))
        else:

            items = items.filter(part=self)

        for item in items:

            quantity += item.quantity

        return quantity

    def build_order_allocations(self, **kwargs):
        include_variants = kwargs.get('include_variants', True)

        queryset = BuildModels.BuildItem.objects.all()

        if include_variants:
            variants = self.get_descendants(include_self=True)
            queryset = queryset.filter(stock_item__part__in=variants)
        else:
            queryset = queryset.filter(stock_item__part=self)

        return queryset

    def build_order_allocation_count(self, **kwargs):
        query = self.build_order_allocations(**kwargs).aggregate(total=Coalesce(Sum('quantity', output_field=models.DecimalField()), 0, output_field=models.DecimalField(),))

        return query['total']

    def sales_order_allocations(self, **kwargs):
        include_variants = kwargs.get('include_variants', True)

        queryset = OrderModels.SalesOrderAllocation.objects.all()

        if include_variants:

            variants = self.get_descendants(include_self=True)
            queryset = queryset.filter(item__part__in=variants)
        else:

            queryset = queryset.filter(item__part=self)

        pending = kwargs.get('pending', True)

        if pending is True:

            queryset = queryset.filter(line__order__status__in=SalesOrderStatusGroups.OPEN, shipment__shipment_date=None,)
        elif pending is False:

            queryset = queryset.exclude(line__order__status__in=SalesOrderStatusGroups.OPEN, shipment__shipment_date=None,)

        return queryset

    def sales_order_allocation_count(self, **kwargs):
        query = self.sales_order_allocations(**kwargs).aggregate(total=Coalesce(Sum('quantity', output_field=models.DecimalField()), 0, output_field=models.DecimalField(),))

        return query['total']

    def transfer_order_allocations(self, **kwargs):
        include_variants = kwargs.get('include_variants', True)

        queryset = OrderModels.TransferOrderAllocation.objects.all()

        if include_variants:

            variants = self.get_descendants(include_self=True)
            queryset = queryset.filter(item__part__in=variants)
        else:

            queryset = queryset.filter(item__part=self)

        pending = kwargs.get('pending', True)

        if pending is True:

            queryset = queryset.filter(line__order__status__in=TransferOrderStatusGroups.OPEN)
        elif pending is False:

            queryset = queryset.exclude(line__order__status__in=TransferOrderStatusGroups.OPEN)

        return queryset

    def transfer_order_allocation_count(self, **kwargs):
        query = self.transfer_order_allocations(**kwargs).aggregate(total=Coalesce(Sum('quantity', output_field=models.DecimalField()), 0, output_field=models.DecimalField(),))

        return query['total']

    def allocation_count(self, **kwargs):
        if self.id is None:

            return 0

        return sum([
            self.build_order_allocation_count(**kwargs),
            self.sales_order_allocation_count(**kwargs),

        ])

    def stock_entries(
        self, include_variants=True, include_external=True, in_stock=None, location=None
    ):
        if include_variants:
            query = StockModels.StockItem.objects.filter(part__in=self.get_descendants(include_self=True))
        else:
            query = self.stock_items

        if in_stock is True:
            query = query.filter(StockModels.StockItem.IN_STOCK_FILTER)
        elif in_stock is False:
            query = query.exclude(StockModels.StockItem.IN_STOCK_FILTER)

        if include_external is False:

            query = query.filter(location__external=False)

        if location:
            locations = location.get_descendants(include_self=True)
            query = query.filter(location__in=locations)

        return query

    def get_stock_count(self, include_variants=True):
        entries = self.stock_entries(in_stock=True, include_variants=include_variants)

        query = entries.aggregate(t=Coalesce(Sum('quantity'), Decimal(0)))

        return query['t']

    @property
    def total_stock(self):
        return self.get_stock_count(include_variants=True)

    def get_bom_item_filter(
        self, include_inherited: bool = True, include_virtual: bool = True
    ):
        bom_filter = Q(part=self)

        if include_inherited:

            parents = self.get_ancestors(include_self=False)

            if parents.exists():
                parent_filter = Q(part__in=parents, inherited=True)

                bom_filter |= parent_filter

        if not include_virtual:
            bom_filter &= Q(sub_part__virtual=False)

        return bom_filter

    def get_bom_items(
        self, include_inherited: bool = True, include_virtual: bool = True
    ) -> QuerySet[BomItem]:
        queryset = BomItem.objects.filter(self.get_bom_item_filter(include_inherited=include_inherited, include_virtual=include_virtual))

        return queryset.prefetch_related('part', 'sub_part')

    def get_installed_part_options(
        self, include_inherited: bool = True, include_variants: bool = True
    ):
        parts = set()

        for bom_item in self.get_bom_items(include_inherited=include_inherited):
            if include_variants and bom_item.allow_variants:
                for part in bom_item.sub_part.get_descendants(include_self=True):
                    parts.add(part)
            else:
                parts.add(bom_item.sub_part)

        return parts

    def get_used_in_bom_item_filter(
        self, include_variants=True, include_substitutes=True
    ):

        try:
            parents = self.get_ancestors(include_self=False)
        except ValueError:

            parents = []

        query = Q(sub_part=self)

        if include_variants:

            query |= Q(allow_variants=True, sub_part__in=parents)

        if include_substitutes:

            substitutes = self.substitute_items.all()

            query |= Q(pk__in=[substitute.bom_item.pk for substitute in substitutes])

        return query

    def get_used_in(self, include_inherited=True, include_substitutes=True):

        bom_items = BomItem.objects.filter(self.get_used_in_bom_item_filter(include_substitutes=include_substitutes))

        parts = set()

        for bom_item in bom_items:
            if bom_item.part in parts:
                continue

            parts.add(bom_item.part)

            if include_inherited and bom_item.inherited:
                try:
                    descendants = bom_item.part.get_descendants(include_self=False)
                except ValueError:

                    descendants = []

                for variant in descendants:
                    parts.add(variant)

        return list(parts)

    @property
    def has_bom(self):
        return self.get_bom_items().exists()

    def get_trackable_parts(self):
        queryset = self.get_bom_items()
        queryset = queryset.filter(sub_part__trackable=True)

        return queryset

    @property
    def has_trackable_parts(self):
        return self.get_trackable_parts().exists()

    @property
    def bom_count(self):
        return self.get_bom_items().count()

    @property
    def used_in_count(self):
        return len(self.get_used_in())

    def get_bom_hash(self):
        result_hash = hashlib.md5(str(self.id).encode())

        bom_items = self.get_bom_items().all().prefetch_related('part', 'sub_part')

        for item in bom_items:
            result_hash.update(str(item.get_item_hash()).encode())

        return str(result_hash.digest())

    def is_bom_valid(self) -> bool:
        if not self.bom_checksum or not self.bom_checked_date:

            return False

        return self.get_bom_hash() == self.bom_checksum

    @transaction.atomic
    def validate_bom(self, user, valid: bool = True):

        bom_items = self.get_bom_items(include_inherited=False).prefetch_related('part', 'sub_part')

        if valid:
            for item in bom_items:
                item.validate_hash(valid=True)

        self.bom_validated = valid
        self.bom_checksum = self.get_bom_hash() if valid else ''
        self.bom_checked_by = user
        self.bom_checked_date = InvenTree.helpers.current_date()

        self.save()

    @transaction.atomic
    def clear_bom(self):
        import part.tasks as part_tasks

        self.bom_items.all().delete()

        InvenTree.tasks.offload_task(part_tasks.check_bom_valid, self.pk, group='part')

    def getRequiredParts(self, recursive=False, parts=None):
        if parts is None:
            parts = set()

        bom_items = self.get_bom_items()

        for bom_item in bom_items:
            sub_part = bom_item.sub_part

            if sub_part not in parts:
                parts.add(sub_part)

                if recursive:
                    sub_part.getRequiredParts(recursive=True, parts=parts)

        return parts

    @property
    def supplier_count(self):
        return self.supplier_parts.count()

    def update_pricing(self):
        self.pricing.update_pricing()

    @property
    def pricing(self):
        try:
            pricing = PartPricing.objects.get(part=self)
        except PartPricing.DoesNotExist:
            pricing = PartPricing(part=self)

        return pricing

    def schedule_pricing_update(
        self, create: bool = False, force: bool = False, refresh: bool = True
    ):
        if not force and not get_global_setting(
            'PRICING_AUTO_UPDATE', backup_value=True
        ):
            return

        if refresh:
            try:
                self.refresh_from_db()
            except Part.DoesNotExist:
                return

        try:
            pricing = self.pricing

            if create or pricing.pk:
                pricing.schedule_for_update(refresh=refresh)
        except IntegrityError:

            pass

    def get_price_info(self, quantity=1, buy=True, bom=True, internal=False):
        price_range = self.get_price_range(quantity, buy, bom, internal)

        if price_range is None:
            return None

        min_price, max_price = price_range

        if min_price == max_price:
            return min_price

        min_price = normalize(min_price)
        max_price = normalize(max_price)

        return f'{min_price} - {max_price}'

    def get_supplier_price_range(self, quantity=1):
        min_price = None
        max_price = None

        for supplier in self.supplier_parts.all():
            price = supplier.get_price(quantity)

            if price is None:
                continue

            if min_price is None or price < min_price:
                min_price = price

            if max_price is None or price > max_price:
                max_price = price

        if min_price is None or max_price is None:
            return None

        min_price = normalize(min_price)
        max_price = normalize(max_price)

        return (min_price, max_price)

    def get_bom_price_range(self, quantity=1, internal=False, purchase=False):
        min_price = None
        max_price = None

        for item in self.get_bom_items().select_related('sub_part'):
            if item.sub_part.pk == self.pk:
                logger.warning('WARNING: BomItem ID %s contains itself in BOM', item.pk)
                continue

            q = Decimal(quantity)
            i = Decimal(item.quantity)

            prices = item.sub_part.get_price_range(q * i, internal=internal, purchase=purchase)

            if prices is None:
                continue

            low, high = prices

            if min_price is None:
                min_price = 0

            if max_price is None:
                max_price = 0

            min_price += low
            max_price += high

        if min_price is None or max_price is None:
            return None

        min_price = normalize(min_price)
        max_price = normalize(max_price)

        return (min_price, max_price)

    def get_price_range(
        self, quantity=1, buy=True, bom=True, internal=False, purchase=False
    ):

        if internal and self.has_internal_price_breaks:
            internal_price = self.get_internal_price(quantity)
            return internal_price, internal_price

        if purchase:
            purchase_price = self.get_purchase_price(quantity)
            if purchase_price:
                return purchase_price

        buy_price_range = self.get_supplier_price_range(quantity) if buy else None
        bom_price_range = (self.get_bom_price_range(quantity, internal=internal) if bom else None)

        if buy_price_range is None:
            return bom_price_range

        elif bom_price_range is None:
            return buy_price_range
        return (
            min(buy_price_range[0], bom_price_range[0]),
            max(buy_price_range[1], bom_price_range[1]),
        )

    @property
    def has_price_breaks(self):
        return self.price_breaks.exists()

    @property
    def price_breaks(self):
        return self.salepricebreaks.order_by('quantity').all()

    @property
    def unit_pricing(self):
        return self.get_price(1)

    def add_price_break(self, quantity, price):

        if self.price_breaks.filter(quantity=quantity, part=self.pk).exists():
            return

        PartSellPriceBreak.objects.create(part=self, quantity=quantity, price=price)

    def get_internal_price(self, quantity, moq=True, multiples=True, currency=None):
        return common.currency.get_price(
            self, quantity, moq, multiples, currency, break_name='internal_price_breaks'
        )

    @property
    def has_internal_price_breaks(self):
        return self.internal_price_breaks.exists()

    @property
    def internal_price_breaks(self):
        return self.internalpricebreaks.order_by('quantity').all()

    def get_purchase_price(self, quantity):
        currency = currency_code_default()
        try:
            prices = [convert_money(item.purchase_price, currency).amount for item in self.stock_items.all() if item.purchase_price]
        except MissingRate:
            prices = None

        if prices:
            return min(prices) * quantity, max(prices) * quantity

        return None

    @transaction.atomic
    def copy_bom_from(self, other, clear: bool = True, **kwargs):

        if other == self:
            return

        if clear:

            self.bom_items.all().delete()

        my_ancestors = self.get_ancestors(include_self=False)

        raise_error = not kwargs.get('skip_invalid', True)

        include_inherited = kwargs.get('include_inherited', False)

        copy_substitutes = kwargs.get('copy_substitutes', True)

        for bom_item in other.get_bom_items(include_inherited=include_inherited).all():

            if not bom_item.part or not bom_item.sub_part:
                continue

            if bom_item.part in my_ancestors and bom_item.inherited:
                continue

            if not bom_item.sub_part.check_add_to_bom(self, raise_error=raise_error):
                continue

            substitutes = BomItemSubstitute.objects.filter(bom_item=bom_item)

            bom_item.part = self
            bom_item.pk = None

            bom_item.save()
            bom_item.refresh_from_db()

            if copy_substitutes:
                for sub in substitutes:

                    sub.pk = None
                    sub.bom_item = bom_item
                    sub.save()

    @transaction.atomic
    def copy_tests_from(self, other: Part, **kwargs) -> None:
        templates = []
        parts = self.get_ancestors(include_self=True)

        if not self.testable:
            return

        for template in other.test_templates.all():

            if PartTestTemplate.objects.filter(
                key=template.key, part__in=parts
            ).exists():
                continue

            template.pk = None
            template.part = self
            templates.append(template)

        if len(templates) > 0:
            PartTestTemplate.objects.bulk_create(templates, batch_size=250)

    @transaction.atomic
    def copy_category_parameters(self, category: PartCategory):
        from common.models import Parameter

        categories = category.get_ancestors(include_self=True)

        category_templates = PartCategoryParameterTemplate.objects.filter(category__in=categories).order_by('-category__level')

        template_ids = set()
        parameters = []
        content_type = ContentType.objects.get_for_model(Part)

        for category_template in category_templates:

            if self.parameters_list.filter(
                template=category_template.template
            ).exists():
                continue

            if category_template.template.pk in template_ids:
                continue

            template_ids.add(category_template.template.pk)

            parameters.append(
                Parameter(
                    template=category_template.template,
                    model_type=content_type,
                    model_id=self.pk,
                    data=category_template.default_value,
                )
            )

        Parameter.objects.bulk_create(parameters, batch_size=250)

    def getTestTemplates(
        self, required=None, include_parent: bool = True, enabled=None
    ) -> QuerySet[PartTestTemplate]:
        if include_parent:
            tests = PartTestTemplate.objects.filter(part__in=self.get_ancestors(include_self=True))
        else:
            tests = self.test_templates

        if required is not None:
            tests = tests.filter(required=required)

        if enabled is not None:
            tests = tests.filter(enabled=enabled)

        return tests

    def getTestTemplateMap(self, **kwargs):
        templates = {}

        for template in self.getTestTemplates(**kwargs):
            templates[template.key] = template

        return templates

    def getRequiredTests(self, include_parent=True, enabled=True):
        return self.getTestTemplates(
            required=True, enabled=enabled, include_parent=include_parent
        )

    def sales_orders(self):
        orders = []

        for line in self.sales_order_line_items.all().prefetch_related('order'):
            if line.order not in orders:
                orders.append(line.order)

        return orders

    def purchase_orders(self):
        orders = []

        for part in self.supplier_parts.all().prefetch_related(
            'purchase_order_line_items'
        ):
            for order in part.purchase_orders():
                if order not in orders:
                    orders.append(order)

        return orders

    @property
    def on_order(self):
        from order.models import PurchaseOrderLineItem

        quantity = 0

        lines = PurchaseOrderLineItem.objects.filter(order__status__in=PurchaseOrderStatusGroups.OPEN, part__part_id=self.pk, quantity__gt=F('received'),).prefetch_related('part')

        for line in lines:
            remaining = line.quantity - line.received

            if remaining > 0:
                quantity += line.part.base_quantity(remaining)

        return quantity

    @property
    def has_variants(self):
        return self.get_all_variants().exists()

    def get_all_variants(self):
        return self.get_descendants(include_self=False)

    @property
    def can_convert(self):
        return self.get_conversion_options().exists()

    def get_conversion_options(self):
        parts = []

        for child in self.get_descendants(include_self=False):
            parts.append(child)

        if self.variant_of:
            parts.append(self.variant_of)

            siblings = self.get_siblings(include_self=False)

            for sib in siblings:
                parts.append(sib)

        filtered_parts = Part.objects.filter(pk__in=[part.pk for part in parts])

        filtered_parts = filtered_parts.exclude(pk=self.pk)

        filtered_parts = filtered_parts.filter(active=True, virtual=False)

        return filtered_parts

    def get_related_parts(self):
        related_parts = set()

        related_parts_1 = self.related_parts_1.filter(part_1__id=self.pk)

        related_parts_2 = self.related_parts_2.filter(part_2__id=self.pk)

        for related_part in related_parts_1:

            related_parts.add(related_part.part_2)

        for related_part in related_parts_2:

            related_parts.add(related_part.part_1)

        return related_parts

    @property
    def related_count(self):
        return len(self.get_related_parts())

    def is_part_low_on_stock(self):
        return self.get_stock_count() < self.minimum_stock

    class Meta:

        verbose_name = _('Part')
        verbose_name_plural = _('Parts')
        ordering = ['name']
        constraints = [UniqueConstraint(fields=['name', 'IPN', 'revision'], name='unique_part')]

    class MPTTMeta:

        parent_attr = 'variant_of'

@receiver(post_save, sender=Part, dispatch_uid='part_post_save_log')
def after_save_part(sender, instance: Part, created, **kwargs):
    from django.conf import settings

    from part import tasks as part_tasks

    if instance and not created and not InvenTree.ready.isImportingData():

        InvenTree.tasks.offload_task(
            part_tasks.notify_low_stock_if_required,
            instance.pk,
            group='notification',
            force_async=not settings.TESTING,
        )

        InvenTree.tasks.offload_task(
            part_tasks.rebuild_supplier_parts,
            instance.pk,
            force_async=True,
            group='part',
        )

class PartPricing(common.models.MetaMixin):

    MAX_PRICING_DEPTH = 50
    currency = models.CharField(default=currency_code_default, max_length=10, verbose_name=_('Currency'), help_text=_('Currency used to cache pricing calculations'), validators=[validators.validate_currency_code],)
    scheduled_for_update = models.BooleanField(default=False)
    part = models.OneToOneField(Part, on_delete=models.CASCADE, related_name='pricing_data', verbose_name=_('Part'),)
    bom_cost_min = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Minimum BOM Cost'), help_text=_('Minimum cost of component parts'),)
    bom_cost_max = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Maximum BOM Cost'), help_text=_('Maximum cost of component parts'),)
    purchase_cost_min = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Minimum Purchase Cost'), help_text=_('Minimum historical purchase cost'),)
    purchase_cost_max = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Maximum Purchase Cost'), help_text=_('Maximum historical purchase cost'),)
    internal_cost_min = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Minimum Internal Price'), help_text=_('Minimum cost based on internal price breaks'),)
    internal_cost_max = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Maximum Internal Price'), help_text=_('Maximum cost based on internal price breaks'),)
    supplier_price_min = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Minimum Supplier Price'), help_text=_('Minimum price of part from external suppliers'),)
    supplier_price_max = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Maximum Supplier Price'), help_text=_('Maximum price of part from external suppliers'),)
    variant_cost_min = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Minimum Variant Cost'), help_text=_('Calculated minimum cost of variant parts'),)
    variant_cost_max = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Maximum Variant Cost'), help_text=_('Calculated maximum cost of variant parts'),)
    override_min = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Minimum Cost'), help_text=_('Override minimum cost'),)
    override_max = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Maximum Cost'), help_text=_('Override maximum cost'),)
    overall_min = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Minimum Cost'), help_text=_('Calculated overall minimum cost'),)
    overall_max = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Maximum Cost'), help_text=_('Calculated overall maximum cost'),)
    sale_price_min = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Minimum Sale Price'), help_text=_('Minimum sale price based on price breaks'),)
    sale_price_max = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Maximum Sale Price'), help_text=_('Maximum sale price based on price breaks'),)
    sale_history_min = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Minimum Sale Cost'), help_text=_('Minimum historical sale price'),)
    sale_history_max = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Maximum Sale Cost'), help_text=_('Maximum historical sale price'),)

    @property
    def is_valid(self):
        return self.updated is not None

    def convert(self, money):
        if money is None:
            return None

        target_currency = currency_code_default()

        try:
            result = convert_money(money, target_currency)
        except MissingRate:
            logger.warning(
                'No currency conversion rate available for %s -> %s',
                money.currency,
                target_currency,
            )
            result = None

        return result

    def schedule_for_update(self, counter: int = 0, refresh: bool = True):
        import InvenTree.ready

        if InvenTree.ready.isImportingData():
            return

        if InvenTree.ready.isRunningMigrations():
            return

        if (
            not self.part
            or not self.part.pk
            or not Part.objects.filter(pk=self.part.pk).exists()
        ):
            logger.warning(
                'Referenced part instance does not exist - skipping pricing update.'
            )
            return

        try:
            if refresh and self.pk:
                self.refresh_from_db()
        except (PartPricing.DoesNotExist, IntegrityError):

            logger.warning(
                "Error refreshing PartPricing instance for part '%s'", self.part
            )
            return

        try:
            p = self.part
            if True:
                p.refresh_from_db()
        except IntegrityError:
            logger.exception(
                "Could not update PartPricing as Part '%s' does not exist", self.part
            )
            return

        if self.scheduled_for_update:

            logger.debug('Pricing for %s already scheduled for update - skipping', p)
            return

        if counter > self.MAX_PRICING_DEPTH:

            logger.debug(
                counter, f'Skipping pricing update for {p} - maximum depth exceeded'
            )
            return

        try:
            self.scheduled_for_update = True
            self.save()
        except IntegrityError:

            logger.exception(
                "Could not save PartPricing for part '%s' to the database", self.part
            )
            return

        import part.tasks as part_tasks

        background = not settings.TESTING or not settings.TESTING_PRICING

        InvenTree.tasks.offload_task(
            part_tasks.update_part_pricing,
            self,
            counter=counter,
            force_async=background,
            group='pricing',
        )

    def update_pricing(
        self,
        counter: int = 0,
        cascade: bool = True,
        previous_min=None,
        previous_max=None,
    ):

        if InvenTree.ready.isImportingData():
            return

        if InvenTree.ready.isRunningMigrations():
            return

        if self.pk is not None:
            try:
                self.refresh_from_db()
            except PartPricing.DoesNotExist:
                pass

        self.update_bom_cost(save=False)
        self.update_purchase_cost(save=False)
        self.update_internal_cost(save=False)
        self.update_supplier_cost(save=False)
        self.update_variant_cost(save=False)
        self.update_sale_cost(save=False)

        self.scheduled_for_update = False

        try:
            self.save()
        except IntegrityError:

            pass

        pricing_changed = False

        if previous_min != self.overall_min or previous_max != self.overall_max:
            pricing_changed = True

        if pricing_changed and cascade:
            self.update_assemblies(counter)
            self.update_templates(counter)

    def update_assemblies(self, counter: int = 0):

        used_in_parts = self.part.get_used_in()

        for p in used_in_parts:
            p.pricing.schedule_for_update(counter=counter + 1)

    def update_templates(self, counter: int = 0):
        templates = self.part.get_ancestors(include_self=False)

        for p in templates:
            p.pricing.schedule_for_update(counter + 1)

    def save(self, *args, **kwargs):

        self.currency = currency_code_default()

        try:
            self.update_overall_cost()
            super().save(*args, **kwargs)
        except Exception:
            log_error('PartPricing.save')
            logger.error(
                "Could not save PartPricing for part '%s' to the database", self.part
            )

    def update_bom_cost(self, save=True):
        if not self.part.assembly:

            self.bom_cost_min = None
            self.bom_cost_max = None

            if save:
                self.save()

            return

        currency_code = common.currency.currency_code_default()

        cumulative_min = Money(0, currency_code)
        cumulative_max = Money(0, currency_code)

        any_min_elements = False
        any_max_elements = False

        for bom_item in self.part.get_bom_items():

            bom_item_min = None
            bom_item_max = None

            for sub_part in bom_item.get_valid_parts_for_allocation():

                if sub_part != bom_item.sub_part and not sub_part.active:
                    continue

                sub_part_pricing = sub_part.pricing

                sub_part_min = self.convert(sub_part_pricing.overall_min)
                sub_part_max = self.convert(sub_part_pricing.overall_max)

                if sub_part_min is not None:
                    if bom_item_min is None or sub_part_min < bom_item_min:
                        bom_item_min = sub_part_min

                if sub_part_max is not None:
                    if bom_item_max is None or sub_part_max > bom_item_max:
                        bom_item_max = sub_part_max

            if bom_item_min is not None:
                bom_item_min *= bom_item.quantity
                cumulative_min += self.convert(bom_item_min)

                any_min_elements = True

            if bom_item_max is not None:
                bom_item_max *= bom_item.quantity
                cumulative_max += self.convert(bom_item_max)

                any_max_elements = True

        if any_min_elements:
            self.bom_cost_min = cumulative_min
        else:
            self.bom_cost_min = None

        if any_max_elements:
            self.bom_cost_max = cumulative_max
        else:
            self.bom_cost_max = None

        if save:
            self.save()

    def update_purchase_cost(self, save=True):

        line_items = OrderModels.PurchaseOrderLineItem.objects.filter(order__status=PurchaseOrderStatus.COMPLETE.value, received__gt=0, part__part=self.part,)

        line_items = line_items.exclude(purchase_price=None)

        purchase_min = None
        purchase_max = None

        for line in line_items:
            if line.purchase_price is None:
                continue

            purchase_cost = self.convert(line.purchase_price / line.part.pack_quantity_native)

            if purchase_cost is None:
                continue

            if purchase_min is None or purchase_cost < purchase_min:
                purchase_min = purchase_cost

            if purchase_max is None or purchase_cost > purchase_max:
                purchase_max = purchase_cost

        if get_global_setting('PRICING_USE_STOCK_PRICING', True):
            items = self.part.stock_items.all()

            days = int(get_global_setting('PRICING_STOCK_ITEM_AGE_DAYS', 0))

            if days > 0:
                date_threshold = InvenTree.helpers.current_date() - timedelta(days=days)
                items = items.filter(updated__gte=date_threshold)

            for item in items:
                cost = self.convert(item.purchase_price)

                if cost is None:
                    continue

                if purchase_min is None or cost < purchase_min:
                    purchase_min = cost

                if purchase_max is None or cost > purchase_max:
                    purchase_max = cost

        self.purchase_cost_min = purchase_min
        self.purchase_cost_max = purchase_max

        if save:
            self.save()

    def update_internal_cost(self, save=True):
        min_int_cost = None
        max_int_cost = None

        if get_global_setting('PART_INTERNAL_PRICE', False):

            for pb in self.part.internalpricebreaks.all():
                cost = self.convert(pb.price)

                if cost is None:

                    continue

                if min_int_cost is None or cost < min_int_cost:
                    min_int_cost = cost

                if max_int_cost is None or cost > max_int_cost:
                    max_int_cost = cost

        self.internal_cost_min = min_int_cost
        self.internal_cost_max = max_int_cost

        if save:
            self.save()

    def update_supplier_cost(self, save=True):
        min_sup_cost = None
        max_sup_cost = None

        if self.part.purchaseable:

            for sp in self.part.supplier_parts.all():

                for pb in sp.pricebreaks.all():
                    if pb.price is None:
                        continue

                    cost = self.convert(pb.price / sp.pack_quantity_native)

                    if cost is None:
                        continue

                    if min_sup_cost is None or cost < min_sup_cost:
                        min_sup_cost = cost

                    if max_sup_cost is None or cost > max_sup_cost:
                        max_sup_cost = cost

        self.supplier_price_min = min_sup_cost
        self.supplier_price_max = max_sup_cost

        if save:
            self.save()

    def update_variant_cost(self, save=True):
        variant_min = None
        variant_max = None

        active_only = get_global_setting('PRICING_ACTIVE_VARIANTS', False)

        if self.part.is_template:
            variants = self.part.get_descendants(include_self=False)

            for v in variants:
                if active_only and not v.active:

                    continue

                v_min = self.convert(v.pricing.overall_min)
                v_max = self.convert(v.pricing.overall_max)

                if v_min is not None:
                    if variant_min is None or v_min < variant_min:
                        variant_min = v_min

                if v_max is not None:
                    if variant_max is None or v_max > variant_max:
                        variant_max = v_max

        self.variant_cost_min = variant_min
        self.variant_cost_max = variant_max

        if save:
            self.save()

    def update_overall_cost(self):
        overall_min = None
        overall_max = None

        min_costs = [self.bom_cost_min, self.purchase_cost_min, self.internal_cost_min]

        max_costs = [self.bom_cost_max, self.purchase_cost_max, self.internal_cost_max]

        purchase_history_override = get_global_setting('PRICING_PURCHASE_HISTORY_OVERRIDES_SUPPLIER', False)

        if get_global_setting('PRICING_USE_SUPPLIER_PRICING', True):

            if self.purchase_cost_min is None or not purchase_history_override:
                min_costs.append(self.supplier_price_min)

            if self.purchase_cost_max is None or not purchase_history_override:
                max_costs.append(self.supplier_price_max)

        if get_global_setting('PRICING_USE_VARIANT_PRICING', True):

            min_costs.append(self.variant_cost_min)
            max_costs.append(self.variant_cost_max)

        for cost in min_costs:
            if cost is None:
                continue

            cost = self.convert(cost)

            if overall_min is None or cost < overall_min:
                overall_min = cost

        for cost in max_costs:
            if cost is None:
                continue

            cost = self.convert(cost)

            if overall_max is None or cost > overall_max:
                overall_max = cost

        if get_global_setting('PART_BOM_USE_INTERNAL_PRICE', False):

            if self.internal_cost_min is not None:
                overall_min = self.internal_cost_min

            if self.internal_cost_max is not None:
                overall_max = self.internal_cost_max

        if self.override_min is not None:
            overall_min = self.convert(self.override_min)

        self.overall_min = overall_min

        if self.override_max is not None:
            overall_max = self.convert(self.override_max)

        self.overall_max = overall_max

    def update_sale_cost(self, save=True):

        min_sell_price = None
        max_sell_price = None

        for pb in self.part.salepricebreaks.all():
            cost = self.convert(pb.price)

            if cost is None:
                continue

            if min_sell_price is None or cost < min_sell_price:
                min_sell_price = cost

            if max_sell_price is None or cost > max_sell_price:
                max_sell_price = cost

        self.sale_price_min = min_sell_price
        self.sale_price_max = max_sell_price

        min_sell_history = None
        max_sell_history = None

        parts = self.part.get_descendants(include_self=True)

        line_items = OrderModels.SalesOrderLineItem.objects.filter(order__status__in=SalesOrderStatusGroups.COMPLETE, part__in=parts)

        line_items = line_items.exclude(sale_price=None)

        for line in line_items:
            cost = self.convert(line.sale_price)

            if cost is None:
                continue

            if min_sell_history is None or cost < min_sell_history:
                min_sell_history = cost

            if max_sell_history is None or cost > max_sell_history:
                max_sell_history = cost

        self.sale_history_min = min_sell_history
        self.sale_history_max = max_sell_history

        if save:
            self.save()

class PartStocktake(models.Model):

    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='stocktakes', verbose_name=_('Part'), help_text=_('Part for stocktake'),)
    item_count = models.IntegerField(default=1, verbose_name=_('Item Count'), help_text=_('Number of individual stock entries at time of stocktake'),)
    quantity = models.DecimalField(max_digits=19, decimal_places=5, validators=[MinValueValidator(0)], verbose_name=_('Quantity'), help_text=_('Total available stock at time of stocktake'),)
    date = models.DateField(verbose_name=_('Date'), help_text=_('Date stocktake was performed'), auto_now_add=True,)
    cost_min = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Minimum Stock Cost'), help_text=_('Estimated minimum cost of stock on hand'),)
    cost_max = InvenTree.fields.InvenTreeModelMoneyField(null=True, blank=True, verbose_name=_('Maximum Stock Cost'), help_text=_('Estimated maximum cost of stock on hand'),)

class PartSellPriceBreak(common.models.PriceBreak):

    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='salepricebreaks', limit_choices_to={'salable': True}, verbose_name=_('Part'),)

    @staticmethod
    def get_api_url():
        return reverse('api-part-sale-price-list')

    class Meta:

        verbose_name = _('Part Sale Price Break')
        unique_together = ('part', 'quantity')

class PartInternalPriceBreak(common.models.PriceBreak):

    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='internalpricebreaks', verbose_name=_('Part'),)

    @staticmethod
    def get_api_url():
        return reverse('api-part-internal-price-list')

    class Meta:

        unique_together = ('part', 'quantity')

class PartStar(models.Model):

    part = models.ForeignKey(Part, on_delete=models.CASCADE, verbose_name=_('Part'), related_name='starred_users',)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'), related_name='starred_parts',)

    class Meta:

        unique_together = ['part', 'user']

class PartCategoryStar(models.Model):

    category = models.ForeignKey(PartCategory, on_delete=models.CASCADE, verbose_name=_('Category'), related_name='starred_users',)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'), related_name='starred_categories',)

    class Meta:

        unique_together = ['category', 'user']

class PartTestTemplate(InvenTree.models.InvenTreeMetadataModel):

    IMPORT_ID_FIELDS = ['key']
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='test_templates', limit_choices_to={'testable': True}, verbose_name=_('Part'),)
    test_name = models.CharField(blank=False, max_length=100, verbose_name=_('Test Name'), help_text=_('Enter a name for the test'),)
    key = models.CharField(blank=True, max_length=100, verbose_name=_('Test Key'), help_text=_('Simplified key for the test'),)
    description = models.CharField(blank=False, null=True, max_length=100, verbose_name=_('Test Description'), help_text=_('Enter description for this test'),)
    enabled = models.BooleanField(default=True, verbose_name=_('Enabled'), help_text=_('Is this test enabled?'))
    required = models.BooleanField(default=True, verbose_name=_('Required'), help_text=_('Is this test required to pass?'),)
    requires_value = models.BooleanField(default=False, verbose_name=_('Requires Value'), help_text=_('Does this test require a value when adding a test result?'),)
    requires_attachment = models.BooleanField(default=False, verbose_name=_('Requires Attachment'), help_text=_('Does this test require a file attachment when adding a test result?'),)
    choices = models.CharField(max_length=5000, verbose_name=_('Choices'), help_text=_('Valid choices for this test (comma-separated)'), blank=True,)

    def __str__(self):
        return ' | '.join([self.part.name, self.test_name])

    @staticmethod
    def get_api_url():
        return reverse('api-part-test-template-list')

    def save(self, *args, **kwargs):
        self.clean()

        super().save(*args, **kwargs)

    def clean(self):
        self.test_name = self.test_name.strip()

        self.key = helpers.generateTestKey(self.test_name)

        if len(self.key) == 0:
            raise ValidationError({
                'test_name': _(
                    'Invalid template name - must include at least one alphanumeric character'
                )
            })

        if self.choices is None:
            self.choices = ''
        else:
            self.choices = str(self.choices).strip()

        if self.choices:
            choice_set = set()

            for choice in self.choices.split(','):
                choice = choice.strip()

                if not choice:
                    continue

                if choice in choice_set:
                    raise ValidationError({'choices': _('Choices must be unique')})

                choice_set.add(choice)

        self.validate_unique()
        super().clean()

    def validate_unique(self, exclude=None):
        if not self.part.testable:
            raise ValidationError({
                'part': _('Test templates can only be created for testable parts')
            })

        parts = self.part.get_ancestors(include_self=True)

        tests = PartTestTemplate.objects.filter(key=self.key, part__in=parts).exclude(pk=self.pk)

        if tests.exists():
            raise ValidationError({
                'test_name': _(
                    'Test template with the same key already exists for part'
                )
            })

        super().validate_unique(exclude)

    def get_choices(self):
        if not self.choices:
            return []

        return [x.strip() for x in self.choices.split(',') if x.strip()]

    class Meta:

        verbose_name = _('Part Test Template')

class BomItem(InvenTree.models.MetadataMixin, InvenTree.models.InvenTreeModel):

    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='bom_items', verbose_name=_('Part'), help_text=_('Select parent part'), limit_choices_to={'assembly': True},)
    sub_part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='used_in', verbose_name=_('Sub part'), help_text=_('Select part to be used in BOM'), limit_choices_to={'component': True},)
    raw_amount = models.CharField(max_length=25, verbose_name=_('Amount'), help_text=_('Amount of sub-part consumed to produce one part'), blank=False, null=False,)
    quantity = models.DecimalField(default=1.0, max_digits=15, decimal_places=5, validators=[MinValueValidator(0)], verbose_name=_('Quantity'), help_text=_('BOM quantity for this BOM item'),)
    optional = models.BooleanField(default=False, verbose_name=_('Optional'), help_text=_('This BOM item is optional'),)
    consumable = models.BooleanField(default=False, verbose_name=_('Consumable'), help_text=_('This BOM item is consumable (it is not tracked in build orders)'),)
    setup_quantity = models.DecimalField(default=0, max_digits=15, decimal_places=5, validators=[MinValueValidator(0)], verbose_name=_('Setup Quantity'), help_text=_('Extra required quantity for a build, to account for setup losses'),)
    attrition = models.DecimalField(default=0, max_digits=6, decimal_places=3, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_('Attrition'), help_text=_('Estimated attrition for a build, expressed as a percentage (0-100)'),)
    rounding_multiple = models.DecimalField(null=True, blank=True, default=None, max_digits=15, decimal_places=5, validators=[MinValueValidator(0)], verbose_name=_('Rounding Multiple'), help_text=_('Round up required production quantity to nearest multiple of this value'),)
    reference = models.CharField(max_length=5000, blank=True, verbose_name=_('Reference'), help_text=_('BOM item reference'),)
    note = models.CharField(max_length=500, blank=True, verbose_name=_('Note'), help_text=_('BOM item notes'),)
    checksum = models.CharField(max_length=128, blank=True, verbose_name=_('Checksum'), help_text=_('BOM line checksum'),)
    validated = models.BooleanField(default=False, verbose_name=_('Validated'), help_text=_('This BOM item has been validated'),)
    inherited = models.BooleanField(default=False, verbose_name=_('Gets inherited'), help_text=_('This BOM item is inherited by BOMs for variant parts'),)
    allow_variants = models.BooleanField(default=False, verbose_name=_('Allow Variants'), help_text=_('Stock items for variant parts can be used for this BOM item'),)

    def __str__(self):
        return f'{decimal2string(self.quantity)} x {self.sub_part.full_name} to make {self.part.full_name}'

    @staticmethod
    def get_api_url():
        return reverse('api-bom-list')

    def get_assemblies(self):
        assemblies = [self.part]

        if self.inherited:
            assemblies += list(self.part.get_descendants(include_self=False))

        return assemblies

    def get_valid_parts_for_allocation(
        self,
        allow_variants: bool = True,
        allow_substitutes: bool = True,
        allow_inactive: bool = True,
    ):

        parts = set()

        parts.add(self.sub_part)

        if allow_variants and self.allow_variants:
            for variant in self.sub_part.get_descendants(include_self=False):
                parts.add(variant)

        if allow_substitutes:
            for sub in self.substitutes.all():
                parts.add(sub.part)

                if allow_variants and self.allow_variants:
                    for sub_variant in sub.part.get_descendants(include_self=False):
                        parts.add(sub_variant)

        valid_parts = []

        for p in parts:

            if p.trackable != self.sub_part.trackable:
                continue

            if not allow_inactive and not p.active:
                continue

            valid_parts.append(p)

        return valid_parts

    def is_stock_item_valid(self, stock_item):
        return stock_item.part in self.get_valid_parts_for_allocation()

    def get_stock_filter(self):
        return Q(part__in=self.get_valid_parts_for_allocation())

    def set_quantity(self, quantity: Decimal | str | float):
        self.raw_amount = quantity
        self.recalculate_quantity()

    def recalculate_quantity(self):
        if self.raw_amount is None or self.raw_amount == '':
            self.raw_amount = self.quantity

        try:
            quantity = InvenTree.conversion.convert_physical_value(self.raw_amount, self.sub_part.units, strip_units=False)

            if not self.sub_part.units and not InvenTree.conversion.is_dimensionless(
                quantity
            ):
                raise ValidationError({
                    'raw_amount': _('Invalid quantity - no units specified for part')
                })

            allow_zero_qty = get_global_setting('PART_BOM_ALLOW_ZERO_QUANTITY', False)

            if allow_zero_qty:
                if float(quantity.magnitude) < 0:
                    raise ValidationError({
                        'raw_amount': _(
                            'Quantity must be greater than or equal to zero'
                        )
                    })

            else:
                if float(quantity.magnitude) <= 0:
                    raise ValidationError({
                        'raw_amount': _('Quantity must be greater than zero')
                    })

            quantity = Decimal(quantity.magnitude)

        except ValidationError as e:
            raise ValidationError({'raw_amount': e.messages})

        try:
            self.quantity = Decimal(quantity).quantize(Decimal('0.00001'), rounding=ROUND_HALF_UP)
        except InvalidOperation:
            msg = _('Invalid quantity provided')
            raise ValidationError({'quantity': msg, 'raw_amount': msg})

    def delete(self):
        import part.tasks as part_tasks

        self.check_part_lock(self.part)

        assemblies = self.get_assemblies()
        super().delete()

        for assembly in assemblies:

            InvenTree.tasks.offload_task(
                part_tasks.check_bom_valid, assembly.pk, group='part'
            )

    def save(self, *args, **kwargs):
        import part.tasks as part_tasks

        self.clean()

        check_lock = kwargs.pop('check_lock', True)

        if check_lock:
            self.check_part_lock(self.part)

        db_instance = self.get_db_instance()

        deltas = self.get_field_deltas()

        if 'part' in deltas and (old_part := deltas['part'].get('old', None)):
            if check_lock:
                self.check_part_lock(old_part)

        self.validated = self.is_line_valid

        super().save(*args, **kwargs)

        if not db_instance or any(f in deltas for f in self.hash_fields()):

            assemblies = set()

            if db_instance:

                assemblies.update(db_instance.get_assemblies())

            assemblies.update(self.get_assemblies())

            for assembly in assemblies:

                InvenTree.tasks.offload_task(
                    part_tasks.check_bom_valid, assembly.pk, group='part'
                )

    def check_part_lock(self, assembly):
        if not get_global_setting('PART_ENABLE_LOCKING'):
            return

        if assembly.locked:
            raise ValidationError(_('BOM item cannot be modified - assembly is locked'))

        if self.inherited:
            for part in assembly.get_descendants(include_self=False):
                if part.locked:
                    raise ValidationError(
                        _('BOM item cannot be modified - variant assembly is locked')
                    )

    def hash_fields(self) -> list[str]:
        return [
            'part',
            'part_id',
            'sub_part',
            'sub_part_id',
            'quantity',
            'setup_quantity',
            'attrition',
            'rounding_multiple',
            'reference',
            'optional',
            'inherited',
            'consumable',
            'allow_variants',
        ]

    def get_item_hash(self) -> str:

        result_hash = hashlib.md5(b'')

        for field in self.hash_fields():

            value = getattr(self, field, None)

            if value is None:
                value = ''

            if value is not None and field in [
                'quantity',
                'attrition',
                'setup_quantity',
                'rounding_multiple',
            ]:
                try:
                    value = normalize(value)

                    if not value or value <= 0:
                        continue
                except Exception:
                    pass

            result_hash.update(str(value).encode())

        return str(result_hash.digest())

    def validate_hash(self, valid=True):
        if valid:
            self.checksum = self.get_item_hash()
        else:
            self.checksum = ''

        self.save(check_lock=False)

    @property
    def is_line_valid(self):

        if len(self.checksum) == 0:
            return False

        return self.get_item_hash() == self.checksum

    @property
    def is_consumable(self) -> bool:
        return self.consumable or self.sub_part.consumable

    @staticmethod
    def consumable_filter(consumable: bool = True, prefix: str = '') -> Q:
        f = Q(**{f'{prefix}consumable': True}) | Q(**{f'{prefix}sub_part__consumable': True})

        return f if consumable else ~f

    def clean(self):
        super().clean()

        self.recalculate_quantity()

        try:

            if self.sub_part:
                self.sub_part.check_add_to_bom(self.part, raise_error=True)

                if self.sub_part.trackable:
                    if self.quantity != int(self.quantity):
                        raise ValidationError({
                            'quantity': _(
                                'Quantity must be integer value for trackable parts'
                            )
                        })

                    if not self.part.trackable:
                        self.part.trackable = True
                        self.part.clean()
                        self.part.save()
            else:
                raise ValidationError({'sub_part': _('Sub part must be specified')})
        except Part.DoesNotExist:
            raise ValidationError({'sub_part': _('Sub part must be specified')})

    def can_build_quantity(self, available_stock: float) -> int:

        available_stock = Decimal(max(0, available_stock - self.setup_quantity))
        quantity_decimal = Decimal(self.quantity)
        attrition_decimal = Decimal(self.attrition) / 100
        n = quantity_decimal * (1 + attrition_decimal)

        if n <= 0:
            return 0.0

        return int(Decimal(available_stock) / n)

    def get_required_quantity(self, build_quantity: float) -> float:

        required = self.quantity * build_quantity

        if self.attrition > 0:
            try:

                attrition = Decimal(self.attrition) / Decimal(100)
                required *= 1 + attrition
            except Exception:
                log_error('bom_item.get_required_quantity')

        if self.setup_quantity > 0:
            try:
                setup_quantity = Decimal(self.setup_quantity)
                required += setup_quantity
            except Exception:
                log_error('bom_item.get_required_quantity')

        if self.rounding_multiple and self.rounding_multiple > 0:
            try:
                round_up = Decimal(self.rounding_multiple)
                value = Decimal(required)
                value = math.ceil(value / round_up) * round_up
                required = float(value)
            except InvalidOperation:
                log_error('bom_item.get_required_quantity')

        return required

    class Meta:

        verbose_name = _('BOM Item')

@receiver(post_save, sender=BomItem, dispatch_uid='update_bom_build_lines')
def update_bom_build_lines(sender, instance, created, **kwargs):
    if InvenTree.ready.canAppAccessDatabase() and not InvenTree.ready.isImportingData():
        import build.tasks

        InvenTree.tasks.offload_task(
            build.tasks.update_build_order_lines, instance.pk, group='build'
        )

@receiver(post_save, sender=BomItem, dispatch_uid='post_save_bom_item')
@receiver(
    post_save, sender=PartSellPriceBreak, dispatch_uid='post_save_sale_price_break'
)
@receiver(
    post_save,
    sender=PartInternalPriceBreak,
    dispatch_uid='post_save_internal_price_break',
)
def update_pricing_after_edit(sender, instance, created, **kwargs):

    if (
        InvenTree.ready.canAppAccessDatabase(allow_test=settings.TESTING_PRICING)
        and not InvenTree.ready.isImportingData()
    ):
        if instance.part:
            instance.part.schedule_pricing_update(create=True)

@receiver(post_delete, sender=BomItem, dispatch_uid='post_delete_bom_item')
@receiver(
    post_delete, sender=PartSellPriceBreak, dispatch_uid='post_delete_sale_price_break'
)
@receiver(
    post_delete,
    sender=PartInternalPriceBreak,
    dispatch_uid='post_delete_internal_price_break',
)
def update_pricing_after_delete(sender, instance, **kwargs):

    if (
        InvenTree.ready.canAppAccessDatabase(allow_test=settings.TESTING_PRICING)
        and not InvenTree.ready.isImportingData()
    ):
        if instance.part:
            instance.part.schedule_pricing_update(create=False)

class BomItemSubstitute(InvenTree.models.InvenTreeMetadataModel):

    bom_item = models.ForeignKey(BomItem, on_delete=models.CASCADE, related_name='substitutes', verbose_name=_('BOM Item'), help_text=_('Parent BOM item'),)
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='substitute_items', verbose_name=_('Part'), help_text=_('Substitute part'), limit_choices_to={'component': True},)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude=exclude)

        if self.part == self.bom_item.sub_part:
            raise ValidationError({
                'part': _('Substitute part cannot be the same as the master part')
            })

    @staticmethod
    def get_api_url():
        return reverse('api-bom-substitute-list')

    class Meta:

        verbose_name = _('BOM Item Substitute')

        unique_together = ('part', 'bom_item')

class PartRelated(InvenTree.models.InvenTreeMetadataModel):

    part_1 = models.ForeignKey(Part, related_name='related_parts_1', verbose_name=_('Part 1'), on_delete=models.CASCADE,)
    part_2 = models.ForeignKey(Part, related_name='related_parts_2', on_delete=models.CASCADE, verbose_name=_('Part 2'), help_text=_('Select Related Part'),)
    note = models.CharField(max_length=500, blank=True, verbose_name=_('Note'), help_text=_('Note for this relationship'),)

    def __str__(self):
        return f'{self.part_1} <--> {self.part_2}'

    def save(self, *args, **kwargs):
        self.clean()
        self.validate_unique()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.part_1 == self.part_2:
            raise ValidationError(
                _('Part relationship cannot be created between a part and itself')
            )

        if PartRelated.objects.filter(part_1=self.part_2, part_2=self.part_1).exists():
            raise ValidationError(_('Duplicate relationship already exists'))

    class Meta:

        unique_together = ('part_1', 'part_2')