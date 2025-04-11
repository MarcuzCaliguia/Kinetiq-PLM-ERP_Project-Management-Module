from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ReportMonitoring, ExternalProject, InternalProject

# Serializers
class ExternalProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalProject
        fields = ['project_id', 'ext_project_request_id', 'project_status']

class InternalProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProject
        fields = ['intrnl_project_id', 'project_request_id', 'intrnl_project_status', 'approval_id']

class ReportMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportMonitoring
        fields = [
            'report_monitoring_id', 'project_id', 'intrnl_project_id', 
            'report_type', 'report_title', 'received_from', 
            'date_created', 'assigned_to', 'description'
        ]
        read_only_fields = ['report_monitoring_id']
    
    def validate(self, data):
        project_id = data.get('project_id')
        intrnl_project_id = data.get('intrnl_project_id')
        
        # Check that at least one project ID is provided
        if not project_id and not intrnl_project_id:
            raise serializers.ValidationError("Either project_id or intrnl_project_id must be provided.")
        
        # Check that both aren't provided at the same time
        if project_id and intrnl_project_id:
            raise serializers.ValidationError("Only one of project_id or intrnl_project_id should be provided, not both.")
        
        return data
    
    def create(self, validated_data):
        # Use the custom create_report method
        report_id = ReportMonitoring.create_report(
            project_id=validated_data.get('project_id'),
            intrnl_project_id=validated_data.get('intrnl_project_id'),
            report_type=validated_data['report_type'],
            report_title=validated_data['report_title'],
            received_from=validated_data['received_from'],
            date_created=validated_data['date_created'],
            assigned_to=validated_data['assigned_to'],
            description=validated_data.get('description', '')
        )
        
        # Return the newly created instance
        return ReportMonitoring.objects.get(report_monitoring_id=report_id)

# ViewSets
class ReportMonitoringViewSet(viewsets.ModelViewSet):
    queryset = ReportMonitoring.objects.all().order_by('-date_created')
    serializer_class = ReportMonitoringSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters from query parameters
        search = self.request.query_params.get('search', None)
        report_type = self.request.query_params.get('report_type', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        project_type = self.request.query_params.get('project_type', None)
        
        if search:
            queryset = queryset.filter(
                Q(report_title__icontains=search) |
                Q(report_monitoring_id__icontains=search) |
                Q(description__icontains=search)
            )
        
        if report_type:
            queryset = queryset.filter(report_type=report_type)
            
        if date_from:
            queryset = queryset.filter(date_created__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(date_created__lte=date_to)
            
        if project_type == 'external':
            queryset = queryset.filter(project_id__isnull=False)
        elif project_type == 'internal':
            queryset = queryset.filter(intrnl_project_id__isnull=False)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def report_types(self, request):
        from .forms import ReportMonitoringForm
        return Response(dict(ReportMonitoringForm.REPORT_TYPE_CHOICES))
    
    @action(detail=False, methods=['get'])
    def modules(self, request):
        from .forms import ReportMonitoringForm
        return Response(dict(ReportMonitoringForm.MODULE_CHOICES))

class ExternalProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExternalProject.objects.all()
    serializer_class = ExternalProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

class InternalProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InternalProject.objects.all()
    serializer_class = InternalProjectSerializer
    permission_classes = [permissions.IsAuthenticated]