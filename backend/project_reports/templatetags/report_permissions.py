from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter
def can_edit_report(user, report):
    """Check if user can edit a specific report"""
    # Superusers can edit anything
    if user.is_superuser:
        return True
    
    # Check if user has general edit permission
    if user.has_perm('project_reports.change_reportmonitoring'):
        return True
    
    # Check if user is in the assigned department
    user_department = getattr(user, 'department', None)
    if user_department and report.assigned_to == user_department:
        return True
    
    return False

@register.filter
def can_delete_report(user, report):
    """Check if user can delete a specific report"""
    # Only superusers and users with explicit delete permission can delete
    return user.is_superuser or user.has_perm('project_reports.delete_reportmonitoring')