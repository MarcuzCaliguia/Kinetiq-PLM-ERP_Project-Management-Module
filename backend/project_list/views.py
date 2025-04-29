from rest_framework import viewsets, status as drf_status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db import connection, transaction
from django.contrib.auth import get_user_model
from .models import (
    ExternalProjectRequest, ExternalProjectDetails,
    ExternalProjectEquipments, InternalProjectRequest,
    InternalProjectDetails, ProjectCosts, ProjectTasks
)
from .serializers import (
    ExternalProjectRequestSerializer, ExternalProjectDetailsSerializer,
    ExternalProjectEquipmentsSerializer,
    InternalProjectRequestSerializer, InternalProjectDetailsSerializer
)

import datetime 
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Helper function to convert cursor results to dictionaries
def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        {columns[i]: value for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]

# Helper function to check if a column exists in a table
def column_exists(table_name, column_name, schema='project_management'):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = %s 
            AND column_name = %s
        """, [schema, table_name, column_name])
        return cursor.fetchone() is not None

# Helper functions for archiving
def archive_external_request(request_id, user_id=None):
    """Archive an external project request and its related data"""
    with connection.cursor() as cursor:
        # First, check if archive tables exist, create them if not
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_management.archived_external_project_request (
                ext_project_request_id character varying(255) NOT NULL,
                ext_project_name character varying(50),
                ext_project_description text,
                approval_id character varying(255),
                item_id character varying(255),
                archived_date timestamp DEFAULT CURRENT_TIMESTAMP,
                archived_by character varying(255),
                CONSTRAINT archived_external_project_request_pkey PRIMARY KEY (ext_project_request_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_management.archived_external_project_details (
                project_id character varying(255) NOT NULL,
                ext_project_request_id character varying(255),
                project_status character varying(20) NOT NULL,
                project_milestone character varying(20),
                start_date date,
                estimated_end_date date,
                warranty_coverage_yr integer,
                warranty_start_date date,
                warranty_end_date date,
                project_issues text,
                warranty_status character varying(20),
                archived_date timestamp DEFAULT CURRENT_TIMESTAMP,
                archived_by character varying(255),
                CONSTRAINT archived_external_project_details_pkey PRIMARY KEY (project_id)
            )
        """)
        
        # Copy the data to archive tables
        cursor.execute("""
            INSERT INTO project_management.archived_external_project_request
            (ext_project_request_id, ext_project_name, ext_project_description, approval_id, item_id, archived_by)
            SELECT 
                ext_project_request_id, ext_project_name, ext_project_description, approval_id, item_id, %s
            FROM 
                project_management.external_project_request
            WHERE 
                ext_project_request_id = %s
            ON CONFLICT (ext_project_request_id) DO NOTHING
        """, [user_id, request_id])
        
        # Archive related project details
        cursor.execute("""
            INSERT INTO project_management.archived_external_project_details
            (project_id, ext_project_request_id, project_status, project_milestone, start_date, 
             estimated_end_date, warranty_coverage_yr, warranty_start_date, warranty_end_date, 
             project_issues, warranty_status, archived_by)
            SELECT 
                project_id, ext_project_request_id, project_status, project_milestone, start_date, 
                estimated_end_date, warranty_coverage_yr, warranty_start_date, warranty_end_date, 
                project_issues, warranty_status, %s
            FROM 
                project_management.external_project_details
            WHERE 
                ext_project_request_id = %s
            ON CONFLICT (project_id) DO NOTHING
        """, [user_id, request_id])
        
        # Now mark the original records as archived
        try:
            # Add archived column if it doesn't exist
            if not column_exists('external_project_request', 'is_archived'):
                cursor.execute("""
                    ALTER TABLE project_management.external_project_request 
                    ADD COLUMN is_archived BOOLEAN DEFAULT FALSE
                """)
            
            if not column_exists('external_project_details', 'is_archived'):
                cursor.execute("""
                    ALTER TABLE project_management.external_project_details 
                    ADD COLUMN is_archived BOOLEAN DEFAULT FALSE
                """)
            
            # Mark as archived
            cursor.execute("""
                UPDATE project_management.external_project_request
                SET is_archived = TRUE
                WHERE ext_project_request_id = %s
            """, [request_id])
            
            cursor.execute("""
                UPDATE project_management.external_project_details
                SET is_archived = TRUE
                WHERE ext_project_request_id = %s
            """, [request_id])
        except Exception as e:
            logger.error(f"Error adding archive column: {str(e)}")
            # If we can't add the column, we'll just return
            return False
        
    return True

