from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Admin').exists()

class IsManagerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()

class IsStaffUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Staff').exists()