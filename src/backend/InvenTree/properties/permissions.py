"""Permission class for Properties Data APIs."""

from rest_framework.permissions import BasePermission

from users.permissions import check_user_permission


# HTTP method -> ruleset permission
METHOD_PERMISSION_MAP = {
    'GET': 'view',
    'HEAD': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete',
}


class PropertiesDataPermission(BasePermission):
    """
    Permission for Properties Data endpoints.

    The ruleset is determined from the model used by the view queryset.
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

        # Get the queryset from the view.
        queryset = getattr(view, 'queryset', None)

        if queryset is None and hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()

        # No model found -> cannot evaluate the ruleset.
        # Deny access for non-superusers.
        if queryset is None:
            return False

        return check_user_permission(
            user,
            queryset.model,
            permission,
            enforce_superuser=True,
        )