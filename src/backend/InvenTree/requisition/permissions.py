"""Permission classes for the 'requisition' app."""

from rest_framework.permissions import BasePermission

from users.permissions import check_user_permission

METHOD_PERMISSION_MAP = {
    'GET': 'view',
    'HEAD': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete',
}


def _check_ruleset_permission(request, view):
    """Check the request against the ruleset of the view's model."""
    user = request.user

    if not user or not user.is_authenticated:
        return False

    if request.method == 'OPTIONS':
        return True

    permission = METHOD_PERMISSION_MAP.get(request.method)
    if permission is None:
        return False

    queryset = getattr(view, 'queryset', None)
    if queryset is None and hasattr(view, 'get_queryset'):
        queryset = view.get_queryset()

    # No model found -> superuser only
    if queryset is None:
        return user.is_superuser

    return check_user_permission(user, queryset.model, permission)


class RequisitionPermission(BasePermission):
    """Controlled by the 'Requisition -> ...' rulesets. Superusers have full access."""

    def has_permission(self, request, view):
        return _check_ruleset_permission(request, view)

        # --- old code ---
        # if not request.user or not request.user.is_authenticated:
        #     return False
        #
        # if request.method in ['GET', 'HEAD', 'OPTIONS']:
        #     return True
        #
        # return request.user.is_superuser


class CostCardPermission(BasePermission):
    """Same ruleset check as RequisitionPermission (kept for existing imports)."""

    def has_permission(self, request, view):
        return _check_ruleset_permission(request, view)

        # --- old code ---
        # if not request.user or not request.user.is_authenticated:
        #     return False
        #
        # if request.method == 'DELETE':
        #     return request.user.is_staff or request.user.is_superuser
        #
        # return True