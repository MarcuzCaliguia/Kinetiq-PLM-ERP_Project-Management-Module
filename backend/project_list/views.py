from rest_framework import viewsets, status as drf_status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db import connection, transaction
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

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
import functools

logger = logging.getLogger(__name__)


CACHE_TTL_SHORT = getattr(settings, 'CACHE_TTL_SHORT', 60 * 5)  
CACHE_TTL_MEDIUM = getattr(settings, 'CACHE_TTL_MEDIUM', 60 * 30)  
CACHE_TTL_LONG = getattr(settings, 'CACHE_TTL_LONG', 60 * 60 * 2)  
DB_STATEMENT_TIMEOUT = getattr(settings, 'DB_STATEMENT_TIMEOUT', 30000)  


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number
        })


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        {columns[i]: value for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]


def with_db_timeout(func):
    """Decorator to set a longer timeout for database operations"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute(f"SET statement_timeout = {DB_STATEMENT_TIMEOUT}")
            try:
                return func(*args, **kwargs)
            finally:
                cursor.execute("RESET statement_timeout")
    return wrapper


def format_response_data(data):
    """Format data for response - handle None values and dates"""
    for item in data:
        for key, value in item.items():
            if value is None:
                item[key] = 'N/A'
            elif isinstance(value, (datetime.date, datetime.datetime)):
                item[key] = value.isoformat()
    return data


def column_exists(table_name, column_name, schema='project_management'):
    """Check if a column exists in a table"""
    cache_key = f"column_exists:{schema}.{table_name}.{column_name}"
    cached_result = cache.get(cache_key)
    
    if cached_result is not None:
        return cached_result
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = %s 
            AND column_name = %s
        """, [schema, table_name, column_name])
        result = cursor.fetchone() is not None
        
    
    cache.set(cache_key, result, 60 * 60)
    return result


