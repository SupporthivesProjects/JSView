from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

import structlog

import InvenTree.ready

logger = structlog.get_logger('inventree')


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        from users import signals  # noqa: F401

        if (
            not InvenTree.ready.isPluginRegistryLoaded()
            or not InvenTree.ready.isInMainThread()
        ):
            return

        if InvenTree.ready.isRunningMigrations():
            return  # pragma: no cover

        if InvenTree.ready.canAppAccessDatabase(allow_test=True):
            try:
                from users.tasks import rebuild_all_permissions

                rebuild_all_permissions()
            except (OperationalError, ProgrammingError):  # pragma: no cover
                pass
            except Exception as e:  # pragma: no cover
                logger.exception('Failed to rebuild permissions: %s', e)

            try:
                self.update_owners()
            except (OperationalError, ProgrammingError):  # pragma: no cover
                pass
            except Exception as e:  # pragma: no cover
                logger.exception('Failed to update owners: %s', e)

    def update_owners(self):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group

        from users.models import Owner

        for group in Group.objects.all():
            Owner.create(group)

        for user in get_user_model().objects.all():
            Owner.create(user)