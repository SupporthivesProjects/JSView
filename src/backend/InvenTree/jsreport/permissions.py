"""Permission class for the JS Report API."""

from rest_framework.permissions import BasePermission

from users.permissions import check_user_role
from users.ruleset import RuleSetEnum


# HTTP method -> ruleset permission
METHOD_PERMISSION_MAP = {
    'GET': 'view',
    'HEAD': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete',
}


class JSReportPermission(BasePermission):
    """
    Permission for JS Report endpoints.

    Controlled by the 'Report -> Reports' ruleset.
    Applies to all users, including superusers.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # OPTIONS only returns API metadata.
        if request.method == 'OPTIONS':
            return True

        permission = METHOD_PERMISSION_MAP.get(request.method)

        if permission is None:
            return False

        return check_user_role(
            user,
            RuleSetEnum.REPORT,
            permission,
            enforce_superuser=True,
        )