from rest_framework.permissions import BasePermission, SAFE_METHODS


    

class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to allow only the creator or an admin to delete or update.
    """

    def has_object_permission(self, request, view, obj):
        # Allow if the user is the creator or an admin
        return obj.creator == request.user or request.user.is_staff