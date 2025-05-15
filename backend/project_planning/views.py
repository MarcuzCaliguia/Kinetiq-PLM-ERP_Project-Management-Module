from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import connection, transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.conf import settings
import uuid
import logging
import time
from functools import wraps
from django.db.models import Prefetch, Q
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from datetime import datetime
import threading
from django.core.exceptions import ValidationError

from .models import (
    ExternalProjectRequest, ExternalProjectDetails, ExternalProjectLabor,
    ExternalProjectEquipments, ExternalProjectWarranty,
    InternalProjectRequest, InternalProjectDetails, InternalProjectLabor
)
from .serializers import (
    ExternalProjectRequestSerializer, ExternalProjectDetailsSerializer,
    ExternalProjectLaborSerializer, ExternalProjectEquipmentsSerializer,
    ExternalProjectWarrantySerializer, InternalProjectRequestSerializer,
    InternalProjectDetailsSerializer, InternalProjectLaborSerializer
)

# Cache timeouts - reduced for Zappa
CACHE_TTL_SHORT = getattr(settings, 'CACHE_TTL_SHORT', 60 * 2)  # 2 minutes
CACHE_TTL_MEDIUM = getattr(settings, 'CACHE_TTL_MEDIUM', 60 * 10)  # 10 minutes
CACHE_TTL_LONG = getattr(settings, 'CACHE_TTL_LONG', 60 * 30)  # 30 minutes

# Database settings
DB_STATEMENT_TIMEOUT = getattr(settings, 'DB_STATEMENT_TIMEOUT', 15000)  # 15 seconds

# Add constants
PROJECT_STATUS_CHOICES = [
    'not started',
    'in progress',
    'completed',
    'on hold',
    'cancelled'
]

INTERNAL_PROJECT_TYPES = [
    "Training Program",
    "Department Event",
    "Facility Maintenance"
]

logger = logging.getLogger(__name__)



def generate_id(prefix):
    """Generate a unique ID with the given prefix"""
    unique_id = uuid.uuid4().hex[:6].upper()
    from datetime import datetime
    year = datetime.now().year
    return f"PROJ-{prefix}-{year}-{unique_id}"


def api_exception_handler(func):
    """Decorator to handle exceptions in API views with specific error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            return Response(
                {'error': str(e), 'type': 'validation_error'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except ExternalProjectRequest.DoesNotExist:
            logger.warning(f"Resource not found in {func.__name__}")
            return Response(
                {'error': 'Requested resource not found', 'type': 'not_found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred', 'type': 'server_error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper


def log_performance(func):
    """Decorator to log function execution time with structured logging"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            
            # Log performance metrics
            logger.info(
                "Function execution completed",
                extra={
                    'function_name': func.__name__,
                    'execution_time_ms': round(execution_time, 2),
                    'status': 'success'
                }
            )
            
            # Log slow operations
            if execution_time > 1000:  # More than 1 second
                logger.warning(
                    "Slow operation detected",
                    extra={
                        'function_name': func.__name__,
                        'execution_time_ms': round(execution_time, 2),
                        'threshold_ms': 1000
                    }
                )
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(
                "Function execution failed",
                extra={
                    'function_name': func.__name__,
                    'execution_time_ms': round(execution_time, 2),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'status': 'error'
                },
                exc_info=True
            )
            raise
            
    return wrapper


class QueryExecutor:
    """Class to execute database queries with proper error handling and timeout"""
    MAX_RESULT_SIZE = 10000  # Maximum number of rows to return

    @staticmethod
    def execute(query, params=None, fetchone=False, fetchall=False, timeout=None, max_rows=None):
        from django.db import connection
        if timeout is None:
            timeout = DB_STATEMENT_TIMEOUT
        if max_rows is None:
            max_rows = QueryExecutor.MAX_RESULT_SIZE
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SET statement_timeout = {timeout}")
                start_time = time.time()
                cursor.execute(query, params or [])
                execution_time = (time.time() - start_time) * 1000
                if execution_time > 1000:
                    logger.warning(f"Slow query detected ({execution_time:.2f}ms): {query}")
                if fetchone:
                    result = cursor.fetchone()
                elif fetchall:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchmany(max_rows)
                    if cursor.fetchone():
                        logger.warning(f"Query result truncated to {max_rows} rows")
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    result = True
                cursor.execute("RESET statement_timeout")
                return result
        except Exception as e:
            logger.error(f"Query failed: {str(e)}\nQuery: {query}\nParams: {params}")
            raise


class ValidationMixin:
    """Mixin for common validation tasks with optimized caching"""
    
    @staticmethod
    def sanitize_input(value):
        """Sanitize input string to prevent injection attacks"""
        if not isinstance(value, str):
            return value
        # Remove any potential SQL injection characters
        return value.replace("'", "''").replace(";", "")
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validate that all required fields are present and not empty"""
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    @staticmethod
    def validate_date_format(date_str, format='%Y-%m-%d'):
        """Validate date string format"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, format).date()
        except ValueError:
            raise ValueError(f"Invalid date format. Expected {format}")
    
    @staticmethod
    def validate_enum_value(value, valid_values, field_name):
        """Validate that a value is in the list of valid values"""
        if value and value not in valid_values:
            raise ValueError(f"Invalid {field_name}. Valid values are: {', '.join(valid_values)}")
        return value
    
    @staticmethod
    def validate_employee_exists(employee_id):
        """Validate that an employee exists in the database with optimized caching"""
        if not employee_id:
            return True
        
        cache_key = f"employee_exists_{employee_id}"
        exists = cache.get(cache_key)
        
        if exists is None:
            try:
                employee_exists = QueryExecutor.execute(
                    "SELECT 1 FROM human_resources.employees WHERE employee_id = %s LIMIT 1",
                    [employee_id],
                    fetchone=True,
                    timeout=5000
                )
                exists = bool(employee_exists)
                cache.set(cache_key, exists, CACHE_TTL_SHORT)
            except Exception:
                logger.warning(f"Could not verify if employee {employee_id} exists")
                return True
        
        return exists
    
    @staticmethod
    def validate_project_exists(project_id, is_internal=False):
        """Validate that a project exists in the database with optimized caching"""
        if not project_id:
            return False
        
        cache_key = f"project_exists_{project_id}_{is_internal}"
        exists = cache.get(cache_key)
        
        if exists is None:
            table = "internal_project_details" if is_internal else "external_project_details"
            id_field = "intrnl_project_id" if is_internal else "project_id"
            
            try:
                project_exists = QueryExecutor.execute(
                    f"SELECT 1 FROM project_management.{table} WHERE {id_field} = %s LIMIT 1",
                    [project_id],
                    fetchone=True,
                    timeout=5000
                )
                exists = bool(project_exists)
                cache.set(cache_key, exists, CACHE_TTL_SHORT)
            except Exception as e:
                logger.warning(f"Could not verify if project {project_id} exists: {str(e)}")
                return False
        
        return exists


