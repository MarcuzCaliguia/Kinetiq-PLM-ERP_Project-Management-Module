from rest_framework import serializers
from .models import (
    ExternalProjectRequest, ExternalProjectDetails, ExternalProjectLabor,
    ExternalProjectEquipments, ExternalProjectWarranty,
    InternalProjectRequest, InternalProjectDetails, InternalProjectLabor
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

class InternalProjectDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectDetails
        fields = '__all__'

class InternalProjectLaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectLabor
        fields = '__all__'