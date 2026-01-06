from rest_framework.permissions import BasePermission,  SAFE_METHODS



class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.

    Allows read-only access to everyone, but write access only to the owner.
    For DELETE requests, checks if the user is authenticated.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to perform the action on the object.

        Args:
            request: The HTTP request.
            view: The view that is being accessed.
            obj: The object being accessed.

        Returns:
            bool: True if permission is granted, False otherwise.
        """
        if request.method in SAFE_METHODS:
            return True
        if request.method == "DELETE":
            return bool(request.user)
        else:
            return obj.user == request.user
