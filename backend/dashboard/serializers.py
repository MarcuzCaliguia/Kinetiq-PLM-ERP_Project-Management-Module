# serializers.py
from rest_framework import serializers
from .models import (
    ExternalProjectDetails, InternalProjectDetails,
    ExternalProjectTracking, InternalProjectTracking,
    ExternalProjectTaskList, InternalProjectTaskList,
    ExternalProjectLabor, InternalProjectLabor,
    ExternalProjectWarranty, ExternalProjectRequest,
    InternalProjectRequest
)
import uuid
from datetime import date

class ExternalProjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectRequest
        fields = '__all__'

class InternalProjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectRequest
        fields = '__all__'

class ExternalProjectWarrantySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectWarranty
        fields = '__all__'
    
    def to_representation(self, instance):
        return {
            'id': instance.project_warranty_id,
            'project_id': instance.project.project_id if instance.project else None,
            'coverage_years': instance.warranty_coverage_yr,
            'start_date': instance.warranty_start_date,
            'end_date': instance.warranty_end_date
        }

class ExternalProjectLaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectLabor
        fields = '__all__'

class InternalProjectLaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectLabor
        fields = '__all__'

class ExternalProjectDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectDetails
        fields = '__all__'

class InternalProjectDetailsSerializer(serializers.ModelSerializer):
    project_request_details = serializers.SerializerMethodField()
    
    class Meta:
        model = InternalProjectDetails
        fields = '__all__'
    
    def get_project_request_details(self, obj):
        if obj.project_request:
            return {
                'request_id': obj.project_request.project_request_id,
                'name': obj.project_request.project_name,
                'description': obj.project_request.project_description
            }
        return None

class ExternalProjectTrackingSerializer(serializers.ModelSerializer):
    project_details = serializers.SerializerMethodField()
    warranty_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ExternalProjectTracking
        fields = '__all__'
    
    def get_project_details(self, obj):
        if obj.project:
            return {
                'id': obj.project.project_id,
                'status': obj.project.project_status
            }
        return None
    
    def get_warranty_details(self, obj):
        if obj.project_warranty:
            return {
                'id': obj.project_warranty.project_warranty_id,
                'coverage_years': obj.project_warranty.warranty_coverage_yr,
                'start_date': obj.project_warranty.warranty_start_date,
                'end_date': obj.project_warranty.warranty_end_date
            }
        return None
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'ProjectTrackingID': instance.project_tracking_id,
            'ProjectID': instance.project.project_id if instance.project else None,
            'ProjectMilestone': instance.project_milestone,
            'StartDate': instance.start_date,
            'EstimatedEndDate': instance.estimated_end_date,
            'ProjectWarrantyStatus': instance.project_warranty.project_warranty_id if instance.project_warranty else None,
            'ProjectIssue': instance.project_issue
        }

class InternalProjectTrackingSerializer(serializers.ModelSerializer):
    project_details = serializers.SerializerMethodField()
    
    class Meta:
        model = InternalProjectTracking
        fields = '__all__'
    
    def get_project_details(self, obj):
        if obj.intrnl_project:
            project = obj.intrnl_project
            request_data = None
            if project.project_request:
                request = project.project_request
                request_data = {
                    'request_id': request.project_request_id,
                    'name': request.project_name,
                    'description': request.project_description
                }
            
            return {
                'id': project.intrnl_project_id,
                'status': project.intrnl_project_status,
                'approval_id': project.approval_id,
                'request': request_data
            }
        return None
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'ProjectTrackingID': instance.intrnl_project_tracking_id,
            'ProjectID': instance.intrnl_project.intrnl_project_id if instance.intrnl_project else None,
            'StartDate': instance.intrnl_start_date,
            'EstimatedEndDate': instance.intrnl_estimated_end_date,
            'ProjectIssue': instance.intrnl_project_issue
        }

