# project_warranties/serializers.py
from rest_framework import serializers
from .models import ExternalProjectDetails, ProjectWarrantyView, ExternalProjectRequest, ExternalProjectsDetails

class ExternalProjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectRequest
        fields = '__all__'

class ExternalProjectDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectDetails
        fields = '__all__'

class ProjectWarrantyViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectWarrantyView
        fields = '__all__'

class ExternalProjectsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectsDetails
        fields = '__all__'