from rest_framework import serializers
from .models import ProjectCosts, ExternalProjectDetails, InternalProjectDetails

class ProjectCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCosts
        fields = '__all__'

class ExternalProjectDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectDetails
        fields = ['project_id', 'project_status', 'start_date', 'estimated_end_date']

class InternalProjectDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectDetails
        fields = ['intrnl_project_id', 'intrnl_project_status', 'start_date', 'estimated_end_date']

class ProjectCostDetailSerializer(serializers.ModelSerializer):
    external_project = serializers.SerializerMethodField()
    internal_project = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectCosts
        fields = '__all__'
    
    def get_external_project(self, obj):
        if obj.project_id:
            try:
                project = ExternalProjectDetails.objects.get(project_id=obj.project_id)
                return ExternalProjectDetailsSerializer(project).data
            except ExternalProjectDetails.DoesNotExist:
                return None
        return None
    
    def get_internal_project(self, obj):
        if obj.intrnl_project_id:
            try:
                project = InternalProjectDetails.objects.get(intrnl_project_id=obj.intrnl_project_id)
                return InternalProjectDetailsSerializer(project).data
            except InternalProjectDetails.DoesNotExist:
                return None
        return None