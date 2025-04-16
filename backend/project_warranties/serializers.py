from rest_framework import serializers
from .models import ExternalProjectWarranty

class ExternalProjectWarrantySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProjectWarranty
        fields = ['project_warranty_id', 'project_id', 'warranty_coverage_yr', 
                  'warranty_start_date', 'warranty_end_date']
        read_only_fields = ['project_warranty_id']  