"""Serializers for the importer app."""

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

import InvenTree.exceptions
from common.models import DataImportSession
from plugin import PluginMixinEnum, registry


class DataImportOptionsSerializer(serializers.Serializer):
    """Serializer for defining a data import session's options (mirrors DataExportOptionsSerializer)."""

    class Meta:
        fields = ['import_format', 'import_plugin']

    def __init__(self, *args, **kwargs):
        self.Meta.fields = ['import_format', 'import_plugin']

        serializer_class = kwargs.pop('serializer_class', None)
        model_class = kwargs.pop('model_class', None)
        view_class = kwargs.pop('view_class', None)
        request = kwargs.pop('request', None)

        if plugin := kwargs.pop('plugin', None):
            if hasattr(plugin, 'get_import_options_serializer'):
                plugin_serializer = plugin.get_import_options_serializer()

                if plugin_serializer:
                    for key, field in plugin_serializer.fields.items():
                        if key.startswith('import_') and key not in self.Meta.fields:
                            self.Meta.fields.append(key)
                            setattr(self, key, field)

        plugin_options = []

        for plugin in registry.with_mixin(PluginMixinEnum.IMPORTER):
            try:
                supports_import = plugin.supports_import(
                    model_class,
                    user=request.user if request else None,
                    serializer_class=serializer_class,
                    view_class=view_class,
                )
            except Exception:
                InvenTree.exceptions.log_error('supports_import', plugin=plugin.slug)
                supports_import = False

            if supports_import:
                plugin_options.append((plugin.slug, plugin.name))

        self.fields['import_plugin'].choices = plugin_options

        super().__init__(*args, **kwargs)

    import_format = serializers.ChoiceField(
        choices=[('csv', 'CSV'), ('xlsx', 'XLSX'), ('tsv', 'TSV'), ('json', 'JSON')],
        default='csv',
        label=_('Import Format'),
    )

    import_plugin = serializers.ChoiceField(
        choices=[],
        default='inventree-importer',
        label=_('Import Plugin'),
    )


class DataImportSessionSerializer(serializers.ModelSerializer):
    """Serializer for reporting import session status/progress/errors to the client."""

    class Meta:
        model = DataImportSession
        fields = [
            'pk', 'status', 'columns', 'field_mapping',
            'row_count', 'completed_count', 'progress', 'errors',
        ]
        read_only_fields = fields