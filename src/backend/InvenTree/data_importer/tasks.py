"""Background tasks for the importer app."""

from django.contrib.auth.models import User

import structlog

from data_importer.models import DataImportSession

logger = structlog.get_logger('inventree')


def import_data(
    view_class,
    user_id,
    session_id: int,
    plugin_key: str,
    import_context: dict,
):
    """Perform the data import task: parse the file, validate + save each row.

    This runs in a background worker so a large file doesn't block the request.
    """
    from plugin import registry

    if (session := DataImportSession.objects.filter(pk=session_id).first()) is None:
        logger.warning('import_data: Session not found: %d', session_id)
        return

    user = User.objects.filter(pk=user_id).first() if user_id else None
    import_plugin = registry.get_plugin(plugin_key, active=True) if plugin_key else None

    view = view_class()
    serializer_class = view.get_serializer_class()

    try:
        dataset = serializer_class.load_dataset(session.data_file)
    except Exception as e:
        session.mark_failure(error=str(e))
        return

    serializer = serializer_class(context={'request': None}, importing=True)
    mapping = session.field_mapping or {}

    errors = []
    completed = 0

    for i, row in enumerate(dataset.dict):
        # Let the plugin transform/enrich the row before validation, if it wants to
        if import_plugin and hasattr(import_plugin, 'transform_row'):
            try:
                row = import_plugin.transform_row(row, import_context)
            except Exception as e:
                errors.append({'row': i, 'error': str(e)})
                continue

        success, result = serializer.import_row(row, mapping)

        if success:
            completed += 1
        else:
            errors.append({'row': i, 'error': result})

        session.completed_count = completed
        session.progress = int(100 * (i + 1) / max(session.row_count, 1))
        session.errors = errors
        session.save(update_fields=['completed_count', 'progress', 'errors'])

    session.mark_complete() if not errors else session.mark_complete(with_errors=True)