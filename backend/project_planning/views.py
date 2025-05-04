from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import connection
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import uuid
import logging
from functools import wraps

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


logger = logging.getLogger(__name__)



def generate_id(prefix):
    """Generate a unique ID with the given prefix"""
    unique_id = uuid.uuid4().hex[:6].upper()
    from datetime import datetime
    year = datetime.now().year
    return f"PROJ-{prefix}-{year}-{unique_id}"


def api_exception_handler(func):
    """Decorator to handle exceptions in API views"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper


class QueryExecutor:
    """Class to execute database queries with proper error handling"""
    
    @staticmethod
    def execute(query, params=None, fetchone=False, fetchall=False):
        """Execute a database query with proper error handling"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or [])
                
                if fetchone:
                    return cursor.fetchone()
                elif fetchall:
                    columns = [col[0] for col in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                return True
        except Exception as e:
            logger.exception(f"Database query error: {str(e)}")
            raise


class ValidationMixin:
    """Mixin for common validation tasks"""
    
    @staticmethod
    def validate_employee_exists(employee_id):
        """Validate that an employee exists in the database"""
        if not employee_id:
            return True  
        
        cache_key = f"employee_exists_{employee_id}"
        exists = cache.get(cache_key)
        
        if exists is None:
            try:
                employee_exists = QueryExecutor.execute(
                    "SELECT COUNT(*) FROM human_resources.employees WHERE employee_id = %s",
                    [employee_id],
                    fetchone=True
                )
                exists = employee_exists and employee_exists[0] > 0
                cache.set(cache_key, exists, 300)  
            except Exception:
                
                logger.warning(f"Could not verify if employee {employee_id} exists")
                return True
        
        return exists
    
    @staticmethod
    def validate_project_exists(project_id, is_internal=False):
        """Validate that a project exists in the database"""
        if not project_id:
            return False
        
        table = "internal_project_details" if is_internal else "external_project_details"
        id_field = "intrnl_project_id" if is_internal else "project_id"
        
        try:
            project_exists = QueryExecutor.execute(
                f"SELECT COUNT(*) FROM project_management.{table} WHERE {id_field} = %s",
                [project_id],
                fetchone=True
            )
            return project_exists and project_exists[0] > 0
        except Exception as e:
            logger.warning(f"Could not verify if project {project_id} exists: {str(e)}")
            return False




class ExternalProjectRequestView(APIView):
    """View for creating external project requests"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExternalProjectDetailsView(APIView):
    """View for creating external project details"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExternalProjectLaborView(APIView, ValidationMixin):
    """View for adding labor to an external project"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        logger.debug(f"Received data for adding project labor: {request.data}")
        
        project_id = request.data.get('ProjectID')
        job_role_needed = request.data.get('JobRoleNeeded')
        employee_id = request.data.get('EmployeeID')
        
        
        if not project_id:
            return Response({'error': 'ProjectID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not job_role_needed:
            return Response({'error': 'JobRoleNeeded is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if not self.validate_project_exists(project_id):
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
            (project_labor_id, project_id, job_role_needed, employee_id)
            VALUES (%s, %s, %s, %s)
            """,
            [labor_id, project_id, job_role_needed, employee_id]
        )
        
        return Response({
            'project_labor_id': labor_id,
            'project': project_id,
            'job_role_needed': job_role_needed,
            'employee_id': employee_id
        }, status=status.HTTP_201_CREATED)


