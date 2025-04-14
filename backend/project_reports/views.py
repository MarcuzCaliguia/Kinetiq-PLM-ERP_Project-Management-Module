from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.db.models import Q
from django.db import connection
from .models import ReportMonitoring, ExternalProject, InternalProject
from .serializers import ReportMonitoringSerializer
from datetime import date
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def project_autocomplete(request):

    search = request.query_params.get('search', '')
    project_type = request.query_params.get('type', 'both')  
    
    try:
        results = []
        
        with connection.cursor() as cursor:
            if project_type in ['external', 'both'] and search:
                cursor.execute("""
                    SELECT 
                        project_id AS id,
                        'external' AS type,
                        project_status AS status
                    FROM 
                        project_management.external_project_details
                    WHERE 
                        project_id ILIKE %s
                    ORDER BY 
                        project_id
                    LIMIT 10
                """, [f'%{search}%'])
                
                columns = [col[0] for col in cursor.description]
                external_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                results.extend(external_results)
            
            if project_type in ['internal', 'both'] and search:
                cursor.execute("""
                    SELECT 
                        intrnl_project_id AS id,
                        'internal' AS type,
                        intrnl_project_status AS status
                    FROM 
                        project_management.internal_project_details
                    WHERE 
                        intrnl_project_id ILIKE %s
                    ORDER BY 
                        intrnl_project_id
                    LIMIT 10
                """, [f'%{search}%'])
                
                columns = [col[0] for col in cursor.description]
                internal_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                results.extend(internal_results)
        
        return Response(results)
    except Exception as e:
        logger.error(f"Error in project_autocomplete: {str(e)}")
        return Response(
            {"error": f"Failed to fetch project suggestions: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
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
            return ReportMonitoring.objects.none()
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in list method: {str(e)}")
            return Response(
                {"error": f"An error occurred while fetching reports: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        try:
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


@api_view(['GET'])
def external_projects(request):
    search = request.query_params.get('search', '')
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    project_id, 
                    ext_project_request_id, 
                    project_status
                FROM 
                    project_management.external_project_details
            """
            
            params = []
            if search:
                query += " WHERE project_id ILIKE %s"
                params.append(f'%{search}%')
            
            query += " ORDER BY project_id LIMIT 100"
            
            cursor.execute(query, params)
            
            columns = [col[0] for col in cursor.description]
            projects = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response(projects)
    except Exception as e:
        logger.error(f"Error fetching external projects: {str(e)}")
        return Response(
            {"error": f"Failed to fetch external projects: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def internal_projects(request):
    search = request.query_params.get('search', '')
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    intrnl_project_id, 
                    project_request_id, 
                    intrnl_project_status
                FROM 
                    project_management.internal_project_details
            """
            
            params = []
            if search:
                query += " WHERE intrnl_project_id ILIKE %s"
                params.append(f'%{search}%')
            
            query += " ORDER BY intrnl_project_id LIMIT 100"
            
            cursor.execute(query, params)
            
            columns = [col[0] for col in cursor.description]
            projects = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response(projects)
    except Exception as e:
        logger.error(f"Error fetching internal projects: {str(e)}")
        return Response(
            {"error": f"Failed to fetch internal projects: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        