# project_request/serializers.py
from rest_framework import serializers
from .models import InternalProjectRequest, ExternalProjectRequest, ManagementApprovals

class ManagementApprovalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementApprovals
        fields = '__all__'

class InternalProjectRequestSerializer(serializers.ModelSerializer):
    approval_details = ManagementApprovalsSerializer(source='approval', read_only=True)
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = InternalProjectRequest
        fields = '__all__'

class ExternalProjectRequestSerializer(serializers.ModelSerializer):
    approval_details = ManagementApprovalsSerializer(source='approval', read_only=True)
    status = serializers.ReadOnlyField()
    
    class Meta:
        model = ExternalProjectRequest
        fields = '__all__'