def clear_related_caches(patterns):
    """Clear cache keys matching the given patterns with versioning support"""
    try:
        # Get cache version
        cache_version = cache.get('cache_version', 1)
        
        # Define all possible cache key patterns
        cache_patterns = {
            'project': [
                'external_project_request_ids',
                'external_approval_ids',
                'external_project_ids',
                'project_status_values',
                'internal_project_request_ids',
                'internal_project_ids',
                'project_details_',
            ],
            'resource': [
                'employee_ids',
                'equipment_ids',
                'equipment_names',
                'department_ids',
            ],
            'cost': [
                'bom_ids',
                'budget_approval_ids',
            ]
        }
        
        # Clear matching patterns
        for pattern in patterns:
            for category, keys in cache_patterns.items():
                if pattern in category or any(pattern in key for key in keys):
                    for key in keys:
                        versioned_key = f"{key}_v{cache_version}"
                        cache.delete(versioned_key)
                        logger.debug(f"Cleared cache key: {versioned_key}")
        
        # Increment cache version if needed
        if any('project' in pattern for pattern in patterns):
            cache.set('cache_version', cache_version + 1, timeout=None)
            logger.info(f"Cache version incremented to {cache_version + 1}")
            
    except Exception as e:
        logger.warning(f"Error clearing cache: {str(e)}")


