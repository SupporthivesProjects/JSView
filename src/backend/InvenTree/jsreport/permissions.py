from rest_framework.permissions import BasePermission

from users.permissions import check_user_role
from users.ruleset import RuleSetEnum

METHOD_PERMISSION_MAP = {
    'GET': 'view',
    'HEAD': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete',
}


class JSReportPermission(BasePermission):
    """Controlled by the 'Report -> Reports' ruleset. Superusers have full access."""

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or request.method == 'OPTIONS':
            return True

        permission = METHOD_PERMISSION_MAP.get(request.method)
        if permission is None:
            return False

        return check_user_role(user, RuleSetEnum.REPORT, permission)

        # --- old code ---
        # if request.method in ['GET', 'HEAD', 'OPTIONS']:
        #     return True
        #
        # return request.user.is_superuser