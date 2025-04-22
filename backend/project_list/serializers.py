from rest_framework import serializers
from .models import (
    ExternalProjectRequest, ExternalProjectDetails, ExternalProjectLabor,
    ExternalProjectEquipments, ExternalProjectWarranty, InternalProjectRequest,
    InternalProjectDetails
)

class ExternalProjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectRequest
        fields = '__all__'

class ExternalProjectDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectDetails
        fields = '__all__'

class ExternalProjectLaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectLabor
        fields = '__all__'

class ExternalProjectEquipmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectEquipments
        fields = '__all__'

class ExternalProjectWarrantySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectWarranty
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
    warranty = serializers.SerializerMethodField()
    
    class Meta:
        model = ExternalProjectDetails
        fields = ['project_id', 'project_status', 'ext_project_request', 'warranty']
        
    def get_warranty(self, obj):
        # Access the prefetched warranty objects
        warranties = list(obj.externalprojectwarranty_set.all())
        if warranties:
            return ExternalProjectWarrantySerializer(warranties[0]).data
        return None

class InternalProjectDetailedSerializer(serializers.ModelSerializer):
    project_request = InternalProjectRequestSerializer(source='project_request_id', read_only=True)
    
    class Meta:
        model = InternalProjectDetails
        fields = ['intrnl_project_id', 'intrnl_project_status', 'approval_id', 'project_request']