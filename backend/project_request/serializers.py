from rest_framework import serializers
from .models import Department, Employee, InternalProjectRequest

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['dept_id', 'dept_name']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['employee_id', 'first_name', 'last_name']

class InternalProjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProjectRequest
        fields = '__all__'