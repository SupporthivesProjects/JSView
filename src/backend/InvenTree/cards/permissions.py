"""Permission classes for the 'cards' app."""

from rest_framework.permissions import BasePermission


class CardsDataPermission(BasePermission):
    """
    Permission for cards *master-like* reference data (e.g. StonePlace).

    Superusers can view and modify.
    Staff and normal authenticated users can only view.
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # GET / HEAD / OPTIONS -> all authenticated users can view
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # POST / PUT / PATCH / DELETE -> only superuser
        return request.user.is_superuser


class CostCardPermission(BasePermission):
    """
    Permission for CostCard and its line records (Diamond/Color Stone/Finish).

    Unlike master data, cost cards are day-to-day working records, so any
    authenticated user may view and create/update them. Deleting a cost
    card (or one of its lines) is restricted to staff/superusers to avoid
    accidental loss of costing history.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method == 'DELETE':
            return request.user.is_staff or request.user.is_superuser

        return True