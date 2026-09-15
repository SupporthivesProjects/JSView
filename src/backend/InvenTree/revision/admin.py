import json

from django.contrib import admin
from django.utils.safestring import mark_safe

from revision import models as revision_models


@admin.register(revision_models.CostCardVersion)
class CostCardVersionAdmin(admin.ModelAdmin):
    """Admin class for the CostCardVersion model."""

    list_display = ('cost_card', 'version', 'created_by', 'created_at', 'active')
    search_fields = ('cost_card__number', 'created_by__username', 'created_by__first_name', 'created_by__last_name')
    autocomplete_fields = ('cost_card', 'created_by')
    # list_filter = ('active', 'created_at')
    ordering = ('-created_at', '-version')
    readonly_fields = ('cost_card', 'version', 'created_by', 'created_at', 'active', 'data_prettified')
    fieldsets = (
        ('Version Information', {
            'fields': ('cost_card', 'version', 'created_by', 'created_at', 'active'),
        }),
        ('Historical Snapshot', {
            'fields': ('data_prettified',),
        }),
    )

    class Media:
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/jsoneditor@9.10.5/dist/jsoneditor.min.css',
            )
        }
        js = (
            'https://cdn.jsdelivr.net/npm/jsoneditor@9.10.5/dist/jsoneditor.min.js',
        )

    def data_prettified(self, instance):
        if not instance.pk:
            return '-'

        json_str = json.dumps(instance.data, indent=2, ensure_ascii=False)
        container_id = f'jsoneditor-{instance.pk}'

        html = f'''
        <style>
        .field-data_prettified,
        .field-data_prettified .readonly,
        .form-row.field-data_prettified {{
            max-width: none !important;
            width: 100% !important;
        }}
        #{container_id}-wrap {{
            width: 100%;
            max-width: 1600px;
        }}
        #{container_id} {{
            width: 100%;
            height: 750px;
        }}
        .jsoneditor {{
            border: 1px solid #ccc;
        }}
        </style>
        <div id="{container_id}-wrap">
            <div id="{container_id}"></div>
        </div>
        <script id="{container_id}-data" type="application/json">{json_str}</script>
        <script>
        (function() {{
            var el = document.getElementById("{container_id}");
            var data = JSON.parse(document.getElementById("{container_id}-data").textContent);
            var editor = new JSONEditor(el, {{
                mode: "view",
                mainMenuBar: true,
                navigationBar: true,
                statusBar: true,
                search: true
            }});
            editor.set(data);
            editor.expandAll();
        }})();
        </script>
        '''
        return mark_safe(html)

    data_prettified.short_description = 'Data'