@with_db_timeout
def add_performance_indexes():
    """Add indexes to improve query performance"""
    cache_key = "performance_indexes_added"
    if cache.get(cache_key):
        return
        
    with connection.cursor() as cursor:
        try:
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ext_project_request_name 
                ON project_management.external_project_request(ext_project_name);
                
                CREATE INDEX IF NOT EXISTS idx_ext_project_request_approval 
                ON project_management.external_project_request(approval_id);
                
                CREATE INDEX IF NOT EXISTS idx_ext_project_request_item 
                ON project_management.external_project_request(item_id);
                
                CREATE INDEX IF NOT EXISTS idx_ext_project_details_status 
                ON project_management.external_project_details(project_status);
                
                CREATE INDEX IF NOT EXISTS idx_ext_project_details_request_id 
                ON project_management.external_project_details(ext_project_request_id);
                
                CREATE INDEX IF NOT EXISTS idx_int_project_request_name 
                ON project_management.internal_project_request(project_name);
                
                CREATE INDEX IF NOT EXISTS idx_int_project_request_employee 
                ON project_management.internal_project_request(employee_id);
                
                CREATE INDEX IF NOT EXISTS idx_int_project_request_dept 
                ON project_management.internal_project_request(dept_id);
                
                CREATE INDEX IF NOT EXISTS idx_int_project_details_status 
                ON project_management.internal_project_details(intrnl_project_status);
                
                CREATE INDEX IF NOT EXISTS idx_int_project_details_request_id 
                ON project_management.internal_project_details(project_request_id);
                
                CREATE INDEX IF NOT EXISTS idx_int_project_details_approval 
                ON project_management.internal_project_details(approval_id);
                
                CREATE INDEX IF NOT EXISTS idx_archived_ext_project_request_name 
                ON project_management.archived_external_project_request(ext_project_name);
                
                CREATE INDEX IF NOT EXISTS idx_archived_int_project_request_name 
                ON project_management.archived_internal_project_request(project_name);
                
                -- Add indexes on archived date for faster sorting
                CREATE INDEX IF NOT EXISTS idx_archived_ext_project_request_date 
                ON project_management.archived_external_project_request(archived_date);
                
                CREATE INDEX IF NOT EXISTS idx_archived_int_project_request_date 
                ON project_management.archived_internal_project_request(archived_date);
                
                -- Add composite indexes for common query patterns
                CREATE INDEX IF NOT EXISTS idx_ext_project_request_composite 
                ON project_management.external_project_request(ext_project_name, approval_id, item_id);
                
                CREATE INDEX IF NOT EXISTS idx_int_project_request_composite 
                ON project_management.internal_project_request(project_name, employee_id, dept_id);
            """)
            logger.info("Performance indexes created successfully")
            
            
            cache.set(cache_key, True, 60 * 60 * 24)  
        except Exception as e:
            logger.error(f"Error creating performance indexes: {str(e)}")


@with_db_timeout
def archive_external_request(request_id, user_id=None):
    """Archive an external project request and its related data"""
    with connection.cursor() as cursor:
        
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
        
        
        try:
            cursor.execute("BEGIN")
            
            
            cursor.execute("""
                SELECT ext_project_request_id FROM project_management.external_project_request
                WHERE ext_project_request_id = %s
            """, [request_id])
            
            if cursor.fetchone() is None:
                cursor.execute("ROLLBACK")
                logger.warning(f"External request {request_id} not found for archiving")
                return False
            
            
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
            
            cursor.execute("COMMIT")
            
            
            cache.delete_pattern("external_project_*")
            
            return True
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Error archiving external request {request_id}: {str(e)}")
            return False


@with_db_timeout
def archive_internal_request(request_id, user_id=None):
    """Archive an internal project request and its related data"""
    with connection.cursor() as cursor:
        
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
        
        
        try:
            cursor.execute("BEGIN")
            
            
            cursor.execute("""
                SELECT project_request_id FROM project_management.internal_project_request
                WHERE project_request_id = %s
            """, [request_id])
            
            if cursor.fetchone() is None:
                cursor.execute("ROLLBACK")
                logger.warning(f"Internal request {request_id} not found for archiving")
                return False
            
            
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
            
            cursor.execute("COMMIT")
            
            
            cache.delete_pattern("internal_project_*")
            
            return True
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Error archiving internal request {request_id}: {str(e)}")
            return False


class BaseProjectViewSet(viewsets.ModelViewSet):
    """Base ViewSet with common methods for all project viewsets"""
    pagination_class = StandardResultsSetPagination
    
    def get_archive_filter(self, table_name):
        """Get the archive filter clause for SQL queries"""
        has_is_archived = column_exists(table_name, 'is_archived')
        return f"AND ({table_name}.is_archived IS NULL OR {table_name}.is_archived = FALSE)" if has_is_archived else ""
    
    def build_where_clause(self, filter_conditions):
        """Build a WHERE clause from filter conditions"""
        if filter_conditions:
            return "WHERE " + " AND ".join(filter_conditions)
        return "WHERE 1=1"
    
    def get_pagination_response(self, data, total_count, page, page_size, base_url):
        """Build a paginated response"""
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            'count': total_count,
            'next': f'{base_url}?page={page+1}' if page < total_pages else None,
            'previous': f'{base_url}?page={page-1}' if page > 1 else None,
            'total_pages': total_pages,
            'current_page': page,
            'results': format_response_data(data)
        }
    
    def parse_pagination_params(self, request):
        """Parse pagination parameters from request"""
        try:
            page = int(request.query_params.get('page', 1))
        except ValueError:
            page = 1
        
        try:
            page_size = min(
                int(request.query_params.get('page_size', 10)),
                self.pagination_class.max_page_size
            )
        except ValueError:
            page_size = 10
            
        return page, page_size


class ExternalProjectRequestViewSet(BaseProjectViewSet):
    queryset = ExternalProjectRequest.objects.all()
    serializer_class = ExternalProjectRequestSerializer
    
    def get_queryset(self):
        """Override to filter out archived requests by default"""
        queryset = ExternalProjectRequest.objects.all()
        
        
        if hasattr(ExternalProjectRequest, 'is_archived'):
            queryset = queryset.filter(Q(is_archived=False) | Q(is_archived=None))
            
        return queryset
    
    @method_decorator(cache_page(CACHE_TTL_SHORT))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """Override list to include specific columns with filtering"""
        try:
            
            page, page_size = self.parse_pagination_params(request)
            offset = (page - 1) * page_size
            
            
            project_name = request.query_params.get('project_name', '')
            approval_id = request.query_params.get('approval_id', '')
            item_id = request.query_params.get('item_id', '')
            status = request.query_params.get('status', '')
            
            
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
            
            
            where_clause = self.build_where_clause(filter_conditions)
            
            
            archive_filter = self.get_archive_filter('epr')
            
            
            cache_key = f"external_project_list:{page}:{page_size}:{project_name}:{approval_id}:{item_id}:{status}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return Response(cached_data)
            
            with connection.cursor() as cursor:
                cursor.execute(f"SET statement_timeout = {DB_STATEMENT_TIMEOUT}")
                
                
                count_query = f"""
                    SELECT COUNT(*) 
                    FROM project_management.external_project_request epr
                    LEFT JOIN project_management.external_project_details epd 
                        ON epr.ext_project_request_id = epd.ext_project_request_id
                    {where_clause} {archive_filter}
                """
                cursor.execute(count_query, filter_params)
                total_count = cursor.fetchone()[0]
                
                
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
                
                cursor.execute("RESET statement_timeout")
            
            
            response_data = self.get_pagination_response(
                data, 
                total_count, 
                page, 
                page_size, 
                '/api/project-management/external-requests/'
            )
            
            
            cache.set(cache_key, response_data, CACHE_TTL_SHORT)
                
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
            failed_ids = []
            
            with transaction.atomic():
                for request_id in ids:
                    if archive_external_request(request_id, user_id):
                        success_count += 1
                    else:
                        failed_ids.append(request_id)
            
            
            cache.delete_pattern("external_project_*")
            
            return Response({
                "message": f"Successfully archived {success_count} of {len(ids)} requests",
                "success_count": success_count,
                "total_count": len(ids),
                "failed_ids": failed_ids
            })
        except Exception as e:
            logger.error(f"Error in bulk_archive: {str(e)}")
            return Response(
                {"error": f"Failed to archive requests: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExternalProjectDetailsViewSet(BaseProjectViewSet):
    queryset = ExternalProjectDetails.objects.all()
    serializer_class = ExternalProjectDetailsSerializer
    
    def get_queryset(self):
        """Override to filter out archived details by default"""
        queryset = ExternalProjectDetails.objects.all()
        
        
        if hasattr(ExternalProjectDetails, 'is_archived'):
            queryset = queryset.filter(Q(is_archived=False) | Q(is_archived=None))
            
        return queryset
    
    @method_decorator(cache_page(CACHE_TTL_SHORT))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """Override list to include all columns from external_project_details with filtering"""
        try:
            
            page, page_size = self.parse_pagination_params(request)
            offset = (page - 1) * page_size
            
            
            project_name = request.query_params.get('project_name', '')
            approval_id = request.query_params.get('approval_id', '')
            status = request.query_params.get('status', '')
            
            
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
            
            
            where_clause = self.build_where_clause(filter_conditions)
            
            
            archive_filter = self.get_archive_filter('epd')
            
            
            cache_key = f"external_project_details:{page}:{page_size}:{project_name}:{approval_id}:{status}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return Response(cached_data)
            
            with connection.cursor() as cursor:
                cursor.execute(f"SET statement_timeout = {DB_STATEMENT_TIMEOUT}")
                
                
                count_query = f"""
                    SELECT COUNT(*) 
                    FROM project_management.external_project_details epd
                    LEFT JOIN project_management.external_project_request epr 
                        ON epd.ext_project_request_id = epr.ext_project_request_id
                    {where_clause} {archive_filter}
                """
                cursor.execute(count_query, filter_params)
                total_count = cursor.fetchone()[0]
                
                
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
                
                cursor.execute("RESET statement_timeout")
            
            
            response_data = self.get_pagination_response(
                data, 
                total_count, 
                page, 
                page_size, 
                '/api/project-management/external-projects/'
            )
            
            
            cache.set(cache_key, response_data, CACHE_TTL_SHORT)
                
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


class InternalProjectRequestViewSet(BaseProjectViewSet):
    queryset = InternalProjectRequest.objects.all()
    serializer_class = InternalProjectRequestSerializer
    
    def get_queryset(self):
        """Override to filter out archived requests by default"""
        queryset = InternalProjectRequest.objects.all()
        
        
        if hasattr(InternalProjectRequest, 'is_archived'):
            queryset = queryset.filter(Q(is_archived=False) | Q(is_archived=None))
            
        return queryset
    
    @method_decorator(cache_page(CACHE_TTL_SHORT))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """Override list to include project details with specific columns and filtering"""
        try:
            
            page, page_size = self.parse_pagination_params(request)
            offset = (page - 1) * page_size
            
            
            project_name = request.query_params.get('project_name', '')
            approval_id = request.query_params.get('approval_id', '')
            employee_id = request.query_params.get('employee_id', '')
            dept_id = request.query_params.get('dept_id', '')
            status = request.query_params.get('status', '')
            
            
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
                filter_conditions.append("d.dept_name ILIKE %s")  
                filter_params.append(f"%{dept_id}%")
            
            if status:
                filter_conditions.append("ipd.intrnl_project_status ILIKE %s")
                filter_params.append(f"%{status}%")
            
            
            where_clause = self.build_where_clause(filter_conditions)
            
            
            archive_filter = self.get_archive_filter('ipr')
            
            
            cache_key = f"internal_project_list:{page}:{page_size}:{project_name}:{approval_id}:{employee_id}:{dept_id}:{status}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return Response(cached_data)
            
            with connection.cursor() as cursor:
                cursor.execute(f"SET statement_timeout = {DB_STATEMENT_TIMEOUT}")
                
                
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
                
                
                data_query = f"""
                    SELECT 
                        ipr.project_request_id, 
                        ipr.project_name,
                        ipd.approval_id,
                        ipr.request_date,
                        e.first_name || ' ' || e.last_name AS employee_name,
                        ipr.employee_id,
                        d.dept_name AS department,
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
                
                cursor.execute("RESET statement_timeout")
            
            
            response_data = self.get_pagination_response(
                data, 
                total_count, 
                page, 
                page_size, 
                '/api/project-management/internal-requests/'
            )
            
            
            cache.set(cache_key, response_data, CACHE_TTL_SHORT)
                
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
            failed_ids = []
            
            with transaction.atomic():
                for request_id in ids:
                    if archive_internal_request(request_id, user_id):
                        success_count += 1
                    else:
                        failed_ids.append(request_id)
            
            
            cache.delete_pattern("internal_project_*")
            
            return Response({
                "message": f"Successfully archived {success_count} of {len(ids)} requests",
                "success_count": success_count,
                "total_count": len(ids),
                "failed_ids": failed_ids
            })
        except Exception as e:
            logger.error(f"Error in bulk_archive: {str(e)}")
            return Response(
                {"error": f"Failed to archive requests: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

class InternalProjectDetailsViewSet(BaseProjectViewSet):
    queryset = InternalProjectDetails.objects.all()
    serializer_class = InternalProjectDetailsSerializer
    
    def get_queryset(self):
        """Override to filter out archived details by default"""
        queryset = InternalProjectDetails.objects.all()
        
        
        if hasattr(InternalProjectDetails, 'is_archived'):
            queryset = queryset.filter(Q(is_archived=False) | Q(is_archived=None))
            
        return queryset
    
    @method_decorator(cache_page(CACHE_TTL_SHORT))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """Override list to include all columns from internal_project_details with filtering"""
        try:
            
            page, page_size = self.parse_pagination_params(request)
            offset = (page - 1) * page_size
            
            
            project_name = request.query_params.get('project_name', '')
            approval_id = request.query_params.get('approval_id', '')
            employee_id = request.query_params.get('employee_id', '')
            status = request.query_params.get('status', '')
            
            
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
            
            
            where_clause = self.build_where_clause(filter_conditions)
            
            
            archive_filter = self.get_archive_filter('ipd')
            
            
            cache_key = f"internal_project_details:{page}:{page_size}:{project_name}:{approval_id}:{employee_id}:{status}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return Response(cached_data)
            
            with connection.cursor() as cursor:
                cursor.execute(f"SET statement_timeout = {DB_STATEMENT_TIMEOUT}")
                
                
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
                
                cursor.execute("RESET statement_timeout")
            
            
            response_data = self.get_pagination_response(
                data, 
                total_count, 
                page, 
                page_size, 
                '/api/project-management/internal-projects/'
            )
            
            
            cache.set(cache_key, response_data, CACHE_TTL_SHORT)
                
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error in InternalProjectDetailsViewSet.list: {str(e)}")
            return Response(
                {"error": f"Failed to fetch internal project details: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProjectWarrantyViewSet(viewsets.ViewSet):
    """View for project warranty information"""
    
    @method_decorator(cache_page(CACHE_TTL_MEDIUM))
    @method_decorator(vary_on_cookie)
    @action(detail=False, methods=['get'])
    def warranty_list(self, request):
        try:
            
            project_id = request.query_params.get('project_id', '')
            project_name = request.query_params.get('project_name', '')
            warranty_status = request.query_params.get('warranty_status', '')
            
            
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
            
            
            where_clause = "WHERE " + " AND ".join(filter_conditions) if filter_conditions else "WHERE 1=1"
            
            
            has_is_archived = column_exists('external_project_details', 'is_archived')
            
            
            archive_filter = ""
            if has_is_archived:
                archive_filter = "AND (d.is_archived IS NULL OR d.is_archived = FALSE)"
            
            
            cache_key = f"warranty_list:{project_id}:{project_name}:{warranty_status}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return Response(cached_data)
            
            with connection.cursor() as cursor:
                cursor.execute(f"SET statement_timeout = {DB_STATEMENT_TIMEOUT}")
                
                
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
                    ORDER BY 
                        CASE 
                            WHEN d.warranty_status = 'Active' THEN 1
                            WHEN d.warranty_status = 'Expiring Soon' THEN 2
                            WHEN d.warranty_status = 'Expired' THEN 3
                            ELSE 4
                        END,
                        d.warranty_end_date
                """
                cursor.execute(query, filter_params)
                data = dictfetchall(cursor)
                
                cursor.execute("RESET statement_timeout")
            
            
            formatted_data = format_response_data(data)
            
            
            cache.set(cache_key, formatted_data, CACHE_TTL_MEDIUM)
                
            return Response(formatted_data)
        except Exception as e:
            logger.error(f"Error fetching warranty data: {str(e)}")
            return Response(
                {"error": f"Failed to fetch warranty data: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@with_db_timeout
def restore_external_request(request_id, user_id=None):
    """Restore an archived external project request and its related data"""
    with connection.cursor() as cursor:
        try:
            cursor.execute("BEGIN")
            
            
            cursor.execute("""
                SELECT * FROM project_management.archived_external_project_request
                WHERE ext_project_request_id = %s
            """, [request_id])
            
            if cursor.fetchone() is None:
                cursor.execute("ROLLBACK")
                return False, "Request not found in archive"
            
            
            cursor.execute("""
                UPDATE project_management.external_project_request
                SET is_archived = FALSE
                WHERE ext_project_request_id = %s
            """, [request_id])
            
            cursor.execute("""
                UPDATE project_management.external_project_details
                SET is_archived = FALSE
                WHERE ext_project_request_id = %s
            """, [request_id])
            
            
            cursor.execute("""
                DELETE FROM project_management.archived_external_project_details
                WHERE ext_project_request_id = %s
            """, [request_id])
            
            cursor.execute("""
                DELETE FROM project_management.archived_external_project_request
                WHERE ext_project_request_id = %s
            """, [request_id])
            
            
            setup_restore_log()
            
            
            cursor.execute("""
                INSERT INTO project_management.restore_log
                (item_id, item_type, restored_by, restore_date)
                VALUES (%s, 'external_request', %s, CURRENT_TIMESTAMP)
                ON CONFLICT (item_id, item_type) DO UPDATE 
                SET restored_by = %s, restore_date = CURRENT_TIMESTAMP
            """, [request_id, user_id, user_id])
            
            cursor.execute("COMMIT")
            
            
            cache.delete_pattern("external_project_*")
            cache.delete_pattern("archived_external_*")
            
            return True, "Successfully restored external request"
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Error restoring external request {request_id}: {str(e)}")
            return False, str(e)


@with_db_timeout
def restore_internal_request(request_id, user_id=None):
    """Restore an archived internal project request and its related data"""
    with connection.cursor() as cursor:
        try:
            cursor.execute("BEGIN")
            
            
            cursor.execute("""
                SELECT * FROM project_management.archived_internal_project_request
                WHERE project_request_id = %s
            """, [request_id])
            
            if cursor.fetchone() is None:
                cursor.execute("ROLLBACK")
                return False, "Request not found in archive"
            
            
            cursor.execute("""
                UPDATE project_management.internal_project_request
                SET is_archived = FALSE
                WHERE project_request_id = %s
            """, [request_id])
            
            cursor.execute("""
                UPDATE project_management.internal_project_details
                SET is_archived = FALSE
                WHERE project_request_id = %s
            """, [request_id])
            
            
            cursor.execute("""
                DELETE FROM project_management.archived_internal_project_details
                WHERE project_request_id = %s
            """, [request_id])
            
            cursor.execute("""
                DELETE FROM project_management.archived_internal_project_request
                WHERE project_request_id = %s
            """, [request_id])
            
            
            setup_restore_log()
            
            
            cursor.execute("""
                INSERT INTO project_management.restore_log
                (item_id, item_type, restored_by, restore_date)
                VALUES (%s, 'internal_request', %s, CURRENT_TIMESTAMP)
                ON CONFLICT (item_id, item_type) DO UPDATE 
                SET restored_by = %s, restore_date = CURRENT_TIMESTAMP
            """, [request_id, user_id, user_id])
            
            cursor.execute("COMMIT")
            
            
            cache.delete_pattern("internal_project_*")
            cache.delete_pattern("archived_internal_*")
            
            return True, "Successfully restored internal request"
        except Exception as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Error restoring internal request {request_id}: {str(e)}")
            return False, str(e)


class ArchivedProjectsViewSet(BaseProjectViewSet):
    """ViewSet for managing archived projects"""
    
    @method_decorator(cache_page(CACHE_TTL_MEDIUM))
    @method_decorator(vary_on_cookie)
    @action(detail=False, methods=['get'])
    def external_requests(self, request):
        """Get archived external project requests"""
        try:
            
            page, page_size = self.parse_pagination_params(request)
            offset = (page - 1) * page_size
            
            
            project_name = request.query_params.get('project_name', '')
            approval_id = request.query_params.get('approval_id', '')
            
            
            filter_conditions = []
            filter_params = []
            
            if project_name:
                filter_conditions.append("a.ext_project_name ILIKE %s")
                filter_params.append(f"%{project_name}%")
            
            if approval_id:
                filter_conditions.append("a.approval_id ILIKE %s")
                filter_params.append(f"%{approval_id}%")
            
            
            where_clause = self.build_where_clause(filter_conditions)
            
            
            cache_key = f"archived_external_requests:{page}:{page_size}:{project_name}:{approval_id}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return Response(cached_data)
            
            with connection.cursor() as cursor:
                cursor.execute(f"SET statement_timeout = {DB_STATEMENT_TIMEOUT}")
                
                
                count_query = f"""
                    SELECT COUNT(*) 
                    FROM project_management.archived_external_project_request a
                    {where_clause}
                """
                cursor.execute(count_query, filter_params)
                total_count = cursor.fetchone()[0]
                
                
                data_query = f"""
                    SELECT 
                        a.ext_project_request_id,
                        a.ext_project_name AS project_name,
                        a.approval_id,
                        a.item_id,
                        a.archived_date,
                        d.project_status,
                        d.start_date
                    FROM 
                        project_management.archived_external_project_request a
                    LEFT JOIN 
                        project_management.archived_external_project_details d
                        ON a.ext_project_request_id = d.ext_project_request_id
                    {where_clause}
                    ORDER BY a.archived_date DESC
                    LIMIT {page_size} OFFSET {offset}
                """
                cursor.execute(data_query, filter_params)
                data = dictfetchall(cursor)
                
                cursor.execute("RESET statement_timeout")
            
            
            response_data = self.get_pagination_response(
                data, 
                total_count, 
                page, 
                page_size, 
                '/api/project-management/archived-projects/external_requests/'
            )
            
            
            cache.set(cache_key, response_data, CACHE_TTL_MEDIUM)
                
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error fetching archived external requests: {str(e)}")
            return Response(
                {"error": f"Failed to fetch archived external requests: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @method_decorator(cache_page(CACHE_TTL_MEDIUM))
    @method_decorator(vary_on_cookie)
    @action(detail=False, methods=['get'])
    def internal_requests(self, request):
        """Get archived internal project requests"""
        try:
            
            page, page_size = self.parse_pagination_params(request)
            offset = (page - 1) * page_size
            
            
            project_name = request.query_params.get('project_name', '')
            
            
            filter_conditions = []
            filter_params = []
            
            if project_name:
                filter_conditions.append("a.project_name ILIKE %s")
                filter_params.append(f"%{project_name}%")
            
            
            where_clause = self.build_where_clause(filter_conditions)
            
            
            cache_key = f"archived_internal_requests:{page}:{page_size}:{project_name}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return Response(cached_data)
            
            with connection.cursor() as cursor:
                cursor.execute(f"SET statement_timeout = {DB_STATEMENT_TIMEOUT}")
                
                
                count_query = f"""
                    SELECT COUNT(*) 
                    FROM project_management.archived_internal_project_request a
                    {where_clause}
                """
                cursor.execute(count_query, filter_params)
                total_count = cursor.fetchone()[0]
                
                
                data_query = f"""
                    SELECT 
                        a.project_request_id,
                        a.project_name,
                        a.request_date,
                        a.employee_id,
                        a.dept_id,
                        a.archived_date,
                        d.approval_id,
                        d.intrnl_project_status AS project_status
                    FROM 
                        project_management.archived_internal_project_request a
                    LEFT JOIN 
                        project_management.archived_internal_project_details d
                        ON a.project_request_id = d.project_request_id
                    {where_clause}
                    ORDER BY a.archived_date DESC
                    LIMIT {page_size} OFFSET {offset}
                """
                cursor.execute(data_query, filter_params)
                data = dictfetchall(cursor)
                
                cursor.execute("RESET statement_timeout")
            
            
            response_data = self.get_pagination_response(
                data, 
                total_count, 
                page, 
                page_size, 
                '/api/project-management/archived-projects/internal_requests/'
            )
            
            
            cache.set(cache_key, response_data, CACHE_TTL_MEDIUM)
                
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error fetching archived internal requests: {str(e)}")
            return Response(
                {"error": f"Failed to fetch archived internal requests: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def restore_external(self, request):
        """Restore archived external project requests"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=drf_status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id = request.user.id if request.user.is_authenticated else None
            
            success_count = 0
            failed_ids = []
            messages = []
            
            with transaction.atomic():
                for request_id in ids:
                    success, message = restore_external_request(request_id, user_id)
                    if success:
                        success_count += 1
                    else:
                        failed_ids.append(request_id)
                        messages.append(f"ID {request_id}: {message}")
            
            
            cache.delete_pattern("external_project_*")
            cache.delete_pattern("archived_external_*")
            
            return Response({
                "message": f"Successfully restored {success_count} of {len(ids)} requests",
                "success_count": success_count,
                "total_count": len(ids),
                "failed_ids": failed_ids,
                "error_messages": messages if failed_ids else []
            })
        except Exception as e:
            logger.error(f"Error in restore_external: {str(e)}")
            return Response(
                {"error": f"Failed to restore requests: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def restore_internal(self, request):
        """Restore archived internal project requests"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=drf_status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id = request.user.id if request.user.is_authenticated else None
            
            success_count = 0
            failed_ids = []
            messages = []
            
            with transaction.atomic():
                for request_id in ids:
                    success, message = restore_internal_request(request_id, user_id)
                    if success:
                        success_count += 1
                    else:
                        failed_ids.append(request_id)
                        messages.append(f"ID {request_id}: {message}")
            
            
            cache.delete_pattern("internal_project_*")
            cache.delete_pattern("archived_internal_*")
            
            return Response({
                "message": f"Successfully restored {success_count} of {len(ids)} requests",
                "success_count": success_count,
                "total_count": len(ids),
                "failed_ids": failed_ids,
                "error_messages": messages if failed_ids else []
            })
        except Exception as e:
            logger.error(f"Error in restore_internal: {str(e)}")
            return Response(
                {"error": f"Failed to restore requests: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@with_db_timeout
def setup_restore_log():
    """Set up the restore log table if it doesn't exist"""
    cache_key = "restore_log_setup_complete"
    if cache.get(cache_key):
        return
        
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_management.restore_log (
                    log_id SERIAL PRIMARY KEY,
                    item_id VARCHAR(255) NOT NULL,
                    item_type VARCHAR(50) NOT NULL,
                    restored_by VARCHAR(255),
                    restore_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(item_id, item_type)
                )
            """)
            
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_restore_log_item 
                ON project_management.restore_log(item_id, item_type);
                
                CREATE INDEX IF NOT EXISTS idx_restore_log_date
                ON project_management.restore_log(restore_date);
            """)
            
            
            cache.set(cache_key, True, 60 * 60 * 24)  
        except Exception as e:
            logger.error(f"Error setting up restore log: {str(e)}")



add_performance_indexes()
setup_restore_log()