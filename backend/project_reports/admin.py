from django.contrib import admin

from django.contrib import admin
from .models import ReportMonitoring, ExternalProject, InternalProject

@admin.register(ReportMonitoring)
class ReportMonitoringAdmin(admin.ModelAdmin):
    list_display = ('report_monitoring_id', 'project_id', 'intrnl_project_id', 'report_type', 
                   'report_title', 'received_from', 'date_created', 'assigned_to')
    list_filter = ('report_type', 'date_created', 'received_from', 'assigned_to')
    search_fields = ('report_monitoring_id', 'report_title', 'description', 'project_id', 'intrnl_project_id')
    ordering = ('-date_created',)

@admin.register(ExternalProject)
class ExternalProjectAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'ext_project_request_id', 'project_status')
    list_filter = ('project_status',)
    search_fields = ('project_id', 'ext_project_request_id')

@admin.register(InternalProject)
class InternalProjectAdmin(admin.ModelAdmin):
    list_display = ('intrnl_project_id', 'project_request_id', 'intrnl_project_status', 'approval_id')
    list_filter = ('intrnl_project_status',)
    search_fields = ('intrnl_project_id', 'project_request_id', 'approval_id')