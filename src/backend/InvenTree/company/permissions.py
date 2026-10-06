"""Permission helpers for the 'company' API (Customers / Vendors split)."""

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


def _truthy(value) -> bool:
    """Convert a request value to bool."""
    return str(value).lower() in ('true', '1', 'yes', 'on')


def _roles(user, permission: str) -> tuple[bool, bool]:
    """Return (can_customer, can_vendor) for the permission type.

    Applies to all users, including superusers.
    """
    return (
        check_user_role(
            user, RuleSetEnum.CUSTOMER, permission, enforce_superuser=True
        ),
        check_user_role(user, RuleSetEnum.VENDOR, permission, enforce_superuser=True),
    )


def filter_company_queryset(user, queryset):
    """Limit the Company queryset to the types the user may view."""
    if not user or not user.is_authenticated:
        return queryset.none()

    can_customer, can_vendor = _roles(user, 'view')

    if can_customer and can_vendor:
        return queryset
    if can_customer:
        return queryset.filter(is_customer=True)
    if can_vendor:
        return queryset.filter(is_supplier=True)

    return queryset.none()


class CompanyPermission(BasePermission):
    """Customers / Vendors permission for Company endpoints.

    Controlled by the Customer / Vendor rulesets. Applies to all users,
    including superusers.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method == 'OPTIONS':
            return True

        permission = METHOD_PERMISSION_MAP.get(request.method)
        if permission is None:
            return False

        can_customer, can_vendor = _roles(user, permission)

        if request.method == 'POST':
            if _truthy(request.data.get('is_customer', False)) and not can_customer:
                return False
            if _truthy(request.data.get('is_supplier', False)) and not can_vendor:
                return False

        return can_customer or can_vendor

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method == 'OPTIONS':
            return True

        permission = METHOD_PERMISSION_MAP.get(request.method)
        if permission is None:
            return False

        can_customer, can_vendor = _roles(user, permission)

        if obj.is_customer and not can_customer:
            return False
        if obj.is_supplier and not can_vendor:
            return False

        return can_customer or can_vendor