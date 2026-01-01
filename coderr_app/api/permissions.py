from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsAdminOrStaff(BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_staff or request.user.is_superuser)

class IsBusinessUserOrOwnerOrReadOnly(BasePermission):
    
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
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return (obj.customer_user == user or obj.business_user == user)
        if request.method == 'PATCH':
            return obj.business_user == user
        return False
    
