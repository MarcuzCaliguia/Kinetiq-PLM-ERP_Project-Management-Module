from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.db.models import Q
from django.db import connection
from .models import ReportMonitoring, ExternalProject, InternalProject, Equipment, Employees, Positions
from .serializers import (
    ReportMonitoringSerializer, ExternalProjectSerializer, 
    InternalProjectSerializer, EquipmentSerializer,
    EmployeeSerializer, PositionSerializer
)
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
        
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        try:
            with connection.cursor() as cursor:
                
                cursor.execute("""
                    SELECT 
                        report_type, 
                        COUNT(*) as count
                    FROM 
                        project_management.report_monitoring
                    GROUP BY 
                        report_type
                    ORDER BY 
                        count DESC
                """)
                
                columns = [col[0] for col in cursor.description]
                by_type = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                
                cursor.execute("""
                    SELECT 
                        TO_CHAR(date_created, 'YYYY-MM') as month, 
                        COUNT(*) as count
                    FROM 
                        project_management.report_monitoring
                    WHERE
                        date_created >= CURRENT_DATE - INTERVAL '1 year'
                    GROUP BY 
                        month
                    ORDER BY 
                        month
                """)
                
                columns = [col[0] for col in cursor.description]
                by_month = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN project_id IS NOT NULL THEN 1 END) as external_project_reports,
                        COUNT(CASE WHEN intrnl_project_id IS NOT NULL THEN 1 END) as internal_project_reports
                    FROM 
                        project_management.report_monitoring
                """)
                
                columns = [col[0] for col in cursor.description]
                totals = dict(zip(columns, cursor.fetchone()))
            
            return Response({
                "by_type": by_type,
                "by_month": by_month,
                "totals": totals
            })
        except Exception as e:
            logger.error(f"Error fetching report statistics: {str(e)}")
            return Response(
                {"error": f"Failed to fetch report statistics: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=False, methods=['get'])
    def project_details(self, request):
        project_id = request.query_params.get('project_id')
        internal_project_id = request.query_params.get('internal_project_id')
        
        try:
            data = {}
            
            if project_id:
                
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            p.project_id, 
                            p.ext_project_request_id, 
                            p.project_status,
                            c.client_name,
                            c.contact_person,
                            c.email,
                            c.phone_number
                        FROM 
                            project_management.external_project_details p
                        LEFT JOIN
                            project_management.clients c ON p.client_id = c.client_id
                        WHERE 
                            p.project_id = %s
                    """, [project_id])
                    
                    columns = [col[0] for col in cursor.description]
                    result = cursor.fetchone()
                    
                    if result:
                        project_data = dict(zip(columns, result))
                        data['project'] = project_data
                        
                        
                        cursor.execute("""
                            SELECT 
                                e.equipment_id,
                                e.equipment_name,
                                e.description,
                                e.availability_status,
                                pe.quantity
                            FROM 
                                project_management.project_equipment pe
                            JOIN
                                project_management.equipment e ON pe.equipment_id = e.equipment_id
                            WHERE 
                                pe.project_id = %s
                            ORDER BY
                                e.equipment_name
                        """, [project_id])
                        
                        columns = [col[0] for col in cursor.description]
                        equipment_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                        data['equipment'] = equipment_results
                        
                        
                        cursor.execute("""
                            SELECT 
                                e.employee_id,
                                e.first_name,
                                e.last_name,
                                p.position_title as job_role
                            FROM 
                                project_management.project_workers pw
                            JOIN
                                project_management.employees e ON pw.employee_id = e.employee_id
                            JOIN
                                project_management.positions p ON e.position = p.position_id
                            WHERE 
                                pw.project_id = %s
                            ORDER BY
                                p.position_title
                        """, [project_id])
                        
                        columns = [col[0] for col in cursor.description]
                        workers_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                        data['workers'] = workers_results
                
            elif internal_project_id:
                
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            p.intrnl_project_id, 
                            p.project_request_id, 
                            p.intrnl_project_status,
                            p.approval_id
                        FROM 
                            project_management.internal_project_details p
                        WHERE 
                            p.intrnl_project_id = %s
                    """, [internal_project_id])
                    
                    columns = [col[0] for col in cursor.description]
                    result = cursor.fetchone()
                    
                    if result:
                        project_data = dict(zip(columns, result))
                        data['project'] = project_data
                        
                        
                        cursor.execute("""
                            SELECT 
                                e.equipment_id,
                                e.equipment_name,
                                e.description,
                                e.availability_status,
                                pe.quantity
                            FROM 
                                project_management.internal_project_equipment pe
                            JOIN
                                project_management.equipment e ON pe.equipment_id = e.equipment_id
                            WHERE 
                                pe.intrnl_project_id = %s
                            ORDER BY
                                e.equipment_name
                        """, [internal_project_id])
                        
                        columns = [col[0] for col in cursor.description]
                        equipment_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                        data['equipment'] = equipment_results
                        
                        
                        cursor.execute("""
                            SELECT 
                                e.employee_id,
                                e.first_name,
                                e.last_name,
                                p.position_title as job_role
                            FROM 
                                project_management.internal_project_workers pw
                            JOIN
                                project_management.employees e ON pw.employee_id = e.employee_id
                            JOIN
                                project_management.positions p ON e.position = p.position_id
                            WHERE 
                                pw.intrnl_project_id = %s
                            ORDER BY
                                p.position_title
                        """, [internal_project_id])
                        
                        columns = [col[0] for col in cursor.description]
                        workers_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                        data['workers'] = workers_results
            
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching project details: {str(e)}")
            return Response(
                {"error": f"Failed to fetch project details: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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

@api_view(['GET'])
def equipment_list(request):
    search = request.query_params.get('search', '')
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    equipment_id, 
                    equipment_name, 
                    description,
                    availability_status
                FROM 
                    production.equipment
                WHERE 1=1
            """
            
            params = []
            if search:
                query += " AND (equipment_name ILIKE %s OR description ILIKE %s)"
                params.extend([f'%{search}%', f'%{search}%'])
            
            query += " ORDER BY equipment_name LIMIT 100"
            
            cursor.execute(query, params)
            
            columns = [col[0] for col in cursor.description]
            equipment = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response(equipment)
    except Exception as e:
        logger.error(f"Error fetching equipment: {str(e)}")
        return Response(
            {"error": f"Failed to fetch equipment: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def employees_list(request):
    search = request.query_params.get('search', '')
    position = request.query_params.get('position', '')
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    e.employee_id, 
                    e.first_name, 
                    e.last_name,
                    p.position_id,
                    p.position_title
                FROM 
                    human_resources.employees e
                JOIN
                    human_resources.positions p ON e.position_id = p.position_id
                WHERE 1=1
            """
            
            params = []
            if search:
                query += " AND (e.first_name ILIKE %s OR e.last_name ILIKE %s OR e.employee_id ILIKE %s)"
                params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
            
            if position:
                query += " AND p.position_id = %s"
                params.append(position)
            
            query += " ORDER BY e.last_name, e.first_name LIMIT 100"
            
            cursor.execute(query, params)
            
            columns = [col[0] for col in cursor.description]
            employees = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response(employees)
    except Exception as e:
        logger.error(f"Error fetching employees: {str(e)}")
        return Response(
            {"error": f"Failed to fetch employees: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def positions_list(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    position_id, 
                    position_title
                FROM 
                    human_resources.positions
                ORDER BY 
                    position_title
            """)
            
            columns = [col[0] for col in cursor.description]
            positions = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response(positions)
    except Exception as e:
        logger.error(f"Error fetching positions: {str(e)}")
        return Response(
            {"error": f"Failed to fetch positions: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )