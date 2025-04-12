from rest_framework import serializers
from .models import InternalProjectTask, ExternalProjectTask

class InternalProjectTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectTask
        fields = '__all__'

class ExternalProjectTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectTask
        fields = '__all__'