from django.contrib import admin
from .models import InternalProjectTask, ExternalProjectTask

@admin.register(InternalProjectTask)
class InternalProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('intrnl_task_id', 'intrnl_project_id', 'intrnl_task_status', 'intrnl_task_deadline')
    list_filter = ('intrnl_task_status', 'intrnl_task_deadline')
    search_fields = ('intrnl_task_id', 'intrnl_project_id', 'intrnl_task_description')
    readonly_fields = ('intrnl_task_id',)

@admin.register(ExternalProjectTask)
class ExternalProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'project_id', 'task_status', 'task_deadline')
    list_filter = ('task_status', 'task_deadline')
    search_fields = ('task_id', 'project_id', 'task_description')
    readonly_fields = ('task_id',)