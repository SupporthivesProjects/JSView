"""Mixin classes for the importer app."""

from collections import OrderedDict
from difflib import get_close_matches
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import structlog
import tablib
from rest_framework import serializers
from rest_framework.response import Response
from taggit.serializers import TagListSerializerField

import data_importer.serializers
import data_importer.tasks
import InvenTree.exceptions
import InvenTree.serializers
from data_importer.models import DataImportSession
from InvenTree.helpers import str2bool
from InvenTree.tasks import offload_task
from plugin import PluginMixinEnum, registry

logger = structlog.get_logger('inventree')


class DataImportSerializerMixin:
    """Mixin class for adding data import functionality to a DRF serializer.

    Provides generic functionality to take tabular data (from an uploaded file)
    and map/validate/save it against this serializer.

    Attributes:
        import_only_fields: List of field names which are only used during data import
        import_exclude_fields: List of field names which are excluded during data import
        import_lookup_fields: List of field names used to match an existing row (for update-or-create)
        import_child_fields: List of child fields which are importable (dot notation)
    """

    import_only_fields = []
    import_exclude_fields = []
    import_lookup_fields = []
    import_child_fields = []

    def get_import_only_fields(self, **kwargs) -> list:
        """Return the list of field names which are only used during data import."""
        return self.import_only_fields

    def get_import_exclude_fields(self, **kwargs) -> list:
        """Return the list of field names which are excluded during data import."""
        return self.import_exclude_fields

    def get_import_lookup_fields(self, **kwargs) -> list:
        """Return the list of field names used to look up an existing instance."""
        return self.import_lookup_fields

    def __init__(self, *args, **kwargs):
        """Initialise the DataImportSerializerMixin.

        Determine if the serializer is being used for data import,
        and if so, adjust the serializer fields accordingly.
        """
        self._importing_data = importing = kwargs.pop('importing', False)

        super().__init__(*args, **kwargs)

        self.request = self.context.get('request')

        if importing:
            # Exclude fields which are not required for data import
            for field in self.get_import_exclude_fields(**kwargs):
                self.fields.pop(field, None)

            # Duplication options are never used for data import
            for field in [
                name
                for name, field in self.fields.items()
                if isinstance(field, InvenTree.serializers.DuplicateOptionsSerializer)
            ]:
                self.fields.pop(field, None)
        else:
            # Exclude fields which are only used for data import
            for field in self.get_import_only_fields(**kwargs):
                self.fields.pop(field, None)

    def get_importable_fields(self) -> dict:
        """Return a dict of fields which can be imported against this serializer instance.

        Returns:
            dict: A dictionary of field names and field objects
        """
        fields = {}

        for name, field in self.fields.items():
            # Skip read-only fields - can't write to them on import
            if getattr(field, 'read_only', False):
                continue

            # Skip tags fields
            # TODO: Implement tag field import support
            if issubclass(field.__class__, TagListSerializerField):
                continue

            # Top-level serializer fields can be imported with dot notation
            if issubclass(field.__class__, serializers.Serializer):
                fields.update(self.get_child_fields(name, field))
                continue

            # Skip 'many' fields (e.g. nested serializers) - not supported yet
            if getattr(field, 'many', False):
                continue

            fields[name] = field

        return fields

    def get_child_fields(self, field_name: str, field) -> dict:
        """Return a dictionary of child fields for a given field.

        Only child fields which match the 'import_child_fields' list will be returned.
        """
        child_fields = {}

        if sub_fields := getattr(field, 'fields', None):
            for sub_name, sub_field in sub_fields.items():
                name = f'{field_name}.{sub_name}'

                if name in self.import_child_fields:
                    sub_field.parent_field = field
                    child_fields[name] = sub_field

        return child_fields

    @classmethod
    def arrange_import_headers(cls, headers: list) -> list:
        """Optional method to arrange the import headers. Override in subclass if required."""
        return headers

    def generate_import_headers(self) -> OrderedDict:
        """Generate a description of importable columns for this serializer.

        Returns an ordered dict of field names to metadata, e.g.:

        {
            'name': {'label': 'Name', 'required': True, 'help_text': ...},
            ...
        }
        """
        fields = self.get_importable_fields()
        field_names = self.arrange_import_headers(list(fields.keys()))

        headers = OrderedDict()

        for field_name in field_names:
            field = fields[field_name]

            label = getattr(field, 'label', field_name)

            if parent := getattr(field, 'parent_field', None):
                label = f'{parent.label}.{label}'

            headers[field_name] = {
                'label': str(label),
                'required': getattr(field, 'required', False),
                'help_text': str(getattr(field, 'help_text', '') or ''),
                'choices': getattr(field, 'choices', None),
            }

        return headers

    def match_headers(self, uploaded_headers: list, cutoff: float = 0.6) -> dict:
        """Attempt to automatically map uploaded column headers to importable fields.

        Arguments:
            uploaded_headers: List of column headers found in the uploaded file
            cutoff: Similarity cutoff (0-1) used for fuzzy matching

        Returns:
            dict: {uploaded_header: matched_field_name or None}
        """
        importable = self.generate_import_headers()

        # Build a lookup of possible match targets -> field_name
        candidates = {}
        for field_name, meta in importable.items():
            candidates[field_name.lower()] = field_name
            candidates[str(meta['label']).lower()] = field_name

        mapping = {}

        for header in uploaded_headers:
            key = str(header).strip().lower()

            if key in candidates:
                mapping[header] = candidates[key]
                continue

            matches = get_close_matches(key, candidates.keys(), n=1, cutoff=cutoff)
            mapping[header] = candidates[matches[0]] if matches else None

        return mapping

    def get_nested_value(self, row: dict, key: str) -> Any:
        """Get/set helper - mirrors exporter's dot-notation nested lookup."""
        keys = key.split('.')
        value = row

        for key in keys:
            if not value:
                break
            if not key:
                continue
            value = value.get(key, None)

        return value

    def build_row_data(self, row: dict, mapping: dict) -> dict:
        """Given a raw uploaded row {uploaded_col: value} and a confirmed
        mapping {uploaded_col: field_name}, construct the payload to validate.
        """
        payload = {}

        for uploaded_col, field_name in mapping.items():
            if not field_name:
                continue
            payload[field_name] = row.get(uploaded_col)

        return payload

    def get_matching_instance(self, validated_data: dict):
        """Attempt to find an existing instance to update, using import_lookup_fields.

        Returns None if no lookup fields are configured, or no match is found
        (in which case a new instance should be created).
        """
        lookup_fields = self.get_import_lookup_fields()

        if not lookup_fields:
            return None

        model = getattr(self.Meta, 'model', None)

        if not model:
            return None

        lookup = {
            f: validated_data[f] for f in lookup_fields if validated_data.get(f) not in [None, '']
        }

        if not lookup:
            return None

        return model.objects.filter(**lookup).first()

    def validate_row(self, row: dict, mapping: dict) -> tuple[bool, dict]:
        """Validate a single uploaded row against this serializer.

        Returns:
            (is_valid, result) where result is either validated_data or serializer errors
        """
        payload = self.build_row_data(row, mapping)

        instance = self.get_matching_instance(payload)

        serializer = self.__class__(
            instance=instance,
            data=payload,
            context=self.context,
            importing=True,
        )

        if serializer.is_valid():
            return True, {'data': serializer.validated_data, 'instance': instance}

        return False, {'errors': serializer.errors}

    def import_row(self, row: dict, mapping: dict):
        """Validate and save a single uploaded row.

        Returns:
            (success: bool, result: instance | error dict)
        """
        is_valid, result = self.validate_row(row, mapping)

        if not is_valid:
            return False, result['errors']

        serializer = self.__class__(
            instance=result['instance'],
            data=self.build_row_data(row, mapping),
            context=self.context,
            importing=True,
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return True, instance

    @staticmethod
    def load_dataset(data_file, file_format: str = None) -> tablib.Dataset:
        """Load an uploaded file into a tablib Dataset (headers + rows)."""
        data_file.seek(0)
        return tablib.Dataset().load(data_file.read(), format=file_format)


class DataImportViewMixin:
    """An API view mixin for importing data via an uploaded file.

    Flow:
        1. POST with a file -> creates an ImportSession, detects columns, returns suggested mapping
        2. PATCH with confirmed mapping -> kicks off background import task
        3. GET -> poll session status/progress/errors
    """

    def is_importing(self) -> bool:
        """Determine if the view is currently handling an import request."""
        if request := getattr(self, 'request', None):
            return str2bool(
                request.data.get('import') or request.query_params.get('import')
            )

        return False

    def get_plugin(self, plugin_slug=None):
        """Return the plugin instance associated with the import request."""
        PLUGIN_KEY = 'import_plugin'

        if not plugin_slug:
            if request := getattr(self, 'request', None):
                plugin_slug = request.data.get(PLUGIN_KEY) or request.query_params.get(
                    PLUGIN_KEY
                )

        if plugin_slug:
            return registry.get_plugin(
                plugin_slug, active=True, with_mixin=PluginMixinEnum.IMPORTER
            )

        return None

    def get_serializer(self, *args, **kwargs):
        """Return the appropriate serializer for import-related requests."""
        importing = kwargs.pop('importing', None)

        if importing is None:
            method = str(getattr(self.request, 'method', '')).lower()
            importing = method in ['options', 'post'] and self.is_importing()

        if importing:
            import_kwargs = {
                'plugin': self.get_plugin(),
                'request': self.request,
                'data': kwargs.get('data'),
                'context': kwargs.get('context'),
            }

            try:
                serializer_class = self.get_serializer_class()
                import_kwargs['serializer_class'] = serializer_class
                import_kwargs['model_class'] = serializer_class.Meta.model
                import_kwargs['view_class'] = self.__class__
            except AttributeError:
                import_kwargs['serializer_class'] = None
                import_kwargs['model_class'] = None
                import_kwargs['view_class'] = None

            return data_importer.serializers.DataImportOptionsSerializer(
                *args, **import_kwargs
            )
        else:
            return super().get_serializer(*args, **kwargs)

    def create_import_session(self, import_plugin, data_file, import_context: dict):
        """Create a new ImportSession from an uploaded file, detect columns, and
        return a suggested column mapping.
        """
        serializer_class = self.get_serializer_class()

        if not issubclass(serializer_class, DataImportSerializerMixin):
            raise ValidationError(
                'Serializer class must inherit from DataImportSerializerMixin'
            )

        try:
            dataset = serializer_class.load_dataset(data_file)
        except Exception as e:
            InvenTree.exceptions.log_error('load_dataset')
            raise ValidationError(_('Could not parse uploaded file: %(error)s') % {'error': str(e)})

        session = DataImportSession.objects.create(
            user=getattr(self.request, 'user', None),
            data_file=data_file,
            columns=list(dataset.headers or []),
            row_count=len(dataset),
        )

        context = self.get_serializer_context()
        serializer = serializer_class(context=context, importing=True)

        mapping = serializer.match_headers(dataset.headers or [])

        # Allow the plugin to adjust the suggested mapping
        if import_plugin and hasattr(import_plugin, 'update_mapping'):
            try:
                mapping = import_plugin.update_mapping(mapping, import_context)
            except Exception:
                InvenTree.exceptions.log_error('update_mapping', plugin=import_plugin.slug)

        session.field_mapping = mapping
        session.save()

        return session, mapping

    def commit_import_session(self, session: DataImportSession, import_plugin, import_context: dict):
        """Kick off the background task which validates and saves every row."""
        session.mark_importing()

        offload_task(
            data_importer.tasks.import_data,
            self.__class__,
            getattr(session.user, 'id', None),
            session.id,
            getattr(import_plugin, 'slug', None),
            import_context,
            group='importer',
        )

        session.refresh_from_db()
        return session

    def post(self, request, *args, **kwargs):
        """Handle file upload -> create session + suggested mapping."""
        from data_importer.serializers import DataImportSessionSerializer

        if not self.is_importing():
            return super().post(request, *args, **kwargs)

        data_file = request.data.get('data_file')

        if not data_file:
            raise ValidationError(_('No file provided'))

        plugin_slug = request.data.get('import_plugin')
        import_plugin = self.get_plugin(plugin_slug)
        import_context = {k: v for k, v in request.data.items() if k.startswith('import_')}

        session, mapping = self.create_import_session(import_plugin, data_file, import_context)

        return Response(
            {
                **DataImportSessionSerializer(session).data,
                'suggested_mapping': mapping,
            },
            status=201,
        )

    def patch(self, request, *args, **kwargs):
        """Handle confirmed column mapping -> trigger background import."""
        from data_importer.serializers import DataImportSessionSerializer

        if not self.is_importing():
            return super().patch(request, *args, **kwargs)

        session_id = request.data.get('session')
        session = DataImportSession.objects.filter(pk=session_id).first()

        if not session:
            raise ValidationError(_('Import session not found'))

        mapping = request.data.get('field_mapping')

        if mapping:
            session.field_mapping = mapping
            session.save()

        plugin_slug = request.data.get('import_plugin')
        import_plugin = self.get_plugin(plugin_slug)
        import_context = {k: v for k, v in request.data.items() if k.startswith('import_')}

        session = self.commit_import_session(session, import_plugin, import_context)

        return Response(DataImportSessionSerializer(session).data, status=200)