from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.db import connection
import logging
from .models import ReportMonitoring, ExternalProject, InternalProject
from .serializers import ReportMonitoringSerializer, ExternalProjectSerializer, InternalProjectSerializer

logger = logging.getLogger(__name__)

class ReportMonitoringViewSet(viewsets.ModelViewSet):
    queryset = ReportMonitoring.objects.all().order_by('-date_created')
    serializer_class = ReportMonitoringSerializer
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            
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
        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}")
            # Return empty queryset on error rather than crashing
            return ReportMonitoring.objects.none()
    
    def create(self, request, *args, **kwargs):
        try:
            # Extract data from request
            project_id = request.data.get('project_id')
            intrnl_project_id = request.data.get('intrnl_project_id')
            report_type = request.data.get('report_type')
            report_title = request.data.get('report_title')
            received_from = request.data.get('received_from')
            date_created = request.data.get('date_created')
            assigned_to = request.data.get('assigned_to')
            description = request.data.get('description', '')
            
            report_id = ReportMonitoring.create_report(
                project_id=project_id,
                intrnl_project_id=intrnl_project_id,
                report_type=report_type,
                report_title=report_title,
                received_from=received_from,
                date_created=date_created,
                assigned_to=assigned_to,
                description=description
            )
            
            if report_id:
                # Fetch the newly created report
                report = ReportMonitoring.objects.get(report_monitoring_id=report_id)
                serializer = self.get_serializer(report)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": "Failed to create report. No report ID was returned."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Error in create method: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def report_types(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        unnest(enum_range(NULL::report_type))::text as report_type
                    ORDER BY 
                        report_type
                """)
                report_types = [row[0] for row in cursor.fetchall()]
            
            return Response(report_types)
        except Exception as e:
            logger.error(f"Error fetching report types: {str(e)}")
            fallback_types = [
                'Sales Order',
                'Resource Availability',
                'Bill of Material',
                'Information',
                'Progress Report',
                'Project Details',
                'Inventory Movement',
            ]
            return Response(fallback_types)
    
    @action(detail=False, methods=['get'])
    def departments(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        unnest(enum_range(NULL::ext_modules))::text as module
                    ORDER BY 
                        module
                """)
                modules = [row[0] for row in cursor.fetchall()]
            
            return Response(modules)
        except Exception as e:
            logger.error(f"Error fetching departments: {str(e)}")
            fallback_departments = [
                'Accounting',
                'Admin',
                'Distribution',
                'Finance',
                'Human Resources',
                'Inventory',
                'Management',
                'MRP',
                'Operations',
                'Production',
                'Project Management',
                'Purchasing',
                'Sales',
                'Services',
                'Solution Customizing',
                'Department - IT Team',
                'Department - Project Management',
            ]
            return Response(fallback_departments)


class ExternalProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExternalProject.objects.all().order_by('project_id')
    serializer_class = ExternalProjectSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            search = request.query_params.get('search', '')
            
            if search:
                queryset = self.get_queryset().filter(project_id__icontains=search)
            else:
                queryset = self.get_queryset()
                
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in ExternalProjectViewSet.list: {str(e)}")
            return Response(
                {"error": f"Failed to fetch external projects: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InternalProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InternalProject.objects.all().order_by('intrnl_project_id')
    serializer_class = InternalProjectSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            search = request.query_params.get('search', '')
            
            if search:
                queryset = self.get_queryset().filter(intrnl_project_id__icontains=search)
            else:
                queryset = self.get_queryset()
                
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in InternalProjectViewSet.list: {str(e)}")
            return Response(
                {"error": f"Failed to fetch internal projects: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )