from rest_framework import serializers
from .models import ReportMonitoring, ExternalProject, InternalProject

class ReportMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportMonitoring
        fields = [
            'report_monitoring_id', 'project_id', 'intrnl_project_id', 
            'report_type', 'report_title', 'received_from', 
            'date_created', 'assigned_to', 'description'
        ]

class ExternalProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProject
        fields = ['project_id', 'ext_project_request_id', 'project_status']

class InternalProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProject
        fields = ['intrnl_project_id', 'project_request_id', 'intrnl_project_status', 'approval_id']