"""Permission helpers for the 'purchase_order' API (Requests / Orders split)."""

from rest_framework.permissions import BasePermission

from users.permissions import check_user_permission, check_user_role
from users.ruleset import RuleSetEnum

from .models import PurchaseOrder


# HTTP method -> ruleset permission
METHOD_PERMISSION_MAP = {
    'GET': 'view',
    'HEAD': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete',
}


def filter_po_queryset(user, queryset, prefix=''):
    """Limit a queryset to the potype(s) the user may view.

    Use prefix='poid__' for PurchaseOrderLine querysets.
    """
    if not user or not user.is_authenticated:
        return queryset.none()

    # Header and lines use different rulesets.
    request_role, order_role = (
        (
            RuleSetEnum.JS_PURCHASE_REQUEST_LINE,
            RuleSetEnum.JS_PURCHASE_ORDER_LINE,
        )
        if prefix
        else (
            RuleSetEnum.JS_PURCHASE_REQUEST,
            RuleSetEnum.JS_PURCHASE_ORDER,
        )
    )

    can_request = check_user_role(
        user,
        request_role,
        'view',
        enforce_superuser=True,
    )

    can_order = check_user_role(
        user,
        order_role,
        'view',
        enforce_superuser=True,
    )

    if can_request and can_order:
        return queryset

    if can_request:
        return queryset.filter(
            **{f'{prefix}potype': 'REQUEST'}
        )

    if can_order:
        return queryset.filter(
            **{f'{prefix}potype': 'ORDER'}
        )

    return queryset.none()


class _PotypePermission(BasePermission):
    """
    Base permission for Purchase Request / Purchase Order.

    Permission is determined by the potype-specific ruleset.
    Applies to all users, including superusers.
    """

    request_role = None
    order_role = None

    def potype_from_data(self, request):
        raise NotImplementedError

    def potype_from_obj(self, obj):
        raise NotImplementedError

    def _roles(self, user, permission):
        return (
            check_user_role(
                user,
                self.request_role,
                permission,
                enforce_superuser=True,
            ),
            check_user_role(
                user,
                self.order_role,
                permission,
                enforce_superuser=True,
            ),
        )

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

        can_request, can_order = self._roles(
            user,
            permission,
        )

        # CREATE must be checked against the requested potype.
        if request.method == 'POST':
            potype = self.potype_from_data(request)

            if potype == 'REQUEST':
                return can_request

            if potype == 'ORDER':
                return can_order

            # Unknown/missing potype -> deny.
            return False

        return can_request or can_order

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # OPTIONS only returns API metadata.
        if request.method == 'OPTIONS':
            return True

        permission = METHOD_PERMISSION_MAP.get(request.method)

        if permission is None:
            return False

        can_request, can_order = self._roles(
            user,
            permission,
        )

        if self.potype_from_obj(obj) == 'REQUEST':
            return can_request

        if self.potype_from_obj(obj) == 'ORDER':
            return can_order

        return False


class PurchaseOrderPermission(_PotypePermission):
    """
    Purchase -> Request / Order rulesets.

    Used for PurchaseOrder header records.
    """

    request_role = RuleSetEnum.JS_PURCHASE_REQUEST
    order_role = RuleSetEnum.JS_PURCHASE_ORDER

    def potype_from_data(self, request):
        return str(
            request.data.get('potype', 'ORDER')
        ).upper()

    def potype_from_obj(self, obj):
        return obj.potype


class PurchaseOrderLinePermission(_PotypePermission):
    """
    Purchase -> Request Lines / Order Lines rulesets.

    Used for PurchaseOrderLine records.
    """

    request_role = RuleSetEnum.JS_PURCHASE_REQUEST_LINE
    order_role = RuleSetEnum.JS_PURCHASE_ORDER_LINE

    def potype_from_data(self, request):
        poid = request.data.get('poid')

        if not poid:
            return None

        return (
            PurchaseOrder.objects
            .filter(pk=poid)
            .values_list('potype', flat=True)
            .first()
        )

    def potype_from_obj(self, obj):
        return obj.poid.potype


class POCostCardPermission(BasePermission):
    """
    Purchase -> Cost Card / Cost Card Lines rulesets.

    The ruleset is determined from the model used by the view queryset.
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

        queryset = getattr(view, 'queryset', None)

        if queryset is None and hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()

        # No model found -> cannot evaluate the ruleset.
        if queryset is None:
            return False

        return check_user_permission(
            user,
            queryset.model,
            permission,
            enforce_superuser=True,
        )