from rest_framework import permissions

class IsTaskOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(request.user, 'profile'):
            return obj.employee_id == request.user.profile.employee_id
        return False

class IsProjectManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'profile'):
            return request.user.profile.role == 'project_manager'
        return False

class IsInternalUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'profile'):
            return request.user.profile.user_type == 'internal'
        return False

class IsExternalUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'profile'):
            return request.user.profile.user_type == 'external'
        return False