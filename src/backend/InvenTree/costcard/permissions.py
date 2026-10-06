"""Permission classes for the 'cards' app."""

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


def _check_ruleset_permission(request, view):
    """Check the request against the ruleset of the view's model.

    The model is taken from the view queryset, so each model is checked against
    its own ruleset (e.g. costcard_stoneplace -> 'Cost Card -> Stone Places').

    Superusers have all permissions by default.
    Other users are checked against the rulesets.
    """
    user = request.user

    if not user or not user.is_authenticated:
        return False

    # Superuser bypasses ruleset checks
    if user.is_superuser:
        return True

    # OPTIONS only returns metadata
    if request.method == 'OPTIONS':
        return True

    permission = METHOD_PERMISSION_MAP.get(request.method)
    if permission is None:
        return False

    queryset = getattr(view, 'queryset', None)
    if queryset is None and hasattr(view, 'get_queryset'):
        queryset = view.get_queryset()

    # No model found -> can't evaluate the ruleset, so deny
    if queryset is None:
        return False

    return check_user_permission(
        user, queryset.model, permission, enforce_superuser=True
    )


class CardsDataPermission(BasePermission):
    """
    Permission for cards *master-like* reference data (e.g. StonePlace).

    Controlled by the group rulesets (Cost Card -> Stone Places, etc.).
    Superusers have all permissions by default.
    """

    def has_permission(self, request, view):
        return _check_ruleset_permission(request, view)


class CostCardPermission(BasePermission):
    """
    Permission for CostCard and its line records (Diamond/Color Stone/Finish).

    Controlled by the group rulesets (Cost Card -> Cost Cards, Diamond Lines,
    Color Stone Lines, Finish Lines). Superusers have all permissions by default.
    """

    def has_permission(self, request, view):
        return _check_ruleset_permission(request, view)