def archive_internal_request(request_id, user_id=None):
    """Archive an internal project request and its related data"""
    with connection.cursor() as cursor:
        # First, check if archive tables exist, create them if not
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_management.archived_internal_project_request (
                project_request_id character varying(255) NOT NULL,
                project_name character varying(50) NOT NULL,
                request_date date NOT NULL,
                employee_id character varying(255),
                dept_id character varying(255),
                reason_for_request text,
                materials_needed text,
                equipments_needed text,
                project_type character varying(20),
                archived_date timestamp DEFAULT CURRENT_TIMESTAMP,
                archived_by character varying(255),
                CONSTRAINT archived_internal_project_request_pkey PRIMARY KEY (project_request_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_management.archived_internal_project_details (
                intrnl_project_id character varying(255) NOT NULL,
                project_request_id character varying(255),
                intrnl_project_status character varying(20) NOT NULL,
                approval_id character varying(255),
                start_date date,
                estimated_end_date date,
                project_issues text,
                archived_date timestamp DEFAULT CURRENT_TIMESTAMP,
                archived_by character varying(255),
                CONSTRAINT archived_internal_project_details_pkey PRIMARY KEY (intrnl_project_id)
            )
        """)
        
        # Copy the data to archive tables
        cursor.execute("""
            INSERT INTO project_management.archived_internal_project_request
            (project_request_id, project_name, request_date, employee_id, dept_id, 
             reason_for_request, materials_needed, equipments_needed, project_type, archived_by)
            SELECT 
                project_request_id, project_name, request_date, employee_id, dept_id, 
                reason_for_request, materials_needed, equipments_needed, project_type, %s
            FROM 
                project_management.internal_project_request
            WHERE 
                project_request_id = %s
            ON CONFLICT (project_request_id) DO NOTHING
        """, [user_id, request_id])
        
        # Archive related project details
        cursor.execute("""
            INSERT INTO project_management.archived_internal_project_details
            (intrnl_project_id, project_request_id, intrnl_project_status, approval_id, 
             start_date, estimated_end_date, project_issues, archived_by)
            SELECT 
                intrnl_project_id, project_request_id, intrnl_project_status, approval_id, 
                start_date, estimated_end_date, project_issues, %s
            FROM 
                project_management.internal_project_details
            WHERE 
                project_request_id = %s
            ON CONFLICT (intrnl_project_id) DO NOTHING
        """, [user_id, request_id])
        
        # Now mark the original records as archived
        try:
            # Add archived column if it doesn't exist
            if not column_exists('internal_project_request', 'is_archived'):
                cursor.execute("""
                    ALTER TABLE project_management.internal_project_request 
                    ADD COLUMN is_archived BOOLEAN DEFAULT FALSE
                """)
            
            if not column_exists('internal_project_details', 'is_archived'):
                cursor.execute("""
                    ALTER TABLE project_management.internal_project_details 
                    ADD COLUMN is_archived BOOLEAN DEFAULT FALSE
                """)
            
            # Mark as archived
            cursor.execute("""
                UPDATE project_management.internal_project_request
                SET is_archived = TRUE
                WHERE project_request_id = %s
            """, [request_id])
            
            cursor.execute("""
                UPDATE project_management.internal_project_details
                SET is_archived = TRUE
                WHERE project_request_id = %s
            """, [request_id])
        except Exception as e:
            logger.error(f"Error adding archive column: {str(e)}")
            # If we can't add the column, we'll just return
            return False
        
    return True

class ExternalProjectRequestViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectRequest.objects.all()
    serializer_class = ExternalProjectRequestSerializer
    pagination_class = StandardResultsSetPagination
    
    def list(self, request, *args, **kwargs):
        """Override list to include specific columns with filtering"""
        try:
            # Get pagination parameters
            page = request.query_params.get('page', 1)
            try:
                page = int(page)
            except ValueError:
                page = 1
            
            page_size = 10
            offset = (page - 1) * page_size
            
            # Get filter parameters
            project_name = request.query_params.get('project_name', '')
            approval_id = request.query_params.get('approval_id', '')
            item_id = request.query_params.get('item_id', '')
            status = request.query_params.get('status', '')
            
            # Build filter conditions
            filter_conditions = []
            filter_params = []
            
            if project_name:
                filter_conditions.append("epr.ext_project_name ILIKE %s")
                filter_params.append(f"%{project_name}%")
            
            if approval_id:
                filter_conditions.append("epr.approval_id ILIKE %s")
                filter_params.append(f"%{approval_id}%")
            
            if item_id:
                filter_conditions.append("epr.item_id ILIKE %s")
                filter_params.append(f"%{item_id}%")
            
            if status:
                filter_conditions.append("epd.project_status ILIKE %s")
                filter_params.append(f"%{status}%")
            
            # Build WHERE clause
            where_clause = ""
            if filter_conditions:
                where_clause = "WHERE " + " AND ".join(filter_conditions)
            else:
                where_clause = "WHERE 1=1"  # Always true condition if no other filters
            
            # Check if is_archived column exists
            has_is_archived = column_exists('external_project_request', 'is_archived')
            
            # Add archive filter only if column exists
            archive_filter = ""
            if has_is_archived:
                archive_filter = "AND (epr.is_archived IS NULL OR epr.is_archived = FALSE)"
            
            # Execute query with pagination and filters
            with connection.cursor() as cursor:
                # Set statement timeout to 10 seconds (10000 milliseconds)
                cursor.execute("SET statement_timeout = 10000")
                
                # Get total count for pagination with filters
                count_query = f"""
                    SELECT COUNT(*) 
                    FROM project_management.external_project_request epr
                    LEFT JOIN project_management.external_project_details epd 
                        ON epr.ext_project_request_id = epd.ext_project_request_id
                    {where_clause} {archive_filter}
                """
                cursor.execute(count_query, filter_params)
                total_count = cursor.fetchone()[0]
                
                # Get paginated data with filters
                data_query = f"""
                    SELECT 
                        epr.ext_project_request_id,
                        epr.ext_project_name AS project_name,
                        epr.approval_id,
                        epr.item_id,
                        epd.start_date,
                        epd.project_status
                    FROM 
                        project_management.external_project_request epr
                    LEFT JOIN 
                        project_management.external_project_details epd 
                        ON epr.ext_project_request_id = epd.ext_project_request_id
                    {where_clause} {archive_filter}
                    ORDER BY epr.ext_project_request_id
                    LIMIT {page_size} OFFSET {offset}
                """
                cursor.execute(data_query, filter_params)
                data = dictfetchall(cursor)
                
                # Reset statement timeout to default
                cursor.execute("RESET statement_timeout")
                
            # Process data to handle None values and dates
            for item in data:
                for key, value in item.items():
                    if value is None:
                        item[key] = 'N/A'
                    elif isinstance(value, datetime.date):
                        item[key] = value.isoformat()
            
            # Create pagination response
            total_pages = (total_count + page_size - 1) // page_size
            response_data = {
                'count': total_count,
                'next': f'/api/project-management/external-requests/?page={page+1}' if page < total_pages else None,
                'previous': f'/api/project-management/external-requests/?page={page-1}' if page > 1 else None,
                'results': data
            }
                
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error in ExternalProjectRequestViewSet.list: {str(e)}")
            return Response(
                {"error": f"Failed to fetch external project requests: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_archive(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=drf_status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id = request.user.id if request.user.is_authenticated else None
            
            success_count = 0
            for request_id in ids:
                if archive_external_request(request_id, user_id):
                    success_count += 1
            
            return Response({
                "message": f"Successfully archived {success_count} of {len(ids)} requests",
                "success_count": success_count,
                "total_count": len(ids)
            })
        except Exception as e:
            logger.error(f"Error in bulk_archive: {str(e)}")
            return Response(
                {"error": f"Failed to archive requests: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExternalProjectDetailsViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectDetails.objects.all()
    serializer_class = ExternalProjectDetailsSerializer
    pagination_class = StandardResultsSetPagination
    
    def list(self, request, *args, **kwargs):
        """Override list to include all columns from external_project_details with filtering"""
        try:
            # Get pagination parameters
            page = request.query_params.get('page', 1)
            try:
                page = int(page)
            except ValueError:
                page = 1
            
            page_size = 10
            offset = (page - 1) * page_size
            
            # Get filter parameters
            project_name = request.query_params.get('project_name', '')
            approval_id = request.query_params.get('approval_id', '')
            status = request.query_params.get('status', '')
            
            # Build filter conditions
            filter_conditions = []
            filter_params = []
            
            if project_name:
                filter_conditions.append("epr.ext_project_name ILIKE %s")
                filter_params.append(f"%{project_name}%")
            
            if approval_id:
                filter_conditions.append("epr.approval_id ILIKE %s")
                filter_params.append(f"%{approval_id}%")
            
            if status:
                filter_conditions.append("epd.project_status ILIKE %s")
                filter_params.append(f"%{status}%")
            
            # Build WHERE clause
            where_clause = ""
            if filter_conditions:
                where_clause = "WHERE " + " AND ".join(filter_conditions)
            else:
                where_clause = "WHERE 1=1"  # Always true condition if no other filters
            
            # Check if is_archived column exists
            has_is_archived = column_exists('external_project_details', 'is_archived')
            
            # Add archive filter only if column exists
            archive_filter = ""
            if has_is_archived:
                archive_filter = "AND (epd.is_archived IS NULL OR epd.is_archived = FALSE)"
            
            # Execute query with pagination and filters
            with connection.cursor() as cursor:
                # Set statement timeout to 10 seconds (10000 milliseconds)
                cursor.execute("SET statement_timeout = 10000")
                
                # Get total count for pagination with filters
                count_query = f"""
                    SELECT COUNT(*) 
                    FROM project_management.external_project_details epd
                    LEFT JOIN project_management.external_project_request epr 
                        ON epd.ext_project_request_id = epr.ext_project_request_id
                    {where_clause} {archive_filter}
                """
                cursor.execute(count_query, filter_params)
                total_count = cursor.fetchone()[0]
                
                # Get paginated data with filters
                data_query = f"""
                    SELECT 
                        epd.project_id,
                        epr.ext_project_name AS project_name,
                        epr.approval_id,
                        epr.item_id,
                        epd.start_date,
                        epd.project_status,
                        epd.project_milestone,
                        epd.estimated_end_date,
                        epd.warranty_coverage_yr,
                        epd.warranty_start_date,
                        epd.warranty_end_date,
                        epd.warranty_status,
                        epd.project_issues
                    FROM 
                        project_management.external_project_details epd
                    LEFT JOIN
                        project_management.external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
                    {where_clause} {archive_filter}
                    ORDER BY
                        epd.project_id
                    LIMIT {page_size} OFFSET {offset}
                """
                cursor.execute(data_query, filter_params)
                data = dictfetchall(cursor)
                
                # Reset statement timeout to default
                cursor.execute("RESET statement_timeout")
                
            # Process data to handle None values and dates
            for item in data:
                for key, value in item.items():
                    if value is None:
                        item[key] = 'N/A'
                    elif isinstance(value, datetime.date):
                        item[key] = value.isoformat()
            
            # Create pagination response
            total_pages = (total_count + page_size - 1) // page_size
            response_data = {
                'count': total_count,
                'next': f'/api/project-management/external-projects/?page={page+1}' if page < total_pages else None,
                'previous': f'/api/project-management/external-projects/?page={page-1}' if page > 1 else None,
                'results': data
            }
                
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error in ExternalProjectDetailsViewSet.list: {str(e)}")
            return Response(
                {"error": f"Failed to fetch external project details: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class ExternalProjectEquipmentsViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectEquipments.objects.all()
    serializer_class = ExternalProjectEquipmentsSerializer

class InternalProjectRequestViewSet(viewsets.ModelViewSet):
    queryset = InternalProjectRequest.objects.all()
    serializer_class = InternalProjectRequestSerializer
    pagination_class = StandardResultsSetPagination
    
    def list(self, request, *args, **kwargs):
        """Override list to include project details with specific columns and filtering"""
        try:
            # Get pagination parameters
            page = request.query_params.get('page', 1)
            try:
                page = int(page)
            except ValueError:
                page = 1
            
            page_size = 10
            offset = (page - 1) * page_size
            
            # Get filter parameters
            project_name = request.query_params.get('project_name', '')
            approval_id = request.query_params.get('approval_id', '')
            employee_id = request.query_params.get('employee_id', '')
            dept_id = request.query_params.get('dept_id', '')
            status = request.query_params.get('status', '')
            
            # Build filter conditions
            filter_conditions = []
            filter_params = []
            
            if project_name:
                filter_conditions.append("ipr.project_name ILIKE %s")
                filter_params.append(f"%{project_name}%")
            
            if approval_id:
                filter_conditions.append("ipd.approval_id ILIKE %s")
                filter_params.append(f"%{approval_id}%")
            
            if employee_id:
                filter_conditions.append("ipr.employee_id ILIKE %s")
                filter_params.append(f"%{employee_id}%")
            
            if dept_id:
                filter_conditions.append("d.dept_name ILIKE %s")  # Changed from ipr.dept_id to d.dept_name
                filter_params.append(f"%{dept_id}%")
            
            if status:
                filter_conditions.append("ipd.intrnl_project_status ILIKE %s")
                filter_params.append(f"%{status}%")
            
            # Build WHERE clause
            where_clause = ""
            if filter_conditions:
                where_clause = "WHERE " + " AND ".join(filter_conditions)
            else:
                where_clause = "WHERE 1=1"  # Always true condition if no other filters
            
            # Check if is_archived column exists
            has_is_archived = column_exists('internal_project_request', 'is_archived')
            
            # Add archive filter only if column exists
            archive_filter = ""
            if has_is_archived:
                archive_filter = "AND (ipr.is_archived IS NULL OR ipr.is_archived = FALSE)"
            
            # Execute query with pagination and filters
            with connection.cursor() as cursor:
                # Set statement timeout to 10 seconds (10000 milliseconds)
                cursor.execute("SET statement_timeout = 10000")
                
                # Get total count for pagination with filters
                count_query = f"""
                    SELECT COUNT(*) 
                    FROM project_management.internal_project_request ipr
                    LEFT JOIN project_management.internal_project_details ipd 
                        ON ipr.project_request_id = ipd.project_request_id
                    LEFT JOIN human_resources.employees e 
                        ON ipr.employee_id = e.employee_id
                    LEFT JOIN human_resources.departments d
                        ON ipr.dept_id = d.dept_id
                    {where_clause} {archive_filter}
                """
                cursor.execute(count_query, filter_params)
                total_count = cursor.fetchone()[0]
                
                # Get paginated data with filters
                data_query = f"""
                    SELECT 
                        ipr.project_request_id, 
                        ipr.project_name,
                        ipd.approval_id,
                        ipr.request_date,
                        e.first_name || ' ' || e.last_name AS employee_name,
                        ipr.employee_id,
                        d.dept_name AS department,  /* Changed from ipr.dept_id to d.dept_name */
                        ipd.intrnl_project_status AS project_status
                    FROM 
                        project_management.internal_project_request ipr
                    LEFT JOIN
                        project_management.internal_project_details ipd ON ipr.project_request_id = ipd.project_request_id
                    LEFT JOIN
                        human_resources.employees e ON ipr.employee_id = e.employee_id
                    LEFT JOIN
                        human_resources.departments d ON ipr.dept_id = d.dept_id
                    {where_clause} {archive_filter}
                    ORDER BY 
                        ipr.project_request_id
                    LIMIT {page_size} OFFSET {offset}
                """
                cursor.execute(data_query, filter_params)
                data = dictfetchall(cursor)
                
                # Reset statement timeout to default
                cursor.execute("RESET statement_timeout")
                
            # Process data to handle None values and dates
            for item in data:
                for key, value in item.items():
                    if value is None:
                        item[key] = 'N/A'
                    elif isinstance(value, datetime.date):
                        item[key] = value.isoformat()
            
            # Create pagination response
            total_pages = (total_count + page_size - 1) // page_size
            response_data = {
                'count': total_count,
                'next': f'/api/project-management/internal-requests/?page={page+1}' if page < total_pages else None,
                'previous': f'/api/project-management/internal-requests/?page={page-1}' if page > 1 else None,
                'results': data
            }
                
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error in InternalProjectRequestViewSet.list: {str(e)}")
            return Response(
                {"error": f"Failed to fetch internal project requests: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_archive(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=drf_status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id = request.user.id if request.user.is_authenticated else None
            
            success_count = 0
            for request_id in ids:
                if archive_internal_request(request_id, user_id):
                    success_count += 1
            
            return Response({
                "message": f"Successfully archived {success_count} of {len(ids)} requests",
                "success_count": success_count,
                "total_count": len(ids)
            })
        except Exception as e:
            logger.error(f"Error in bulk_archive: {str(e)}")
            return Response(
                {"error": f"Failed to archive requests: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class InternalProjectDetailsViewSet(viewsets.ModelViewSet):
    queryset = InternalProjectDetails.objects.all()
    serializer_class = InternalProjectDetailsSerializer
    pagination_class = StandardResultsSetPagination
    
    def list(self, request, *args, **kwargs):
        """Override list to include all columns from internal_project_details with filtering"""
        try:
            # Get pagination parameters
            page = request.query_params.get('page', 1)
            try:
                page = int(page)
            except ValueError:
                page = 1
            
            page_size = 10
            offset = (page - 1) * page_size
            
            # Get filter parameters
            project_name = request.query_params.get('project_name', '')
            approval_id = request.query_params.get('approval_id', '')
            employee_id = request.query_params.get('employee_id', '')
            status = request.query_params.get('status', '')
            
            # Build filter conditions
            filter_conditions = []
            filter_params = []
            
            if project_name:
                filter_conditions.append("ipr.project_name ILIKE %s")
                filter_params.append(f"%{project_name}%")
            
            if approval_id:
                filter_conditions.append("ipd.approval_id ILIKE %s")
                filter_params.append(f"%{approval_id}%")
            
            if employee_id:
                filter_conditions.append("ipr.employee_id ILIKE %s")
                filter_params.append(f"%{employee_id}%")
            
            if status:
                filter_conditions.append("ipd.intrnl_project_status ILIKE %s")
                filter_params.append(f"%{status}%")
            
            # Build WHERE clause
            where_clause = ""
            if filter_conditions:
                where_clause = "WHERE " + " AND ".join(filter_conditions)
            else:
                where_clause = "WHERE 1=1"  # Always true condition if no other filters
            
            # Check if is_archived column exists
            has_is_archived = column_exists('internal_project_details', 'is_archived')
            
            # Add archive filter only if column exists
            archive_filter = ""
            if has_is_archived:
                archive_filter = "AND (ipd.is_archived IS NULL OR ipd.is_archived = FALSE)"
            
            # Execute query with pagination and filters
            with connection.cursor() as cursor:
                # Set statement timeout to 10 seconds (10000 milliseconds)
                cursor.execute("SET statement_timeout = 10000")
                
                # Get total count for pagination with filters
                count_query = f"""
                    SELECT COUNT(*) 
                    FROM project_management.internal_project_details ipd
                    LEFT JOIN project_management.internal_project_request ipr 
                        ON ipd.project_request_id = ipr.project_request_id
                    LEFT JOIN human_resources.departments d 
                        ON ipr.dept_id = d.dept_id
                    {where_clause} {archive_filter}
                """
                cursor.execute(count_query, filter_params)
                total_count = cursor.fetchone()[0]
                
                # Get paginated data with filters
                data_query = f"""
                    SELECT 
                        ipd.intrnl_project_id,
                        ipr.project_request_id,
                        ipr.project_name,
                        ipd.intrnl_project_status AS status,
                        ipd.approval_id,
                        ipr.employee_id,
                        d.dept_name AS department,
                        ipr.reason_for_request AS description,
                        ipd.start_date,
                        ipd.estimated_end_date,
                        ipd.project_issues
                    FROM 
                        project_management.internal_project_details ipd
                    LEFT JOIN
                        project_management.internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
                    LEFT JOIN
                        human_resources.departments d ON ipr.dept_id = d.dept_id
                    {where_clause} {archive_filter}
                    ORDER BY
                        ipd.intrnl_project_id
                    LIMIT {page_size} OFFSET {offset}
                """
                cursor.execute(data_query, filter_params)
                data = dictfetchall(cursor)
                
                # Reset statement timeout to default
                cursor.execute("RESET statement_timeout")
                
            # Process data to handle None values and dates
            for item in data:
                for key, value in item.items():
                    if value is None:
                        item[key] = 'N/A'
                    elif isinstance(value, datetime.date):
                        item[key] = value.isoformat()
            
            # Create pagination response
            total_pages = (total_count + page_size - 1) // page_size
            response_data = {
                'count': total_count,
                'next': f'/api/project-management/internal-projects/?page={page+1}' if page < total_pages else None,
                'previous': f'/api/project-management/internal-projects/?page={page-1}' if page > 1 else None,
                'results': data
            }
                
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error in InternalProjectDetailsViewSet.list: {str(e)}")
            return Response(
                {"error": f"Failed to fetch internal project details: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProjectWarrantyViewSet(viewsets.ViewSet):
    """View for project warranty information"""
    
    @action(detail=False, methods=['get'])
    def warranty_list(self, request):
        try:
            # Get filter parameters
            project_id = request.query_params.get('project_id', '')
            project_name = request.query_params.get('project_name', '')
            warranty_status = request.query_params.get('warranty_status', '')
            
            # Build filter conditions
            filter_conditions = []
            filter_params = []
            
            if project_id:
                filter_conditions.append("d.project_id ILIKE %s")
                filter_params.append(f"%{project_id}%")
            
            if project_name:
                filter_conditions.append("r.ext_project_name ILIKE %s")
                filter_params.append(f"%{project_name}%")
            
            if warranty_status:
                filter_conditions.append("d.warranty_status ILIKE %s")
                filter_params.append(f"%{warranty_status}%")
            
            # Build WHERE clause
            where_clause = ""
            if filter_conditions:
                where_clause = "WHERE " + " AND ".join(filter_conditions)
            else:
                where_clause = "WHERE 1=1"  # Always true condition if no other filters
            
            # Check if is_archived column exists
            has_is_archived = column_exists('external_project_details', 'is_archived')
            
            # Add archive filter only if column exists
            archive_filter = ""
            if has_is_archived:
                archive_filter = "AND (d.is_archived IS NULL OR d.is_archived = FALSE)"
            
            with connection.cursor() as cursor:
                # Set statement timeout to 10 seconds (10000 milliseconds)
                cursor.execute("SET statement_timeout = 10000")
                
                query = f"""
                    SELECT 
                        d.project_id,
                        r.ext_project_name,
                        d.warranty_coverage_yr,
                        d.warranty_status,
                        d.warranty_start_date,
                        d.warranty_end_date
                    FROM 
                        project_management.external_project_details d
                    JOIN 
                        project_management.external_project_request r 
                        ON d.ext_project_request_id = r.ext_project_request_id
                    {where_clause} {archive_filter}
                    ORDER BY d.project_id
                """
                cursor.execute(query, filter_params)
                data = dictfetchall(cursor)
                
                # Reset statement timeout to default
                cursor.execute("RESET statement_timeout")
                
            # Process data to handle None values and dates
            for item in data:
                for key, value in item.items():
                    if value is None:
                        item[key] = 'N/A'
                    elif isinstance(value, datetime.date):
                        item[key] = value.isoformat()
                
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching warranty data: {str(e)}")
            return Response(
                {"error": f"Failed to fetch warranty data: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )