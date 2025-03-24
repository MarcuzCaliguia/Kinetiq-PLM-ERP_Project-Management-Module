from rest_framework import serializers
from .models import (
    InternalProjectRequest,
    InternalProjectDetails,
    InternalProjectLabor,
    InternalProjectTaskList
)

class InternalProjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectRequest
        fields = '__all__'

class InternalProjectDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectDetails
        fields = '__all__'

class InternalProjectLaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectLabor
        fields = '__all__'

class InternalProjectTaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectTaskList
        fields = '__all__'