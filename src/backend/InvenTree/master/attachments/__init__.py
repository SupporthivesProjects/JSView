import logging

from .base import REGISTRY, Built  # noqa: F401
from . import pdf, xlsx  # noqa: F401  (importing registers every attachment)

logger = logging.getLogger('inventree')


def build_attachments(keys, ctx):
    """Build each requested attachment independently.

    One failing attachment never blocks the others. Returns (files, errors).
    """
    files = []
    errors = []
    seen = set()

    for key in keys:
        key = (key or '').strip()

        if not key or key in seen:
            continue

        seen.add(key)
        cls = REGISTRY.get(key)

        if cls is None:
            logger.error('Unknown attachment key %r (known: %s)', key, ', '.join(sorted(REGISTRY)))
            errors.append(f'{key}: unknown attachment key')
            continue

        try:
            files.append(cls().build(ctx))
        except Exception as exc:
            logger.exception('Attachment %s failed to build', key)
            errors.append(f'{key}: {exc}')

    return files, errors