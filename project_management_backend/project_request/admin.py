from django.contrib import admin
from .models import (
    InternalProjectRequest,
    InternalProjectDetails,
    InternalProjectLabor,
    InternalProjectTaskList
)

@admin.register(InternalProjectRequest)
class InternalProjectRequestAdmin(admin.ModelAdmin):
    list_display = ('project_request_id',)
    search_fields = ('project_request_id',)

@admin.register(InternalProjectDetails)
class InternalProjectDetailsAdmin(admin.ModelAdmin):
    list_display = ('intrnl_project_id', 'project_request_id', 'intrnl_project_status')
    list_filter = ('intrnl_project_status',)
    search_fields = ('intrnl_project_id', 'project_request_id__project_request_id')

@admin.register(InternalProjectLabor)
class InternalProjectLaborAdmin(admin.ModelAdmin):
    list_display = ('intrnl_project_labor_id',)
    search_fields = ('intrnl_project_labor_id',)

@admin.register(InternalProjectTaskList)
class InternalProjectTaskListAdmin(admin.ModelAdmin):
    list_display = ('intrnl_task_id', 'intrnl_project_id', 'intrnl_task_status', 'intrnl_task_deadline')
    list_filter = ('intrnl_task_status', 'intrnl_task_deadline')
    search_fields = ('intrnl_task_id', 'intrnl_task_description')
    date_hierarchy = 'intrnl_task_deadline'