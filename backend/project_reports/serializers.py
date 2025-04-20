from rest_framework import serializers
from .models import ReportMonitoring, ExternalProject, InternalProject, Equipment, Employees, Positions

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

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['equipment_id', 'equipment_name', 'description', 'availability_status', 'last_maintenance_date', 'equipment_cost']

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Positions
        fields = ['position_id', 'position_title']

class EmployeeSerializer(serializers.ModelSerializer):
    position_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Employees
        fields = ['employee_id', 'position', 'first_name', 'last_name', 'position_title']
    
    def get_position_title(self, obj):
        if obj.position:
            return obj.position.position_title
        return None