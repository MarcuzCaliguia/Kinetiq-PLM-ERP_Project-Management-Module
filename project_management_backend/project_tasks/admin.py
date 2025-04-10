from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django import forms
import uuid

from .models import (
    InternalProjectTaskList, ExternalProjectTaskList,
    InternalProjectDetails, ExternalProjectDetails,
    InternalProjectLabor, ExternalProjectLabor,
    get_valid_internal_project_ids, get_valid_external_project_ids,
    get_valid_internal_labor_ids, get_valid_external_labor_ids
)

class TaskStatusFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return (
            ('completed', 'Completed'),
            ('at_risk', 'At Risk'),
            ('ongoing', 'Ongoing'),
        )
    
    def queryset(self, request, queryset):
        if hasattr(queryset.model, 'intrnl_task_status'):
            status_field = 'intrnl_task_status'
        else:
            status_field = 'task_status'
            
        if self.value() == 'completed':
            return queryset.filter(**{f'{status_field}__icontains': 'completed'})
        if self.value() == 'at_risk':
            return queryset.filter(**{f'{status_field}__icontains': 'at risk'})
        if self.value() == 'ongoing':
            return queryset.filter(**{f'{status_field}__icontains': 'ongoing'})

# In admin.py, update the form classes
class InternalTaskForm(forms.ModelForm):
    class Meta:
        model = InternalProjectTaskList
        fields = ['intrnl_project', 'intrnl_task_description', 'intrnl_task_status', 'intrnl_task_deadline', 'intrnl_project_labor']
        exclude = ['intrnl_task_id']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['intrnl_task_status'].widget = forms.Select(choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled')
        ])

class ExternalTaskForm(forms.ModelForm):
    class Meta:
        model = ExternalProjectTaskList
        fields = ['project', 'task_description', 'task_status', 'task_deadline', 'project_labor']
        exclude = ['task_id']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_status'].widget = forms.Select(choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled')
        ])

# Also update the TaskStatusFilter class
class TaskStatusFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return (
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled')
        )
    
    def queryset(self, request, queryset):
        if hasattr(queryset.model, 'intrnl_task_status'):
            status_field = 'intrnl_task_status'
        else:
            status_field = 'task_status'
            
        if self.value() == 'pending':
            return queryset.filter(**{f'{status_field}': 'pending'})
        if self.value() == 'in_progress':
            return queryset.filter(**{f'{status_field}': 'in_progress'})
        if self.value() == 'completed':
            return queryset.filter(**{f'{status_field}': 'completed'})
        if self.value() == 'canceled':
            return queryset.filter(**{f'{status_field}': 'canceled'})

@admin.register(InternalProjectTaskList)
class InternalTaskAdmin(admin.ModelAdmin):
    form = InternalTaskForm
    list_display = ('intrnl_task_id', 'get_status_badge', 'get_project_id', 'intrnl_task_deadline', 'intrnl_task_description')
    list_filter = (TaskStatusFilter, 'intrnl_project', 'intrnl_task_deadline')
    search_fields = ('intrnl_task_id', 'intrnl_task_description')
    readonly_fields = ('intrnl_task_id',)
    actions = None  # Disable actions dropdown
    
    def get_status_badge(self, obj):
        status = str(obj.intrnl_task_status).lower()
        if 'completed' in status:
            color = '#00bcd4'  # Cyan
            text = 'Completed'
        elif 'at risk' in status:
            color = '#f44336'  # Red
            text = 'At Risk'
        elif 'ongoing' in status:
            color = '#ff9800'  # Orange
            text = 'Ongoing'
        else:
            color = '#9e9e9e'  # Grey
            text = status.title()
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px;">{}</span>',
            color, text
        )
    get_status_badge.short_description = 'Status'
    
    def get_project_id(self, obj):
        if obj.intrnl_project:
            return obj.intrnl_project.intrnl_project_id
        return "N/A"
    get_project_id.short_description = 'Project ID'
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def get_fieldsets(self, request, obj=None):
        if obj is None:  # Adding a new task
            return (
                (None, {
                    'fields': ('intrnl_project', 'intrnl_task_description', 'intrnl_task_status', 'intrnl_task_deadline', 'intrnl_project_labor')
                }),
            )
        else:  # Editing an existing task
            return (
                (None, {
                    'fields': ('intrnl_task_id', 'intrnl_project', 'intrnl_task_description', 'intrnl_task_status', 'intrnl_task_deadline', 'intrnl_project_labor')
                }),
            )

@admin.register(ExternalProjectTaskList)
class ExternalTaskAdmin(admin.ModelAdmin):
    form = ExternalTaskForm
    list_display = ('task_id', 'get_status_badge', 'get_project_id', 'task_deadline', 'task_description')
    list_filter = (TaskStatusFilter, 'project', 'task_deadline')
    search_fields = ('task_id', 'task_description')
    readonly_fields = ('task_id',)
    actions = None  # Disable actions dropdown
    
    def get_status_badge(self, obj):
        status = str(obj.task_status).lower()
        if 'completed' in status:
            color = '#00bcd4'  # Cyan
            text = 'Completed'
        elif 'at risk' in status:
            color = '#f44336'  # Red
            text = 'At Risk'
        elif 'ongoing' in status:
            color = '#ff9800'  # Orange
            text = 'Ongoing'
        else:
            color = '#9e9e9e'  # Grey
            text = status.title()
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px;">{}</span>',
            color, text
        )
    get_status_badge.short_description = 'Status'
    
    def get_project_id(self, obj):
        if obj.project:
            return obj.project.project_id
        return "N/A"
    get_project_id.short_description = 'Project ID'
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def get_fieldsets(self, request, obj=None):
        if obj is None:  # Adding a new task
            return (
                (None, {
                    'fields': ('project', 'task_description', 'task_status', 'task_deadline', 'project_labor')
                }),
            )
        else:  # Editing an existing task
            return (
                (None, {
                    'fields': ('task_id', 'project', 'task_description', 'task_status', 'task_deadline', 'project_labor')
                }),
            )

# Removed the registration of additional models
# admin.site.register(InternalProjectDetails)
# admin.site.register(ExternalProjectDetails)
# admin.site.register(InternalProjectLabor)
# admin.site.register(ExternalProjectLabor)