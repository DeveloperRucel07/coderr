from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsAdminOrStaff(BasePermission):
    """
    Custom permission to only allow admin or staff users to access certain views.

    Grants permission for all methods except DELETE, which requires admin or staff status.
    """

    def has_permission(self, request, view):
        return (request.user.is_staff or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return (request.user.is_staff or request.user.is_superuser)
        return True

class IsBusinessUserOrOwnerOrReadOnly(BasePermission):
    """
    Custom permission for offer views, allowing read access to all, but write access only to business users.
    For object-level permissions, only the owner of the offer can modify it.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user.profile, 'type', None) == 'business'

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
    
class IsBusinessUserOrder(BasePermission):
    """
    Custom permission for order-related views, allowing read access to all, but write access only to business users.
    For object-level permissions, only the business user associated with the order can modify it.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user.profile, 'type', None) == 'business'

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        return obj.business_user == request.user


class IsCustomerReviewer(BasePermission):
    """
    Custom permission for review-related views, allowing read access to all, but write access only to customer users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        return getattr(request.user.profile, 'type', None) == 'customer'
    
class IsReviewOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.reviewer == request.user


class IsBusinessOrCustomerUser(BasePermission):
    """
    Custom permission for order views, allowing read access to customer and business users involved in the order.
    Write access (PATCH) is restricted to the business user, and DELETE requires admin or staff status.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return (obj.customer_user == user or obj.business_user == user)
        if request.method == 'PATCH':
            return obj.business_user == user
        if request.method == 'DELETE':
            return user == user.is_staff or user == user.is_superuser
        return False
    
