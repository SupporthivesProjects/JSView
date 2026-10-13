import logging
from .base import REGISTRY
from . import pdf, xlsx  # noqa: F401  (importing registers the classes)

logger = logging.getLogger('inventree')


def build_attachments(keys, ctx):
    built, errors = [], []
    for key in keys:
        cls = REGISTRY.get(key)
        if cls is None:
            errors.append(f'Unknown attachment: {key}')
            continue
        try:
            built.append(cls().build(ctx))
        except Exception as exc:
            logger.exception('Attachment %s failed', key)
            errors.append(f'{key}: {exc}')
    return built, errors