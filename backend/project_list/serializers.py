from rest_framework import serializers
from .models import (
    ExternalProjectRequest, ExternalProjectDetails, ProjectLabor,
    ExternalProjectEquipments, InternalProjectRequest,
    InternalProjectDetails, ProjectCosts, ProjectTasks
)

class ExternalProjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectRequest
        fields = '__all__'

class ExternalProjectDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectDetails
        fields = '__all__'

class ProjectLaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectLabor
        fields = '__all__'

class ExternalProjectEquipmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectEquipments
        fields = '__all__'

class ProjectCostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCosts
        fields = '__all__'

class ProjectTasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTasks
        fields = '__all__'

class InternalProjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectRequest
        fields = '__all__'
    
    def to_representation(self, instance):
        """Ensure dept_id is included in the serialized data"""
        data = super().to_representation(instance)
        # Explicitly include dept_id
        data['dept_id'] = str(instance.dept_id) if instance.dept_id else 'N/A'
        return data

class InternalProjectDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectDetails
        fields = '__all__'

class ExternalProjectDetailedSerializer(serializers.ModelSerializer):
    ext_project_request = ExternalProjectRequestSerializer(source='ext_project_request_id', read_only=True)
    
    class Meta:
        model = ExternalProjectDetails
        fields = [
            'project_id', 'project_status', 'project_milestone', 
            'start_date', 'estimated_end_date', 'warranty_coverage_yr',
            'warranty_start_date', 'warranty_end_date', 'project_issues',
            'warranty_status', 'ext_project_request'
        ]

class InternalProjectDetailedSerializer(serializers.ModelSerializer):
    project_request = InternalProjectRequestSerializer(source='project_request_id', read_only=True)
    
    class Meta:
        model = InternalProjectDetails
        fields = [
            'intrnl_project_id', 'intrnl_project_status', 'approval_id', 
            'start_date', 'estimated_end_date', 'project_issues', 'project_request'
        ]