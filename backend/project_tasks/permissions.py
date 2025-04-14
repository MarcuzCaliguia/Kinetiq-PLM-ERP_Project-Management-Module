# permissions.py
from rest_framework import permissions

class IsTaskOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a task to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the task
        # Assuming the employee_id is stored in the user's profile
        if hasattr(request.user, 'profile'):
            return obj.employee_id == request.user.profile.employee_id
        return False

class IsProjectManager(permissions.BasePermission):
    """
    Custom permission to only allow project managers to perform certain actions.
    """
    def has_permission(self, request, view):
        # Check if user has project manager role
        if hasattr(request.user, 'profile'):
            return request.user.profile.role == 'project_manager'
        return False

class IsInternalUser(permissions.BasePermission):
    """
    Custom permission to only allow internal users to access internal tasks.
    """
    def has_permission(self, request, view):
        # Check if user has internal user role
        if hasattr(request.user, 'profile'):
            return request.user.profile.user_type == 'internal'
        return False

class IsExternalUser(permissions.BasePermission):
    """
    Custom permission to only allow external users to access external tasks.
    """
    def has_permission(self, request, view):
        # Check if user has external user role
        if hasattr(request.user, 'profile'):
            return request.user.profile.user_type == 'external'
        return False