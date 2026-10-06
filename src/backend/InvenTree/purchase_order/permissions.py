"""Permission helpers for the 'purchase_order' API (Requests / Orders split)."""

from rest_framework.permissions import BasePermission

from users.permissions import check_user_permission, check_user_role
from users.ruleset import RuleSetEnum

from .models import PurchaseOrder

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

    if user.is_superuser:
        return queryset

    # Header and lines use different rulesets
    request_role, order_role = (
        (RuleSetEnum.JS_PURCHASE_REQUEST_LINE, RuleSetEnum.JS_PURCHASE_ORDER_LINE)
        if prefix
        else (RuleSetEnum.JS_PURCHASE_REQUEST, RuleSetEnum.JS_PURCHASE_ORDER)
    )

    can_request = check_user_role(user, request_role, 'view')
    can_order = check_user_role(user, order_role, 'view')

    if can_request and can_order:
        return queryset
    if can_request:
        return queryset.filter(**{f'{prefix}potype': 'REQUEST'})
    if can_order:
        return queryset.filter(**{f'{prefix}potype': 'ORDER'})

    return queryset.none()


class _PotypePermission(BasePermission):
    """Base class: checks the Request / Order ruleset based on potype."""

    request_role = None
    order_role = None

    def potype_from_data(self, request):
        raise NotImplementedError

    def potype_from_obj(self, obj):
        raise NotImplementedError

    def _roles(self, user, permission):
        return (
            check_user_role(user, self.request_role, permission),
            check_user_role(user, self.order_role, permission),
        )

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or request.method == 'OPTIONS':
            return True

        permission = METHOD_PERMISSION_MAP.get(request.method)
        if permission is None:
            return False

        can_request, can_order = self._roles(user, permission)

        if request.method == 'POST':
            potype = self.potype_from_data(request)
            if potype == 'REQUEST':
                return can_request
            if potype == 'ORDER':
                return can_order

        return can_request or can_order

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or request.method == 'OPTIONS':
            return True

        permission = METHOD_PERMISSION_MAP.get(request.method)
        if permission is None:
            return False

        can_request, can_order = self._roles(user, permission)

        if self.potype_from_obj(obj) == 'REQUEST':
            return can_request

        return can_order


class PurchaseOrderPermission(_PotypePermission):
    """Purchase -> Request / Order rulesets (PurchaseOrder header)."""

    request_role = RuleSetEnum.JS_PURCHASE_REQUEST
    order_role = RuleSetEnum.JS_PURCHASE_ORDER

    def potype_from_data(self, request):
        return str(request.data.get('potype', 'ORDER')).upper()

    def potype_from_obj(self, obj):
        return obj.potype


class PurchaseOrderLinePermission(_PotypePermission):
    """Purchase -> Request Lines / Order Lines rulesets (PurchaseOrderLine)."""

    request_role = RuleSetEnum.JS_PURCHASE_REQUEST_LINE
    order_role = RuleSetEnum.JS_PURCHASE_ORDER_LINE

    def potype_from_data(self, request):
        poid = request.data.get('poid')
        if not poid:
            return None
        return (
            PurchaseOrder.objects.filter(pk=poid).values_list('potype', flat=True).first()
        )

    def potype_from_obj(self, obj):
        return obj.poid.potype


class POCostCardPermission(BasePermission):
    """Purchase -> Cost Card / Cost Card Lines rulesets (taken from the model)."""

    def has_permission(self, request, view):
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

        if queryset is None:
            return user.is_superuser

        return check_user_permission(user, queryset.model, permission)