class ExternalProjectTaskListSerializer(serializers.ModelSerializer):
    overdue_days = serializers.SerializerMethodField()
    
    class Meta:
        model = ExternalProjectTaskList
        fields = '__all__'
    
    def get_overdue_days(self, obj):
        if obj.task_deadline < date.today():
            delta = date.today() - obj.task_deadline
            return f"{delta.days}days"
        return ""
    
    def to_representation(self, instance):
        return {
            'Overdue': self.get_overdue_days(instance),
            'Task': instance.task_description,
            'Deadline': instance.task_deadline,
            'Employee': instance.project_labor.employee_id if instance.project_labor else 'none'
        }

class InternalProjectTaskListSerializer(serializers.ModelSerializer):
    overdue_days = serializers.SerializerMethodField()
    
    class Meta:
        model = InternalProjectTaskList
        fields = '__all__'
    
    def get_overdue_days(self, obj):
        if obj.intrnl_task_deadline < date.today():
            delta = date.today() - obj.intrnl_task_deadline
            return f"{delta.days}days"
        return ""
    
    def to_representation(self, instance):
        return {
            'Overdue': self.get_overdue_days(instance),
            'Task': instance.intrnl_task_description,
            'Deadline': instance.intrnl_task_deadline,
            'Employee': instance.intrnl_project_labor.employee_id if instance.intrnl_project_labor else 'none'
        }

class CreateExternalProjectSerializer(serializers.Serializer):
    project_id = serializers.CharField(max_length=255)
    project_milestone = serializers.CharField()
    start_date = serializers.DateField()
    estimated_end_date = serializers.DateField()
    project_warranty_id = serializers.CharField(required=False, allow_blank=True)
    project_issue = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        project_id = validated_data.get('project_id')
        warranty_id = validated_data.get('project_warranty_id')
        
        # Check if project exists, if not create it
        project, created = ExternalProjectDetails.objects.get_or_create(
            project_id=project_id,
            defaults={'project_status': 'Active'}
        )
        
        # Create project tracking
        tracking_id = str(uuid.uuid4())[:8]
        
        # Get warranty if provided
        warranty = None
        if warranty_id:
            try:
                warranty = ExternalProjectWarranty.objects.get(project_warranty_id=warranty_id)
            except ExternalProjectWarranty.DoesNotExist:
                pass
        
        ExternalProjectTracking.objects.create(
            project_tracking_id=tracking_id,
            project=project,
            project_milestone=validated_data.get('project_milestone'),
            start_date=validated_data.get('start_date'),
            estimated_end_date=validated_data.get('estimated_end_date'),
            project_warranty=warranty,
            project_issue=validated_data.get('project_issue', '')
        )
        
        return {
            'project_id': project_id,
            'tracking_id': tracking_id
        }

class CreateInternalProjectSerializer(serializers.Serializer):
    project_id = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    estimated_end_date = serializers.DateField()
    project_issue = serializers.CharField(required=False, allow_blank=True)
    project_request_id = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        project_id = validated_data.get('project_id')
        request_id = validated_data.get('project_request_id')
        
        # Get project request if provided
        project_request = None
        if request_id:
            try:
                project_request = InternalProjectRequest.objects.get(project_request_id=request_id)
            except InternalProjectRequest.DoesNotExist:
                pass
        
        # Check if project exists, if not create it
        project, created = InternalProjectDetails.objects.get_or_create(
            intrnl_project_id=project_id,
            defaults={
                'intrnl_project_status': 'Active',
                'project_request': project_request
            }
        )
        
        # Create project tracking
        tracking_id = str(uuid.uuid4())[:8]
        InternalProjectTracking.objects.create(
            intrnl_project_tracking_id=tracking_id,
            intrnl_project=project,
            intrnl_start_date=validated_data.get('start_date'),
            intrnl_estimated_end_date=validated_data.get('estimated_end_date'),
            intrnl_project_issue=validated_data.get('project_issue', '')
        )
        
        return {
            'project_id': project_id,
            'tracking_id': tracking_id
        }