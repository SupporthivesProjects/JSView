"""Permission helpers for the 'company' API (Customers / Vendors split)."""

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


def _truthy(value) -> bool:
    """Convert a request value to bool."""
    return str(value).lower() in ('true', '1', 'yes', 'on')


def _roles(user, permission: str) -> tuple[bool, bool]:
    """Return (can_customer, can_vendor) for the permission type.

    Superusers have all permissions by default.
    Other users are checked against the rulesets.
    """
    if user.is_superuser:
        return True, True

    return (
        check_user_role(
            user,
            RuleSetEnum.CUSTOMER,
            permission,
            enforce_superuser=True,
        ),
        check_user_role(
            user,
            RuleSetEnum.VENDOR,
            permission,
            enforce_superuser=True,
        ),
    )


def filter_company_queryset(user, queryset):
    """Limit the Company queryset to the customer/vendor types the user can view."""

    if not user or not user.is_authenticated:
        return queryset.none()

    # Superuser can view everything.
    if user.is_superuser:
        return queryset

    can_customer, can_vendor = _roles(user, 'view')

    # User can view both customers and vendors.
    if can_customer and can_vendor:
        return queryset

    # User can view customers only.
    if can_customer:
        return queryset.filter(is_customer=True)

    # User can view vendors only.
    if can_vendor:
        return queryset.filter(is_supplier=True)

    # User cannot view either.
    return queryset.none()


class CompanyPermission(BasePermission):
    """
    Permission for Company endpoints.

    Superusers have all permissions by default.
    Other users are controlled independently through the
    Customer and Vendor rulesets.
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

        can_customer, can_vendor = _roles(user, permission)

        # For CREATE, determine which type of company is being created.
        if request.method == 'POST':
            is_customer = _truthy(
                request.data.get('is_customer', False)
            )
            is_supplier = _truthy(
                request.data.get('is_supplier', False)
            )

            # Customer company requires Customer -> Add.
            if is_customer and not can_customer:
                return False

            # Vendor company requires Vendor -> Add.
            if is_supplier and not can_vendor:
                return False

            # If neither type is specified, deny creation.
            if not is_customer and not is_supplier:
                return False

            return True

        # For GET/PUT/PATCH/DELETE, at least one applicable
        # Customer/Vendor permission is required.
        return can_customer or can_vendor

    def has_object_permission(self, request, view, obj):
        """Check permission against the actual Company object."""

        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Superuser bypasses ruleset checks.
        if user.is_superuser:
            return True

        if request.method == 'OPTIONS':
            return True

        permission = METHOD_PERMISSION_MAP.get(request.method)

        if permission is None:
            return False

        can_customer, can_vendor = _roles(user, permission)

        # Customer object requires Customer permission.
        if obj.is_customer and not can_customer:
            return False

        # Vendor object requires Vendor permission.
        if obj.is_supplier and not can_vendor:
            return False

        # Object is neither customer nor vendor.
        if not obj.is_customer and not obj.is_supplier:
            return False

        return True