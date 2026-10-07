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

    Controlled by the per-report ruleset set on the view as `report_role`
    (e.g. RuleSetEnum.REPORT_OPEN_ORDER).
    Superusers have all permissions by default.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Superuser bypasses ruleset checks.
        if user.is_superuser:
            return True

        # OPTIONS only returns API metadata.
        if request.method == 'OPTIONS':
            return True

        permission = METHOD_PERMISSION_MAP.get(request.method)

        if permission is None:
            return False

        # Each report view defines its own ruleset; deny if missing.
        role = getattr(view, 'report_role', None)

        if role is None:
            return False

        return check_user_role(
            user,
            # RuleSetEnum.REPORT,
            role,
            permission,
            enforce_superuser=True,
        )