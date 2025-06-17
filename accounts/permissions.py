from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    '''
    Admin only
    '''
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsStaffUser(BasePermission):
    '''
    Admin or Staff only
    '''
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff
    
class IsUser(BasePermission):
     '''
    User only
    '''
     def has_permission(self, request, view):
         return request.user.is_authenticated