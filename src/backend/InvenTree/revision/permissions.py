from rest_framework.permissions import BasePermission


class MasterDataPermission(BasePermission):
    """
    Superusers can view and modify master data.
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