class ExternalProjectEquipmentView(APIView, ValidationMixin):
    """View for adding equipment to an external project"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        project_id = request.data.get('ProjectID')
        equipment_names = request.data.get('EquipmentNames', [])
        
        # Ensure equipment_names is a list
        if isinstance(equipment_names, str):
            equipment_names = [equipment_names]
        
        # Validate project exists
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
        
        results = []
        
        for equipment_name in equipment_names:
            # First, get the equipment_id from the equipment name
            equipment = QueryExecutor.execute(
                """
                SELECT equipment_id 
                FROM production.equipment 
                WHERE equipment_name = %s
                """,
                [equipment_name],
                fetchone=True
            )
            
            if not equipment:
                return Response(
                    {'error': f'Equipment with name "{equipment_name}" not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            equipment_id = equipment[0]
            
            # Then, find the corresponding project_equipment_id
            project_equipment = QueryExecutor.execute(
                """
                SELECT project_equipment_id 
                FROM production.project_equipment 
                WHERE equipment_id = %s
                """,
                [equipment_id],
                fetchone=True
            )
            
            if not project_equipment:
                return Response(
                    {'error': f'Equipment "{equipment_name}" (ID: {equipment_id}) is not available for projects. It needs to be added to the project equipment list first.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            project_equipment_id = project_equipment[0]
            
            # Create equipment assignment using the correct table name and ID
            equipment_list_id = generate_id('EQL')
            
            QueryExecutor.execute(
                """
                INSERT INTO project_management.external_project_equipments
                (project_equipment_list_id, project_id, project_equipment_id)
                VALUES (%s, %s, %s)
                """,
                [equipment_list_id, project_id, project_equipment_id]
            )
            
            results.append({
                'project_equipment_list_id': equipment_list_id,
                'project_id': project_id,
                'equipment_name': equipment_name,
                'project_equipment_id': project_equipment_id
            })
        
        return Response({
            'message': f'Successfully added {len(results)} equipment items to project',
            'results': results
        }, status=status.HTTP_201_CREATED)

class ExternalProjectWarrantyView(APIView, ValidationMixin):
    """View for adding warranty information to an external project"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        logger.debug(f"Received warranty data: {request.data}")
        
        project_id = request.data.get('ProjectID')
        if not project_id:
            return Response({'error': 'ProjectID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if not self.validate_project_exists(project_id):
            return Response(
                {'error': f'Project with ID {project_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        
        warranty_coverage_yr = request.data.get('Warrantycoverageyear')
        warranty_start_date = request.data.get('Warrantystartdate')
        warranty_end_date = request.data.get('Warrantyenddate')
        
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
        
        return Response({
            'project_id': project_id,
            'warranty_coverage_yr': warranty_coverage_yr,
            'warranty_start_date': warranty_start_date,
            'warranty_end_date': warranty_end_date,
            'message': 'Warranty information updated successfully'
        }, status=status.HTTP_200_OK)


class UpdateExternalProjectDetailsView(APIView):
    """View for updating external project details"""
    
    @method_decorator(api_exception_handler)
    def put(self, request, project_request_id):
        logger.debug(f"Looking for project request with ID: {project_request_id}")
        
        try:
            project_request = ExternalProjectRequest.objects.get(ext_project_request_id=project_request_id)
            logger.debug(f"Found project request: {project_request.ext_project_name}")
        except ExternalProjectRequest.DoesNotExist:
            logger.debug(f"Project request with ID {project_request_id} not found")
            return Response(
                {'error': f'Project request with ID {project_request_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            project_details = ExternalProjectDetails.objects.filter(ext_project_request_id=project_request_id).first()
            if project_details:
                logger.debug(f"Found project details with ID: {project_details.project_id}")
            else:
                logger.debug(f"No project details found for request ID: {project_request_id}")
                new_project_id = generate_id('EPD')
                logger.debug(f"Creating new project details with ID: {new_project_id}")
                project_details = ExternalProjectDetails(
                    project_id=new_project_id,
                    ext_project_request_id=project_request_id,
                    project_status='Pending'
                )
        except Exception as e:
            logger.exception(f"Error finding/creating project details: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            if 'project_status' in request.data:
                logger.debug(f"Updating project status to: {request.data['project_status']}")
                project_details.project_status = request.data['project_status']
                project_details.save()
        except Exception as e:
            logger.exception(f"Error updating project status: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'project_id': project_details.project_id,
            'ext_project_request_id': project_request_id,
            'project_status': project_details.project_status
        })


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
    """View for getting a list of all external project requests"""
    
    @method_decorator(api_exception_handler)
    @method_decorator(cache_page(60))  
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
                ORDER BY
                    epr.ext_project_request_id DESC
            """, fetchall=True)
            
            return Response(results)
        except Exception as e:
            logger.warning(f"Error getting external project requests with join: {str(e)}")
            
            results = QueryExecutor.execute("""
                SELECT 
                    ext_project_request_id AS project_request_id,
                    ext_project_name AS project_name,
                    approval_id,
                    item_id
                FROM 
                    project_management.external_project_request
                ORDER BY
                    ext_project_request_id DESC
            """, fetchall=True)
            
            
            for result in results:
                result['start_date'] = None
                result['project_status'] = None
            
            return Response(results)




class InternalProjectView(APIView, ValidationMixin):
    """View for creating a new internal project"""
    
    @method_decorator(api_exception_handler)
    def post(self, request):
        logger.debug(f"Received data: {request.data}")
        
        
        project_name = request.data.get('ProjectNameint')
        request_date = request.data.get('RequestDateint')
        starting_date = request.data.get('Startingdateint')
        employee_id = request.data.get('EmployeeIDint')
        department_id = request.data.get('DepartmentIDint')
        reason_for_request = request.data.get('ReasonForRequestint')
        materials_needed = request.data.get('MaterialsNeededint')
        equipment_needed = request.data.get('EquipmentNeededint')
        project_type = request.data.get('ProjectTypeint')
        
        
        if not project_name:
            return Response({'error': 'Project name is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not request_date:
            return Response({'error': 'Request date is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if employee_id and not self.validate_employee_exists(employee_id):
            return Response(
                {'error': f'Employee with ID {employee_id} not found. Please select a valid employee.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
        valid_project_types = ["Training Program", "Department Event", "Facility Maintenance"]
        
        
        if project_type and project_type not in valid_project_types:
            return Response({
                'error': f'Invalid project type: {project_type}. Valid types are: {valid_project_types}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
        project_request_id = generate_id('IPR')
        
        
        QueryExecutor.execute(
            """
            INSERT INTO project_management.internal_project_request
            (project_request_id, project_name, request_date, employee_id, dept_id, 
            reason_for_request, materials_needed, equipments_needed, project_type, is_archived)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                project_request_id, 
                project_name,
                request_date,
                employee_id,
                department_id,
                reason_for_request,
                materials_needed,
                equipment_needed,
                project_type,
                False
            ]
        )
        
        logger.debug(f"Created internal project request with ID: {project_request_id}")
        
        
        if starting_date:
            try:
                details_id = generate_id('IPD')
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
                logger.warning(f"Error creating project details: {str(e)}")
                
        
        
        return Response({
            'project_request_id': project_request_id,
            'project_name': project_name,
            'message': 'Internal project request created successfully'
        }, status=status.HTTP_201_CREATED)


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
    """View for getting a list of all internal project requests"""
    
    @method_decorator(api_exception_handler)
    @method_decorator(cache_page(60))  
    def get(self, request):
        try:
            
            enum_values = QueryExecutor.execute(
                "SELECT enum_range(NULL::intrnl_project_status)",
                fetchone=True
            )
            
            if enum_values and enum_values[0]:
                enum_values = enum_values[0].replace('{', '').replace('}', '').split(',')
                enum_values = [val.strip('"') for val in enum_values]
                default_status = enum_values[0] if enum_values else 'not started'
            else:
                default_status = 'not started'
            
            logger.debug(f"Valid project status values: {enum_values}")
            
            
            results = QueryExecutor.execute(f"""
                SELECT 
                    ipr.project_request_id,
                    ipr.project_name,
                    COALESCE(ipd.approval_id, 'N/A') AS approval_id,
                    ipr.request_date,
                    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
                    d.dept_name,
                    COALESCE(ipd.intrnl_project_status, '{default_status}') AS project_status
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
                ORDER BY
                    ipr.request_date DESC
            """, fetchall=True)
            
            
            for result in results:
                if not result.get('employee_name'):
                    result['employee_name'] = 'Unknown'
                
                if not result.get('dept_name'):
                    result['dept_name'] = 'Unknown'
                
                
                if result.get('approval_id') is None:
                    result['approval_id'] = 'N/A'
                
                
                status = result.get('project_status', default_status)
                result['project_status'] = status.replace('_', ' ').title()
                
                
                result['employee'] = result.pop('employee_name')
                result['department'] = result.pop('dept_name')
            
            return Response(results)
        except Exception as e:
            logger.warning(f"Error getting internal project requests with join: {str(e)}")
            
            basic_results = QueryExecutor.execute("""
                SELECT 
                    project_request_id,
                    project_name,
                    request_date,
                    employee_id,
                    dept_id
                FROM 
                    project_management.internal_project_request
                ORDER BY
                    request_date DESC
            """, fetchall=True)
            
            
            for result in basic_results:
                result['approval_id'] = 'N/A'
                result['employee'] = result.get('employee_id', 'Unknown')
                result['department'] = result.get('dept_id', 'Unknown')
                result['project_status'] = 'Not Started'
                
                
                if 'employee_id' in result:
                    del result['employee_id']
                if 'dept_id' in result:
                    del result['dept_id']
            
            return Response(basic_results)




class CachedListView(APIView):
    """Base class for views that return cached lists"""
    
    cache_key = None
    cache_timeout = 300  
    
    def get_data(self):
        """Override this method to provide the actual data"""
        raise NotImplementedError
    
    @method_decorator(api_exception_handler)
    def get(self, request):
        if not self.cache_key:
            raise ValueError("cache_key must be set")
            
        cached_data = cache.get(self.cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        data = self.get_data()
        cache.set(self.cache_key, data, self.cache_timeout)
        return Response(data)


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
    """View for getting a list of all external project request IDs"""
    
    cache_key = "external_project_request_ids"
    
    def get_data(self):
        return list(ExternalProjectRequest.objects.values_list('ext_project_request_id', flat=True))


class ExternalProjectIdsView(CachedListView):
    """View for getting a list of all external project IDs"""
    
    cache_key = "external_project_ids"
    
    def get_data(self):
        return list(ExternalProjectDetails.objects.values_list('project_id', flat=True))


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
                    "name": f"{emp['first_name']} {emp['last_name']}"
                } for emp in employees]
            
            
            employees = QueryExecutor.execute("""
                SELECT DISTINCT pl.employee_id, e.first_name, e.last_name
                FROM project_management.project_labor pl
                JOIN human_resources.employees e ON pl.employee_id = e.employee_id
                WHERE pl.employee_id IS NOT NULL
            """, fetchall=True)
            
            if employees:
                return [{
                    "id": emp['employee_id'], 
                    "name": f"{emp['first_name']} {emp['last_name']}"
                } for emp in employees]
        except Exception as e:
            logger.warning(f"Could not query employees: {str(e)}")
        
        
        return [
            {"id": "EMP-001", "name": "John Doe"},
            {"id": "EMP-002", "name": "Jane Smith"},
            {"id": "EMP-003", "name": "Michael Johnson"}
        ]


class EquipmentIdsView(CachedListView):
    """View for getting a list of all equipment IDs"""
    
    cache_key = "equipment_ids"
    
    def get_data(self):
        ids = list(ExternalProjectEquipments.objects.values_list('project_equipment_id', flat=True).distinct())
        return [id for id in ids if id]


class InternalProjectRequestIdsView(CachedListView):
    """View for getting a list of all internal project request IDs"""
    
    cache_key = "internal_project_request_ids"
    
    def get_data(self):
        return list(InternalProjectRequest.objects.values_list('project_request_id', flat=True))


class InternalProjectIdsView(CachedListView):
    """View for getting a list of all internal project IDs"""
    
    cache_key = "internal_project_ids"
    
    def get_data(self):
        return list(InternalProjectDetails.objects.values_list('intrnl_project_id', flat=True))


class DepartmentIdsView(CachedListView):
    """View for getting a list of all department IDs"""
    
    cache_key = "department_ids"
    
    def get_data(self):
        ids = list(InternalProjectRequest.objects.values_list('dept_id', flat=True).distinct())
        return [id for id in ids if id]


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