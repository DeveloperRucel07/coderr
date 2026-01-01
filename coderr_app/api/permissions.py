from rest_framework.permissions import BasePermission, SAFE_METHODS

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