class ExternalProjectRequestView(APIView):
    """View for creating external project requests with optimized bulk operations"""
    
    @method_decorator(api_exception_handler)
    @method_decorator(log_performance)
    def post(self, request):
        start_time = time.time()
        try:
            with transaction.atomic():
                data = {
                    'ext_project_request_id': generate_id('EPR'),
                    'ext_project_name': request.data.get('ProjectName'),
                    'ext_project_description': request.data.get('ProjectDescription'),
                    'approval_id': request.data.get('ApprovalID'),
                    'item_id': request.data.get('OrderID')
                }
                
                serializer = ExternalProjectRequestSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    # Clear relevant caches
                    cache_start = time.time()
                    clear_related_caches(['external_project_request_ids', 'external_approval_ids'])
                    cache_time = (time.time() - cache_start) * 1000
                    logger.info(f"Performance: Cache clearing took {cache_time:.2f}ms")
                    
                    execution_time = (time.time() - start_time) * 1000
                    logger.info(f"Performance: ExternalProjectRequestView.post total execution time: {execution_time:.2f}ms")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Performance: ExternalProjectRequestView.post failed after {execution_time:.2f}ms - Error: {str(e)}")
            return Response(
                {'error': 'Failed to create external project request'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExternalProjectDetailsView(APIView):
    """View for creating external project details with optimized querying"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        try:
            with transaction.atomic():
                project_request_id = request.data.get('ProjectRequestID')
                project_request = get_object_or_404(ExternalProjectRequest, ext_project_request_id=project_request_id)
                
                data = {
                    'project_id': generate_id('EPD'),
                    'ext_project_request': project_request_id,
                    'project_status': request.data.get('ProjectStatus', 'Pending')
                }
                
                serializer = ExternalProjectDetailsSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    # Clear relevant caches
                    clear_related_caches(['external_project_ids', 'project_status_values'])
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating external project details: {str(e)}")
            return Response(
                {'error': 'Failed to create external project details'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExternalProjectLaborView(APIView, ValidationMixin):
    """View for adding labor to an external project with optimized validation"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        try:
            with transaction.atomic():
                logger.debug(f"Received data for adding project labor: {request.data}")
                
                project_id = request.data.get('ProjectID')
                job_role_needed = request.data.get('JobRoleNeeded')
                employee_id = request.data.get('EmployeeID')
                
                # Validate required fields
                if not project_id:
                    return Response({'error': 'ProjectID is required'}, status=status.HTTP_400_BAD_REQUEST)
                if not job_role_needed:
                    return Response({'error': 'JobRoleNeeded is required'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Validate project exists with caching
                if not self.validate_project_exists(project_id):
                    return Response(
                        {'error': f'Project with ID {project_id} not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Validate employee if provided
                if employee_id and not self.validate_employee_exists(employee_id):
                    return Response(
                        {'error': f'Employee with ID {employee_id} not found'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                labor_id = generate_id('LAB')
                
                QueryExecutor.execute(
                    """
                    INSERT INTO project_management.project_labor
                    (project_labor_id, project_id, job_role_needed, employee_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    [labor_id, project_id, job_role_needed, employee_id]
                )
                
                # Clear relevant caches
                clear_related_caches(['employee_ids'])
                
                return Response({
                    'project_labor_id': labor_id,
                    'project': project_id,
                    'job_role_needed': job_role_needed,
                    'employee_id': employee_id
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error adding project labor: {str(e)}")
            return Response(
                {'error': 'Failed to add project labor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExternalProjectEquipmentView(APIView, ValidationMixin):
    """View for adding equipment to an external project with optimized bulk operations"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        try:
            with transaction.atomic():
                project_id = request.data.get('ProjectID')
                equipment_names = request.data.get('EquipmentNames', [])
                
                if isinstance(equipment_names, str):
                    equipment_names = [equipment_names]
                
                if not self.validate_project_exists(project_id):
                    return Response(
                        {'error': f'Project with ID {project_id} not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                if not equipment_names:
                    return Response(
                        {'error': 'At least one equipment item is required'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Optimized bulk fetch with a single query
                equipment_data = QueryExecutor.execute(
                    """
                    WITH equipment_info AS (
                        SELECT e.equipment_id, e.equipment_name, pe.project_equipment_id
                        FROM production.equipment e
                        LEFT JOIN production.project_equipment pe ON e.equipment_id = pe.equipment_id
                        WHERE e.equipment_name = ANY(%s)
                    )
                    SELECT * FROM equipment_info
                    """,
                    [equipment_names],
                    fetchall=True,
                    timeout=10000
                )
                
                equipment_map = {e['equipment_name']: e for e in equipment_data}
                
                # Validate equipment
                missing_equipment = [name for name in equipment_names if name not in equipment_map]
                if missing_equipment:
                    return Response(
                        {'error': f'Equipment not found: {", ".join(missing_equipment)}'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                unavailable_equipment = [
                    name for name, eq in equipment_map.items() 
                    if not eq['project_equipment_id']
                ]
                if unavailable_equipment:
                    return Response(
                        {'error': f'Equipment not available for projects: {", ".join(unavailable_equipment)}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Bulk insert with a single query
                equipment_list_ids = [generate_id('EQL') for _ in equipment_names]
                values = [
                    (id, project_id, equipment_map[name]['project_equipment_id'])
                    for id, name in zip(equipment_list_ids, equipment_names)
                ]
                
                placeholders = ','.join(['(%s, %s, %s)'] * len(values))
                flat_values = [val for tup in values for val in tup]
                
                QueryExecutor.execute(
                    f"""
                    INSERT INTO project_management.external_project_equipments
                    (project_equipment_list_id, project_id, project_equipment_id)
                    VALUES {placeholders}
                    """,
                    flat_values,
                    timeout=10000
                )
                
                results = [
                    {
                        'project_equipment_list_id': id,
                        'project_id': project_id,
                        'equipment_name': name,
                        'project_equipment_id': equipment_map[name]['project_equipment_id']
                    }
                    for id, name in zip(equipment_list_ids, equipment_names)
                ]
                
                return Response({
                    'message': f'Successfully added {len(results)} equipment items to project',
                    'results': results
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error adding project equipment: {str(e)}")
            return Response(
                {'error': 'Failed to add project equipment'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExternalProjectWarrantyView(APIView, ValidationMixin):
    """View for adding warranty information to an external project with optimized validation"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        try:
            with transaction.atomic():
                logger.debug(f"Received warranty data: {request.data}")
                
                project_id = request.data.get('ProjectID')
                if not project_id:
                    return Response({'error': 'ProjectID is required'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Validate project exists with caching
                if not self.validate_project_exists(project_id):
                    return Response(
                        {'error': f'Project with ID {project_id} not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                warranty_coverage_yr = request.data.get('Warrantycoverageyear')
                warranty_start_date = request.data.get('Warrantystartdate')
                warranty_end_date = request.data.get('Warrantyenddate')
                
                # Validate required fields
                if not warranty_coverage_yr:
                    return Response({'error': 'Warranty coverage year is required'}, status=status.HTTP_400_BAD_REQUEST)
                if not warranty_start_date:
                    return Response({'error': 'Warranty start date is required'}, status=status.HTTP_400_BAD_REQUEST)
                if not warranty_end_date:
                    return Response({'error': 'Warranty end date is required'}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    warranty_coverage_yr = int(warranty_coverage_yr)
                except (ValueError, TypeError):
                    return Response(
                        {'error': 'Warranty coverage year must be a number'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                from datetime import datetime
                try:
                    start_date = datetime.strptime(warranty_start_date, '%Y-%m-%d').date()
                    end_date = datetime.strptime(warranty_end_date, '%Y-%m-%d').date()
                    
                    if end_date <= start_date:
                        return Response(
                            {'error': 'Warranty end date must be after warranty start date'}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except ValueError:
                    return Response(
                        {'error': 'Invalid date format. Use YYYY-MM-DD format.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                QueryExecutor.execute(
                    """
                    UPDATE project_management.external_project_details
                    SET warranty_coverage_yr = %s, 
                        warranty_start_date = %s, 
                        warranty_end_date = %s
                    WHERE project_id = %s
                    """,
                    [warranty_coverage_yr, warranty_start_date, warranty_end_date, project_id]
                )
                
                # Clear relevant caches
                clear_related_caches(['project_details_'])
                
                return Response({
                    'project_id': project_id,
                    'warranty_coverage_yr': warranty_coverage_yr,
                    'warranty_start_date': warranty_start_date,
                    'warranty_end_date': warranty_end_date,
                    'message': 'Warranty information updated successfully'
                }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating warranty information: {str(e)}")
            return Response(
                {'error': 'Failed to update warranty information'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateExternalProjectDetailsView(APIView):
    """View for updating external project details with optimized caching"""
    
    @method_decorator(api_exception_handler)
    def put(self, request, project_request_id):
        try:
            with transaction.atomic():
                logger.debug(f"Looking for project request with ID: {project_request_id}")
                
                # Get project request and details in separate queries
                project_request = ExternalProjectRequest.objects.get(ext_project_request_id=project_request_id)
                project_details = ExternalProjectDetails.objects.filter(ext_project_request=project_request).first()
                
                logger.debug(f"Found project request: {project_request.ext_project_name}")
                
                project_details_exist = bool(project_details)
                project_id = project_details.project_id if project_details_exist else None
                
                if project_details_exist:
                    logger.debug(f"Found existing project details with ID: {project_id}")
                
                new_status = request.data.get('project_status')
                
                # Validate project status
                if new_status and new_status not in PROJECT_STATUS_CHOICES:
                    return Response({
                        'error': f'Invalid project status. Must be one of: {", ".join(PROJECT_STATUS_CHOICES)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if project_details_exist:
                    # Build update query dynamically
                    update_fields = []
                    update_values = []
                    
                    if new_status:
                        update_fields.append("project_status = %s")
                        update_values.append(new_status)
                    
                    if update_fields:
                        try:
                            QueryExecutor.execute(
                                f"""
                                UPDATE project_management.external_project_details
                                SET {', '.join(update_fields)}
                                WHERE ext_project_request_id = %s
                                """,
                                update_values + [project_request_id]
                            )
                            logger.debug(f"Updated project details for request ID: {project_request_id}")
                        except Exception as e:
                            logger.error(f"Database error updating project details: {str(e)}")
                            raise
                else:
                    # Create new project details
                    new_project_id = generate_id('EPD')
                    project_id = new_project_id
                    
                    if not new_status:
                        new_status = 'not started'
                    
                    try:
                        QueryExecutor.execute(
                            """
                            INSERT INTO project_management.external_project_details
                            (project_id, ext_project_request_id, project_status)
                            VALUES (%s, %s, %s)
                            """,
                            [new_project_id, project_request_id, new_status]
                        )
                        logger.debug(f"Created new project details with ID: {new_project_id}")
                    except Exception as e:
                        logger.error(f"Database error creating project details: {str(e)}")
                        raise
                
                # Update project description if provided
                if 'project_description' in request.data and request.data['project_description']:
                    try:
                        QueryExecutor.execute(
                            """
                            UPDATE project_management.external_project_request
                            SET ext_project_description = %s
                            WHERE ext_project_request_id = %s
                            """,
                            [request.data['project_description'], project_request_id]
                        )
                        logger.debug(f"Updated project description for request ID: {project_request_id}")
                    except Exception as e:
                        logger.error(f"Database error updating project description: {str(e)}")
                        raise
                
                # Clear relevant caches
                clear_related_caches(['project_details_', 'external_project_ids', 'project_status_values'])
                
                return Response({
                    'project_id': project_id,
                    'project_request_id': project_request_id,
                    'project_status': new_status,
                    'message': 'Project details updated successfully'
                })
        except ExternalProjectRequest.DoesNotExist:
            logger.debug(f"Project request with ID {project_request_id} not found")
            return Response(
                {'error': f'Project request with ID {project_request_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating project details: {str(e)}")
            return Response(
                {'error': 'Failed to update project details'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExternalProjectCostManagementView(APIView, ValidationMixin):
    """View for adding cost management information to an external project"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        logger.debug(f"Received cost management data: {request.data}")
        
        
        project_id = request.data.get('ProjectID')
        bom_id = request.data.get('BomID')
        budget_approvals_id = request.data.get('ProjectBudgetApproval')
        
        
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if not self.validate_project_exists(project_id):
            return Response(
                {'error': f'Project with ID {project_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        
        resource_id = generate_id('RES')
        
        
        response_data = {
            'message': 'Cost management record created',
            'project_id': project_id,
            'bom_id': bom_id or 'Not specified',
            'budget_approvals_id': budget_approvals_id or 'Not specified',
            'project_resources_id': resource_id
        }
        
        
        try:
            QueryExecutor.execute(
                """
                INSERT INTO project_management.project_costs
                (project_id, bom_id, budget_approvals_id)
                VALUES (%s, %s, %s)
                """,
                [project_id, bom_id, budget_approvals_id]
            )
            logger.debug("Successfully saved cost management record")
        except Exception as e:
            logger.warning(f"Could not save cost management record: {str(e)}")
            response_data['warning'] = "Record may not have been saved to database"
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class ExternalProjectRequestsListView(APIView):
    """View for getting a list of all external project requests with optimized querying"""
    
    @method_decorator(api_exception_handler)
    @method_decorator(cache_page(CACHE_TTL_SHORT))
    def get(self, request):
        try:
            results = QueryExecutor.execute("""
                SELECT 
                    epr.ext_project_request_id AS project_request_id,
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
                WHERE 
                    epr.is_archived = false
                ORDER BY
                    epr.ext_project_request_id DESC
                LIMIT 1000
            """, fetchall=True, timeout=10000)
            
            return Response(results)
        except Exception as e:
            logger.error(f"Error fetching external project requests: {str(e)}")
            return Response(
                {'error': 'Failed to fetch external project requests'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class InternalProjectView(APIView, ValidationMixin):
    """View for creating a new internal project"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        logger.debug(f"Received data: {request.data}")
        
        # Extract data from request
        project_name = request.data.get('ProjectNameint')
        request_date = request.data.get('RequestDateint')
        starting_date = request.data.get('Startingdateint')
        employee_id = request.data.get('EmployeeIDint')
        department_id = request.data.get('DepartmentIDint')
        reason_for_request = request.data.get('ReasonForRequestint')
        materials_needed = request.data.get('MaterialsNeededint')
        equipment_needed = request.data.get('EquipmentNeededint')
        project_type = request.data.get('ProjectTypeint')
        
        # Validate required fields
        if not project_name:
            return Response({'error': 'Project name is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not request_date:
            return Response({'error': 'Request date is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate dates
        try:
            request_date_dt = datetime.strptime(request_date, '%Y-%m-%d').date()
            if starting_date:
                starting_date_dt = datetime.strptime(starting_date, '%Y-%m-%d').date()
                if starting_date_dt < request_date_dt:
                    return Response({
                        'error': 'Starting date cannot be before request date'
                    }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD format.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate employee if provided
        if employee_id and not self.validate_employee_exists(employee_id):
            return Response(
                {'error': f'Employee with ID {employee_id} not found. Please select a valid employee.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate department if provided
        if department_id:
            try:
                department_exists = QueryExecutor.execute(
                    """
                    SELECT 1 FROM human_resources.departments 
                    WHERE dept_id = %s LIMIT 1
                    """,
                    [department_id],
                    fetchone=True
                )
                if not department_exists:
                    return Response({
                        'error': f'Department with ID {department_id} not found'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error validating department: {str(e)}")
                return Response({
                    'error': 'Failed to validate department'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Validate project type
        if project_type and project_type not in INTERNAL_PROJECT_TYPES:
            return Response({
                'error': f'Invalid project type: {project_type}. Valid types are: {", ".join(INTERNAL_PROJECT_TYPES)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Insert project request (let DB trigger generate project_request_id)
                try:
                    QueryExecutor.execute(
                        """
                        INSERT INTO project_management.internal_project_request
                        (project_name, request_date, employee_id, dept_id, 
                        reason_for_request, materials_needed, equipments_needed, project_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            project_name,
                            request_date,
                            employee_id,
                            department_id,
                            reason_for_request,
                            materials_needed,
                            equipment_needed,
                            project_type
                        ]
                    )
                    logger.debug(f"Inserted internal project request for {project_name} on {request_date}")
                except Exception as e:
                    logger.error(f"Database error creating project request: {str(e)}")
                    raise
                
                # Fetch the most recent project_request_id for this project
                project_request_row = QueryExecutor.execute(
                    """
                    SELECT project_request_id 
                    FROM project_management.internal_project_request 
                    WHERE project_name = %s AND request_date = %s AND (employee_id = %s OR (%s IS NULL AND employee_id IS NULL))
                    ORDER BY project_request_id DESC LIMIT 1
                    """,
                    [project_name, request_date, employee_id, employee_id],
                    fetchone=True
                )
                if not project_request_row:
                    raise Exception("Failed to create project request")
                project_request_id = project_request_row[0]
                
                # Then, create the project details if starting date is provided
                if starting_date:
                    details_id = generate_id('IPD')
                    try:
                        QueryExecutor.execute(
                            """
                            INSERT INTO project_management.internal_project_details
                            (intrnl_project_id, project_request_id, intrnl_project_status, start_date)
                            VALUES (%s, %s, %s, %s)
                            """,
                            [details_id, project_request_id, 'not started', starting_date]
                        )
                        logger.debug(f"Created internal project details with ID: {details_id}")
                    except Exception as e:
                        logger.error(f"Database error creating project details: {str(e)}")
                        raise
                
                # Clear relevant caches
                clear_related_caches(['internal_project_request_ids', 'internal_project_ids'])
                
                return Response({
                    'project_request_id': project_request_id,
                    'project_name': project_name,
                    'message': 'Internal project request created successfully'
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creating internal project: {str(e)}")
            return Response(
                {'error': f'Failed to create internal project: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateInternalProjectDetailsView(APIView):
    """View for updating internal project details"""
    
    @method_decorator(api_exception_handler)
    def put(self, request, project_request_id):
        logger.debug(f"Updating internal project details for request ID: {project_request_id}")
        logger.debug(f"Received data: {request.data}")
        
        
        project_request = QueryExecutor.execute(
            """
            SELECT project_request_id, project_name 
            FROM project_management.internal_project_request
            WHERE project_request_id = %s
            """,
            [project_request_id],
            fetchone=True
        )
        
        if not project_request:
            return Response(
                {'error': f'Project request with ID {project_request_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        logger.debug(f"Found project request: {project_request[1]}")
        
        
        project_details = QueryExecutor.execute(
            """
            SELECT intrnl_project_id
            FROM project_management.internal_project_details
            WHERE project_request_id = %s
            """,
            [project_request_id],
            fetchone=True
        )
        
        project_details_exist = bool(project_details)
        project_id = project_details[0] if project_details_exist else None
        
        if project_details_exist:
            logger.debug(f"Found existing project details with ID: {project_id}")
        
        
        new_status = request.data.get('intrnl_project_status')
        new_approval_id = request.data.get('approval_id')
        
        if project_details_exist:
            
            update_fields = []
            update_values = []
            
            if new_status:
                update_fields.append("intrnl_project_status = %s")
                update_values.append(new_status)
            
            if new_approval_id:
                update_fields.append("approval_id = %s")
                update_values.append(new_approval_id)
            
            if update_fields:
                QueryExecutor.execute(
                    f"""
                    UPDATE project_management.internal_project_details
                    SET {', '.join(update_fields)}
                    WHERE project_request_id = %s
                    """,
                    update_values + [project_request_id]
                )
                logger.debug(f"Updated project details for request ID: {project_request_id}")
        else:
            
            new_project_id = generate_id('IPD')
            project_id = new_project_id
            
            if not new_status:
                new_status = 'not started'
            
            QueryExecutor.execute(
                """
                INSERT INTO project_management.internal_project_details
                (intrnl_project_id, project_request_id, intrnl_project_status, approval_id)
                VALUES (%s, %s, %s, %s)
                """,
                [new_project_id, project_request_id, new_status, new_approval_id]
            )
            logger.debug(f"Created new project details with ID: {new_project_id}")
        
        
        if 'project_description' in request.data and request.data['project_description']:
            QueryExecutor.execute(
                """
                UPDATE project_management.internal_project_request
                SET reason_for_request = %s
                WHERE project_request_id = %s
                """,
                [request.data['project_description'], project_request_id]
            )
            logger.debug(f"Updated project description for request ID: {project_request_id}")
        
        
        return Response({
            'intrnl_project_id': project_id,
            'project_request_id': project_request_id,
            'intrnl_project_status': new_status,
            'approval_id': new_approval_id,
            'message': 'Project details updated successfully'
        })


class InternalProjectLaborView(APIView, ValidationMixin):
    """View for adding labor to an internal project"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        logger.debug(f"Adding internal project labor with data: {request.data}")
        
        project_id = request.data.get('Projectidint')
        job_role = request.data.get('Jobroleint')
        employee_id = request.data.get('EmployeeIDint')
        
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not job_role:
            return Response({'error': 'Job role is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if not self.validate_project_exists(project_id, is_internal=True):
            return Response(
                {'error': f'Project with ID {project_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        
        if employee_id and not self.validate_employee_exists(employee_id):
            return Response(
                {'error': f'Employee with ID {employee_id} not found. Please select a valid employee.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        labor_id = generate_id('LAB')
        
        QueryExecutor.execute(
            """
            INSERT INTO project_management.project_labor
            (project_labor_id, intrnl_project_id, job_role_needed, employee_id)
            VALUES (%s, %s, %s, %s)
            """,
            [labor_id, project_id, job_role, employee_id]
        )
        
        logger.debug(f"Inserted internal project labor with ID: {labor_id}")
        
        return Response({
            'project_labor_id': labor_id,
            'intrnl_project_id': project_id,
            'job_role_needed': job_role,
            'employee_id': employee_id,
            'message': 'Internal project labor added successfully'
        }, status=status.HTTP_201_CREATED)


class InternalProjectRequestsListView(APIView):
    """View for getting a list of all internal project requests with optimized querying"""
    
    @method_decorator(api_exception_handler)
    @method_decorator(cache_page(CACHE_TTL_SHORT))
    def get(self, request):
        try:
            results = QueryExecutor.execute("""
                SELECT 
                    ipr.project_request_id,
                    ipr.project_name,
                    COALESCE(ipd.approval_id, 'N/A') AS approval_id,
                    ipr.request_date,
                    ipr.employee_id,
                    ipr.dept_id,
                    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
                    d.dept_name,
                    COALESCE(ipd.intrnl_project_status, 'not started') AS project_status
                FROM 
                    project_management.internal_project_request ipr
                LEFT JOIN 
                    project_management.internal_project_details ipd 
                    ON ipr.project_request_id = ipd.project_request_id
                LEFT JOIN 
                    human_resources.employees e 
                    ON ipr.employee_id = e.employee_id
                LEFT JOIN 
                    human_resources.departments d 
                    ON ipr.dept_id = d.dept_id
                WHERE 
                    ipr.is_archived = false
                ORDER BY
                    ipr.request_date DESC
                LIMIT 1000
            """, fetchall=True, timeout=10000)
            
            for result in results:
                result['employee'] = result.pop('employee_name', 'Unknown')
                result['department'] = result.pop('dept_name', 'Unknown')
                result['project_status'] = result.get('project_status', 'not started').replace('_', ' ').title()
            
            return Response(results)
        except Exception as e:
            logger.error(f"Error fetching internal project requests: {str(e)}")
            return Response(
                {'error': 'Failed to fetch internal project requests'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class CachedListView(APIView):
    """Base class for views that return cached lists with optimized caching"""
    
    cache_key = None
    cache_timeout = CACHE_TTL_SHORT
    
    def get_data(self):
        """Override this method to provide the actual data"""
        raise NotImplementedError
    
    @method_decorator(api_exception_handler)
    @method_decorator(cache_page(CACHE_TTL_SHORT))
    def get(self, request):
        if not self.cache_key:
            raise ValueError("cache_key must be set")
        
        try:
            data = self.get_data()
            return Response(data)
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}.get_data: {str(e)}")
            return Response(
                {'error': 'Failed to fetch data'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EquipmentNamesView(CachedListView):
    """View for getting a list of all equipment names and IDs"""
    
    cache_key = "equipment_names"
    
    def get_data(self):
        try:
            equipment = QueryExecutor.execute("""
                SELECT equipment_id, equipment_name 
                FROM production.equipment
                ORDER BY equipment_name
            """, fetchall=True)
            
            return [{"id": item['equipment_id'], "name": item['equipment_name']} for item in equipment]
        except Exception as e:
            logger.warning(f"Could not query equipment: {str(e)}")
            # Return some mock data if the query fails
            return [
                {"id": "EQ-001", "name": "Drill Machine"},
                {"id": "EQ-002", "name": "Welding Equipment"},
                {"id": "EQ-003", "name": "Forklift"},
                {"id": "EQ-004", "name": "Concrete Mixer"},
                {"id": "EQ-005", "name": "Excavator"}
            ]


class ExternalApprovalIdsView(CachedListView):
    """View for getting a list of all external approval IDs"""
    
    cache_key = "external_approval_ids"
    
    def get_data(self):
        approval_ids = QueryExecutor.execute("""
            SELECT DISTINCT approval_id 
            FROM project_management.external_project_request
            WHERE approval_id IS NOT NULL
        """, fetchall=True)
        
        return [row['approval_id'] for row in approval_ids]


class InternalApprovalIdsView(CachedListView):
    """View for getting a list of all internal approval IDs"""
    
    cache_key = "internal_approval_ids"
    
    def get_data(self):
        approval_ids = []
        
        
        internal_ids = QueryExecutor.execute("""
            SELECT DISTINCT approval_id 
            FROM project_management.internal_project_details
            WHERE approval_id IS NOT NULL
        """, fetchall=True)
        
        approval_ids.extend([row['approval_id'] for row in internal_ids])
        
        
        try:
            management_ids = QueryExecutor.execute("""
                SELECT DISTINCT approval_id 
                FROM management.management_approvals
                WHERE approval_id IS NOT NULL
            """, fetchall=True)
            
            approval_ids.extend([row['approval_id'] for row in management_ids])
        except Exception as e:
            logger.warning(f"Could not query management.management_approvals: {str(e)}")
        
        
        return sorted(list(set(approval_ids)))


class OrderIdsView(CachedListView):
    """View for getting a list of all order IDs"""
    
    cache_key = "order_ids"
    
    def get_data(self):
        order_ids = list(ExternalProjectRequest.objects.values_list('item_id', flat=True).distinct())
        return [id for id in order_ids if id]


class ExternalProjectRequestIdsView(CachedListView):
    """View for getting a list of all external project request IDs and names"""
    
    cache_key = "external_project_request_ids"
    
    def get_data(self):
        return [
            {"id": obj["ext_project_request_id"], "name": obj["ext_project_name"]}
            for obj in ExternalProjectRequest.objects.values("ext_project_request_id", "ext_project_name")
        ]


class ExternalProjectIdsView(CachedListView):
    """View for getting a list of all external project IDs and names"""
    
    cache_key = "external_project_ids"
    
    def get_data(self):
        try:
            projects = QueryExecutor.execute("""
                SELECT epd.project_id, epr.ext_project_name
                FROM project_management.external_project_details epd
                JOIN project_management.external_project_request epr 
                    ON epd.ext_project_request_id = epr.ext_project_request_id
                ORDER BY epr.ext_project_name
            """, fetchall=True)
            
            return [{
                "id": proj['project_id'],
                "name": proj['ext_project_name']
            } for proj in projects]
        except Exception as e:
            logger.warning(f"Could not query external projects: {str(e)}")
            return []


class EmployeeIdsView(CachedListView):
    """View for getting a list of all employee IDs and names"""
    
    cache_key = "employee_ids"
    
    def get_data(self):
        try:
            employees = QueryExecutor.execute("""
                SELECT employee_id, first_name, last_name 
                FROM human_resources.employees 
                WHERE employee_id IS NOT NULL
            """, fetchall=True)
            if employees:
                return [{
                    "id": emp['employee_id'], 
                    "name": f"{emp['employee_id']} - {emp['first_name']} {emp['last_name']}"
                } for emp in employees]
            # If no employees, return empty list
            return []
        except Exception as e:
            logger.warning(f"Could not query employees: {str(e)}")
            # Only return mock data if there was a query error
            return [
                {"id": "EMP-001", "name": "EMP-001 - John Doe"},
                {"id": "EMP-002", "name": "EMP-002 - Jane Smith"},
                {"id": "EMP-003", "name": "EMP-003 - Michael Johnson"}
            ]


class EquipmentIdsView(CachedListView):
    """View for getting a list of all equipment IDs"""
    
    cache_key = "equipment_ids"
    
    def get_data(self):
        ids = list(ExternalProjectEquipments.objects.values_list('project_equipment_id', flat=True).distinct())
        return [id for id in ids if id]


class InternalProjectRequestIdsView(CachedListView):
    """View for getting a list of all internal project request IDs and names"""
    
    cache_key = "internal_project_request_ids"
    
    def get_data(self):
        return [
            {"id": obj["project_request_id"], "name": obj["project_name"]}
            for obj in InternalProjectRequest.objects.values("project_request_id", "project_name")
        ]


class InternalProjectIdsView(CachedListView):
    """View for getting a list of all internal project IDs and names"""
    
    cache_key = "internal_project_ids"
    
    def get_data(self):
        try:
            projects = QueryExecutor.execute("""
                SELECT ipd.intrnl_project_id, ipr.project_name
                FROM project_management.internal_project_details ipd
                JOIN project_management.internal_project_request ipr 
                    ON ipd.project_request_id = ipr.project_request_id
                ORDER BY ipr.project_name
            """, fetchall=True)
            
            return [{
                "id": proj['intrnl_project_id'],
                "name": proj['project_name']
            } for proj in projects]
        except Exception as e:
            logger.warning(f"Could not query internal projects: {str(e)}")
            return []


class DepartmentIdsView(CachedListView):
    """View for getting a list of all department IDs and names"""
    
    cache_key = "department_ids"
    
    def get_data(self):
        try:
            departments = QueryExecutor.execute("""
                SELECT dept_id, dept_name 
                FROM human_resources.departments 
                WHERE dept_id IS NOT NULL
                ORDER BY dept_name
            """, fetchall=True)
            if departments:
                return [{
                    "id": dept['dept_id'],
                    "name": dept['dept_name']
                } for dept in departments]
            # If no departments, return empty list
            return []
        except Exception as e:
            logger.warning(f"Could not query departments: {str(e)}")
            # Only return mock data if there was a query error
            return []


class ProjectStatusValuesView(CachedListView):
    """View for getting a list of all possible project status values"""
    
    cache_key = "project_status_values"
    cache_timeout = 3600  
    
    def get_data(self):
        try:
            enum_values = QueryExecutor.execute("SELECT enum_range(NULL::project_status)", fetchone=True)
            if enum_values and enum_values[0]:
                enum_values = enum_values[0].replace('{', '').replace('}', '').split(',')
                return [val.strip('"') for val in enum_values]
        except Exception:
            pass
        
        
        return ['not started', 'in progress', 'completed']


class InternalProjectStatusValuesView(CachedListView):
    """View for getting a list of all possible internal project status values"""
    
    cache_key = "internal_project_status_values"
    cache_timeout = 3600  
    
    def get_data(self):
        try:
            enum_values = QueryExecutor.execute("SELECT enum_range(NULL::intrnl_project_status)", fetchone=True)
            if enum_values and enum_values[0]:
                enum_values = enum_values[0].replace('{', '').replace('}', '').split(',')
                return [val.strip('"') for val in enum_values]
        except Exception:
            pass
        
        
        return ['not started', 'in progress', 'completed']


class BomIdsView(CachedListView):
    """View for getting a list of all BOM IDs from cost management"""
    
    cache_key = "bom_ids"
    
    def get_data(self):
        bom_ids = QueryExecutor.execute("""
            SELECT DISTINCT bom_id
            FROM project_management.project_costs
            WHERE bom_id IS NOT NULL
        """, fetchall=True)
        
        return [row['bom_id'] for row in bom_ids]


class BudgetApprovalIdsView(CachedListView):
    """View for getting a list of all budget approval IDs from cost management"""
    
    cache_key = "budget_approval_ids"
    
    def get_data(self):
        budget_ids = QueryExecutor.execute("""
            SELECT DISTINCT budget_approvals_id
            FROM project_management.project_costs
            WHERE budget_approvals_id IS NOT NULL
        """, fetchall=True)
        
        return [row['budget_approvals_id'] for row in budget_ids]


class ClearCacheView(APIView):
    """View for clearing the application cache"""
    
    @method_decorator(api_exception_handler)
    def get(self, request):
        cache.clear()
        return Response({'message': 'Cache cleared successfully'})


def rate_limit(limit=100, period=60):
    """Decorator to implement rate limiting on API endpoints"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(',')[0]
            else:
                client_ip = request.META.get('REMOTE_ADDR')
            
            # Create rate limit key
            rate_key = f"rate_limit_{client_ip}_{func.__name__}"
            
            # Get current count
            current = cache.get(rate_key, 0)
            
            if current >= limit:
                logger.warning(f"Rate limit exceeded for {client_ip} on {func.__name__}")
                return Response(
                    {'error': 'Rate limit exceeded', 'type': 'rate_limit'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Increment counter
            cache.set(rate_key, current + 1, period)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


@api_view(['POST'])
@api_exception_handler
def create_external_project_request(request):
    return ExternalProjectRequestView().post(request)

@api_view(['POST'])
@api_exception_handler
def create_external_project_details(request):
    return ExternalProjectDetailsView().post(request)

@api_view(['POST'])
@api_exception_handler
def add_external_project_labor(request):
    return ExternalProjectLaborView().post(request)

@api_view(['POST'])
@api_exception_handler
def add_external_project_equipment(request):
    return ExternalProjectEquipmentView().post(request)

@api_view(['POST'])
@api_exception_handler
def add_external_project_warranty(request):
    return ExternalProjectWarrantyView().post(request)

@api_view(['PUT'])
@api_exception_handler
def update_external_project_details(request, project_request_id):
    return UpdateExternalProjectDetailsView().put(request, project_request_id)

@api_view(['POST'])
@api_exception_handler
def add_external_project_cost_management(request):
    return ExternalProjectCostManagementView().post(request)

@api_view(['GET'])
@api_exception_handler
def get_external_project_requests_list(request):
    return ExternalProjectRequestsListView().get(request)


@api_view(['POST'])
@api_exception_handler
def create_internal_project(request):
    return InternalProjectView().post(request)

@api_view(['PUT'])
@api_exception_handler
def update_internal_project_details(request, project_request_id):
    return UpdateInternalProjectDetailsView().put(request, project_request_id)

@api_view(['POST'])
@api_exception_handler
def add_internal_project_labor(request):
    return InternalProjectLaborView().post(request)

@api_view(['GET'])
@api_exception_handler
def get_internal_project_requests_list(request):
    return InternalProjectRequestsListView().get(request)


@api_view(['GET'])
@api_exception_handler
def get_external_approval_ids(request):
    return ExternalApprovalIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_internal_approval_ids(request):
    return InternalApprovalIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_approval_ids(request):
    return ExternalApprovalIdsView().get(request)  

@api_view(['GET'])
@api_exception_handler
def get_order_ids(request):
    return OrderIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_external_project_request_ids(request):
    return ExternalProjectRequestIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_external_project_ids(request):
    return ExternalProjectIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_employee_ids(request):
    return EmployeeIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_equipment_ids(request):
    return EquipmentIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_equipment_names(request):
    return EquipmentNamesView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_internal_project_request_ids(request):
    return InternalProjectRequestIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_internal_project_ids(request):
    return InternalProjectIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_department_ids(request):
    return DepartmentIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_project_status_values(request):
    return ProjectStatusValuesView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_internal_project_status_values(request):
    return InternalProjectStatusValuesView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_bom_ids_from_cost_management(request):
    return BomIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def get_budget_approval_ids_from_cost_management(request):
    return BudgetApprovalIdsView().get(request)

@api_view(['GET'])
@api_exception_handler
def clear_cache(request):
    return ClearCacheView().get(request)

class PaginatedListView(APIView):
    """Base class for views that return paginated lists"""
    
    page_size = 20
    max_page_size = 100
    
    def get_pagination_params(self, request):
        """Get pagination parameters from request"""
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', self.page_size))
            
            # Validate page size
            if page_size > self.max_page_size:
                page_size = self.max_page_size
            if page_size < 1:
                page_size = self.page_size
                
            return page, page_size
        except ValueError:
            return 1, self.page_size
    
    def paginate_results(self, results, page, page_size):
        """Paginate the results"""
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        total_count = len(results)
        paginated_results = results[start_idx:end_idx]
        
        return {
            'results': paginated_results,
            'pagination': {
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }