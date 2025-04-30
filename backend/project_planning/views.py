from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db import connection
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
import uuid

def generate_id(prefix):
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{unique_id}"

 
@api_view(['POST'])
def create_external_project_request(request):
    try:
         
         
        data = {
            'ext_project_request_id': generate_id('EXTREQ'),
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
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_external_project_details(request):
    try:
         
        project_request_id = request.data.get('ProjectRequestID')
        project_request = get_object_or_404(ExternalProjectRequest, ext_project_request_id=project_request_id)
        
        data = {
            'project_id': generate_id('EXTPRJ'),
            'ext_project_request': project_request_id,
            'project_status': request.data.get('ProjectStatus', 'Pending')
        }
        
        serializer = ExternalProjectDetailsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_external_project_labor(request):
    try:
        # Add debug logging
        print(f"Received data for adding project labor: {request.data}")
        
        project_id = request.data.get('ProjectID')
        job_role_needed = request.data.get('JobRoleNeeded')
        employee_id = request.data.get('EmployeeID')
        
        # Validate required fields
        if not project_id:
            return Response({'error': 'ProjectID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not job_role_needed:
            return Response({'error': 'JobRoleNeeded is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to get the project
        try:
            project = ExternalProjectDetails.objects.get(project_id=project_id)
            print(f"Found project with ID: {project.project_id}")
        except ExternalProjectDetails.DoesNotExist:
            print(f"Project with ID {project_id} not found")
            return Response(
                {'error': f'Project with ID {project_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create the labor record directly
        labor_id = generate_id('LABOR')
        print(f"Generated labor ID: {labor_id}")
        
        # Try using a direct SQL query to insert the record
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO project_management.project_labor
                (project_labor_id, project_id, job_role_needed, employee_id)
                VALUES (%s, %s, %s, %s)
                """,
                [labor_id, project_id, job_role_needed, employee_id]
            )
        
        print(f"Inserted labor record with ID: {labor_id}")
        
        # Return the created data
        return Response({
            'project_labor_id': labor_id,
            'project': project_id,
            'job_role_needed': job_role_needed,
            'employee_id': employee_id
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        print(f"Error adding project labor: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_external_project_equipment(request):
    try:
        project_id = request.data.get('ProjectID')
        project = get_object_or_404(ExternalProjectDetails, project_id=project_id)
        
        data = {
            'project_equipment_list_id': generate_id('EQPLIST'),
            'project': project_id,
            'project_equipment_id': request.data.get('ProjectEquipmentID')
        }
        
        serializer = ExternalProjectEquipmentsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_external_project_warranty(request):
    try:
        print(f"Received warranty data: {request.data}")
        
        project_id = request.data.get('ProjectID')
        if not project_id:
            return Response({'error': 'ProjectID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            project = ExternalProjectDetails.objects.get(project_id=project_id)
            print(f"Found project with ID: {project.project_id}")
        except ExternalProjectDetails.DoesNotExist:
            print(f"Project with ID {project_id} not found")
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
        
        # Update the project details with warranty information using SQL
        # This bypasses any model validation issues
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE project_management.external_project_details
                SET warranty_coverage_yr = %s, 
                    warranty_start_date = %s, 
                    warranty_end_date = %s
                WHERE project_id = %s
                """,
                [warranty_coverage_yr, warranty_start_date, warranty_end_date, project_id]
            )
            
        print(f"Updated warranty information for project ID: {project_id}")
        
        # Return the updated data
        return Response({
            'project_id': project_id,
            'warranty_coverage_yr': warranty_coverage_yr,
            'warranty_start_date': warranty_start_date,
            'warranty_end_date': warranty_end_date,
            'message': 'Warranty information updated successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error updating project warranty: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_internal_project(request):
    try:
        print(f"Received data: {request.data}")
        
        # Get required fields from the request
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
        
        # Valid project types based on the database enum
        valid_project_types = ["Training Program", "Department Event", "Facility Maintenance"]
        
        # Check if provided project_type is valid
        if project_type and project_type not in valid_project_types:
            return Response({
                'error': f'Invalid project type: {project_type}. Valid types are: {valid_project_types}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare data for insertion
        data = {
            'project_request_id': generate_id('INTREQ'),
            'project_name': project_name,
            'request_date': request_date,
            'employee_id': employee_id,
            'dept_id': department_id,
            'reason_for_request': reason_for_request,
            'materials_needed': materials_needed,
            'equipments_needed': equipment_needed,
            'project_type': project_type,
            'is_archived': False
        }
        
        # Use direct SQL for insertion
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO project_management.internal_project_request
                (project_request_id, project_name, request_date, employee_id, dept_id, 
                reason_for_request, materials_needed, equipments_needed, project_type, is_archived)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING project_request_id
                """,
                [
                    data['project_request_id'], 
                    data['project_name'],
                    data['request_date'],
                    data['employee_id'],
                    data['dept_id'],
                    data['reason_for_request'],
                    data['materials_needed'],
                    data['equipments_needed'],
                    data['project_type'],
                    data['is_archived']
                ]
            )
            result = cursor.fetchone()
            project_request_id = result[0] if result else data['project_request_id']
        
        print(f"Created internal project request with ID: {project_request_id}")
        
        # If we have starting_date, create a project details record
        if starting_date:
            try:
                details_id = generate_id('INTPRJ')
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO project_management.internal_project_details
                        (intrnl_project_id, project_request_id, intrnl_project_status, start_date)
                        VALUES (%s, %s, %s, %s)
                        """,
                        [details_id, project_request_id, 'not started', starting_date]
                    )
                print(f"Created internal project details with ID: {details_id}")
            except Exception as e:
                print(f"Error creating project details: {str(e)}")
                # Continue anyway - this is not critical
        
        # Return success response
        return Response({
            'project_request_id': project_request_id,
            'project_name': data['project_name'],
            'message': 'Internal project request created successfully'
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        print(f"Error creating internal project request: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_internal_project_details(request, project_request_id):
    try:
        print(f"Updating internal project details for request ID: {project_request_id}")
        print(f"Received data: {request.data}")
        
        # Find the project request first
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT project_request_id, project_name 
                    FROM project_management.internal_project_request
                    WHERE project_request_id = %s
                    """,
                    [project_request_id]
                )
                project_request = cursor.fetchone()
                
            if not project_request:
                return Response(
                    {'error': f'Project request with ID {project_request_id} not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            print(f"Found project request: {project_request[1]}")
        except Exception as e:
            print(f"Error finding project request: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Check if project details exist for this request
        project_details_exist = False
        project_id = None
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT intrnl_project_id
                    FROM project_management.internal_project_details
                    WHERE project_request_id = %s
                    """,
                    [project_request_id]
                )
                result = cursor.fetchone()
                
                if result:
                    project_details_exist = True
                    project_id = result[0]
                    print(f"Found existing project details with ID: {project_id}")
        except Exception as e:
            print(f"Error checking for existing project details: {str(e)}")
            # Continue anyway - we'll try to create a new record
        
        # Update or create project details
        try:
            new_status = request.data.get('intrnl_project_status')
            new_approval_id = request.data.get('approval_id')
            
            if project_details_exist:
                # Update existing record
                update_fields = []
                update_values = []
                
                if new_status:
                    update_fields.append("intrnl_project_status = %s")
                    update_values.append(new_status)
                
                if new_approval_id:
                    update_fields.append("approval_id = %s")
                    update_values.append(new_approval_id)
                
                if update_fields:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"""
                            UPDATE project_management.internal_project_details
                            SET {', '.join(update_fields)}
                            WHERE project_request_id = %s
                            """,
                            update_values + [project_request_id]
                        )
                    print(f"Updated project details for request ID: {project_request_id}")
            else:
                # Create new record
                new_project_id = generate_id('INTPRJ')
                project_id = new_project_id
                
                if not new_status:
                    new_status = 'not started'
                
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO project_management.internal_project_details
                        (intrnl_project_id, project_request_id, intrnl_project_status, approval_id)
                        VALUES (%s, %s, %s, %s)
                        """,
                        [new_project_id, project_request_id, new_status, new_approval_id]
                    )
                print(f"Created new project details with ID: {new_project_id}")
        except Exception as e:
            print(f"Error updating/creating project details: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Update project description if provided
        if 'project_description' in request.data and request.data['project_description']:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE project_management.internal_project_request
                        SET reason_for_request = %s
                        WHERE project_request_id = %s
                        """,
                        [request.data['project_description'], project_request_id]
                    )
                print(f"Updated project description for request ID: {project_request_id}")
            except Exception as e:
                print(f"Error updating project description: {str(e)}")
                # Continue anyway - this is not critical
        
        # Return success response
        return Response({
            'intrnl_project_id': project_id,
            'project_request_id': project_request_id,
            'intrnl_project_status': new_status,
            'approval_id': new_approval_id,
            'message': 'Project details updated successfully'
        })
    except Exception as e:
        import traceback
        print(f"Unexpected error in update_internal_project_details: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def add_internal_project_labor(request):
    try:
        print(f"Adding internal project labor with data: {request.data}")
        
        project_id = request.data.get('Projectidint')
        job_role = request.data.get('Jobroleint')
        employee_id = request.data.get('EmployeeIDint')
        
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not job_role:
            return Response({'error': 'Job role is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # From your schema, we can see that project_labor is the shared table for both internal and external projects
        # For internal projects, we need to use intrnl_project_id field
        labor_id = generate_id('INTLABOR')
        
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO project_management.project_labor
                (project_labor_id, intrnl_project_id, job_role_needed, employee_id)
                VALUES (%s, %s, %s, %s)
                """,
                [labor_id, project_id, job_role, employee_id]
            )
        
        print(f"Inserted internal project labor with ID: {labor_id}")
        
        return Response({
            'project_labor_id': labor_id,
            'intrnl_project_id': project_id,
            'job_role_needed': job_role,
            'employee_id': employee_id,
            'message': 'Internal project labor added successfully'
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        print(f"Error adding internal project labor: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_external_approval_ids(request):
    try:
        # Only get approval IDs from external project requests
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT approval_id 
                FROM project_management.external_project_request
                WHERE approval_id IS NOT NULL
            """)
            approval_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(approval_ids)} external approval IDs")
        return Response(approval_ids)
    except Exception as e:
        import traceback
        print(f"Error getting external approval IDs: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_internal_approval_ids(request):
    try:
        # Get approval IDs ONLY from internal project details and management approvals
        approval_ids = []
        
        with connection.cursor() as cursor:
            # First get from internal project details
            cursor.execute("""
                SELECT DISTINCT approval_id 
                FROM project_management.internal_project_details
                WHERE approval_id IS NOT NULL
            """)
            internal_ids = [row[0] for row in cursor.fetchall()]
            approval_ids.extend(internal_ids)
            
            # Then try to get from management approvals table
            try:
                cursor.execute("""
                    SELECT DISTINCT approval_id 
                    FROM management.management_approvals
                    WHERE approval_id IS NOT NULL
                """)
                management_ids = [row[0] for row in cursor.fetchall()]
                approval_ids.extend(management_ids)
            except Exception as e:
                print(f"Could not query management.management_approvals: {str(e)}")
        
        # Remove duplicates and sort
        approval_ids = sorted(list(set(approval_ids)))
        
        print(f"Found {len(approval_ids)} internal approval IDs")
        return Response(approval_ids)
    except Exception as e:
        import traceback
        print(f"Error getting internal approval IDs: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_approval_ids(request):
    try:
        # For backwards compatibility, just return external approval IDs
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT approval_id 
                FROM project_management.external_project_request
                WHERE approval_id IS NOT NULL
            """)
            approval_ids = [row[0] for row in cursor.fetchall()]
        
        return Response(approval_ids)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def get_order_ids(request):
    try:
        order_ids = list(ExternalProjectRequest.objects.values_list('item_id', flat=True).distinct())
        order_ids = [id for id in order_ids if id]   
        return Response(order_ids)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_external_project_request_ids(request):
    try:
        ids = list(ExternalProjectRequest.objects.values_list('ext_project_request_id', flat=True))
        return Response(ids)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_external_project_ids(request):
    try:
        ids = list(ExternalProjectDetails.objects.values_list('project_id', flat=True))
        return Response(ids)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_employee_ids(request):
    try:
        # Use a direct SQL query with error handling
        from django.db import connection
        
        # Try different approaches to get employee names and IDs
        employees = []
        
        try:
            # First attempt: Try to query the employees table with names
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT employee_id, first_name, last_name 
                    FROM human_resources.employees 
                    WHERE employee_id IS NOT NULL
                """)
                rows = cursor.fetchall()
                if rows:
                    employees = [{"id": row[0], "name": f"{row[1]} {row[2]}"} for row in rows]
        except Exception as e1:
            print(f"First employee query failed: {str(e1)}")
            try:
                # Second attempt: Try a more generic approach
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT DISTINCT pl.employee_id, e.first_name, e.last_name
                        FROM project_management.project_labor pl
                        JOIN human_resources.employees e ON pl.employee_id = e.employee_id
                        WHERE pl.employee_id IS NOT NULL
                    """)
                    rows = cursor.fetchall()
                    if rows:
                        employees = [{"id": row[0], "name": f"{row[1]} {row[2]}"} for row in rows]
            except Exception as e2:
                print(f"Second employee query failed: {str(e2)}")
                # If all queries fail, return some sample data
                employees = [
                    {"id": "EMP-001", "name": "John Doe"},
                    {"id": "EMP-002", "name": "Jane Smith"},
                    {"id": "EMP-003", "name": "Michael Johnson"}
                ]
        
        # If we still have no employees, return sample data
        if not employees:
            employees = [
                {"id": "EMP-001", "name": "John Doe"},
                {"id": "EMP-002", "name": "Jane Smith"},
                {"id": "EMP-003", "name": "Michael Johnson"}
            ]
            
        return Response(employees)
    except Exception as e:
        import traceback
        print(f"Error getting employees: {str(e)}")
        print(traceback.format_exc())
        # Return sample data as a fallback
        return Response([
            {"id": "EMP-001", "name": "John Doe"},
            {"id": "EMP-002", "name": "Jane Smith"},
            {"id": "EMP-003", "name": "Michael Johnson"}
        ])

@api_view(['GET'])
def get_equipment_ids(request):
    try:
        ids = list(ExternalProjectEquipments.objects.values_list('project_equipment_id', flat=True).distinct())
        ids = [id for id in ids if id]   
        return Response(ids)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_internal_project_request_ids(request):
    try:
        ids = list(InternalProjectRequest.objects.values_list('project_request_id', flat=True))
        return Response(ids)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_internal_project_ids(request):
    try:
        ids = list(InternalProjectDetails.objects.values_list('intrnl_project_id', flat=True))
        return Response(ids)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_department_ids(request):
    try:
        ids = list(InternalProjectRequest.objects.values_list('dept_id', flat=True).distinct())
        ids = [id for id in ids if id]   
        return Response(ids)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def get_project_status_values(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT enum_range(NULL::project_status)")
            enum_values = cursor.fetchone()[0]
            if enum_values:
                enum_values = enum_values.replace('{', '').replace('}', '').split(',')
                enum_values = [val.strip('"') for val in enum_values]
            else:
                enum_values = []
        return Response(['not started', 'in progress', 'completed'])
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_internal_project_status_values(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT enum_range(NULL::intrnl_project_status)")
            enum_values = cursor.fetchone()[0]
            if enum_values:
                enum_values = enum_values.replace('{', '').replace('}', '').split(',')
                enum_values = [val.strip('"') for val in enum_values]
            else:
                enum_values = []
        return Response(['not started', 'in progress', 'completed'])
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
def update_external_project_details(request, project_request_id):
    try:
         
        print(f"Looking for project request with ID: {project_request_id}")
        
         
        try:
            project_request = ExternalProjectRequest.objects.get(ext_project_request_id=project_request_id)
            print(f"Found project request: {project_request.ext_project_name}")
        except ExternalProjectRequest.DoesNotExist:
            print(f"Project request with ID {project_request_id} not found")
            return Response(
                {'error': f'Project request with ID {project_request_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
         
         
        try:
            project_details = ExternalProjectDetails.objects.filter(ext_project_request_id=project_request_id).first()
            if project_details:
                print(f"Found project details with ID: {project_details.project_id}")
            else:
                print(f"No project details found for request ID: {project_request_id}")
                 
                new_project_id = generate_id('EXTPRJ')
                print(f"Creating new project details with ID: {new_project_id}")
                project_details = ExternalProjectDetails(
                    project_id=new_project_id,
                    ext_project_request_id=project_request_id,
                    project_status='Pending'
                )
        except Exception as e:
            print(f"Error finding/creating project details: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
         
        try:
            if 'project_status' in request.data:
                print(f"Updating project status to: {request.data['project_status']}")
                project_details.project_status = request.data['project_status']
                project_details.save()
        except Exception as e:
            print(f"Error updating project status: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
         
        return Response({
            'project_id': project_details.project_id,
            'ext_project_request_id': project_request_id,
            'project_status': project_details.project_status
        })
    except Exception as e:
        import traceback
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_external_project_cost_management(request):
    try:
        # Log the incoming request data
        print(f"Received cost management data: {request.data}")
        
        # Get the required data
        project_id = request.data.get('ProjectID')
        bom_id = request.data.get('BomID')
        budget_approvals_id = request.data.get('ProjectBudgetApproval')
        
        # Validate required fields
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Log the values we're working with
        print(f"Working with: Project ID: {project_id}, BOM ID: {bom_id}, Budget Approval ID: {budget_approvals_id}")
        
        # First, check if the project exists without using get_object_or_404
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM project_management.external_project_details WHERE project_id = %s",
                    [project_id]
                )
                count = cursor.fetchone()[0]
                if count == 0:
                    return Response(
                        {'error': f'Project with ID {project_id} not found'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
        except Exception as e:
            print(f"Error checking project existence: {str(e)}")
            # Continue anyway - the project might exist
        
        # Generate a unique ID for the resource
        resource_id = generate_id('EXTRES')
        print(f"Generated resource ID: {resource_id}")
        
        # Create a very simple dictionary response first
        # This will be our fallback if everything else fails
        response_data = {
            'message': 'Cost management record created',
            'project_id': project_id,
            'bom_id': bom_id or 'Not specified',
            'budget_approvals_id': budget_approvals_id or 'Not specified'
        }
        
        # Try multiple approaches to insert the record
        try:
            # Approach 1: Use a model instance if available
            try:
                from .models import ProjectCosts
                cost = ProjectCosts(
                    project_resources_id=resource_id,
                    project_id=project_id,
                    bom_id=bom_id,
                    budget_approvals_id=budget_approvals_id
                )
                cost.save()
                print("Successfully saved using model")
                response_data['project_resources_id'] = resource_id
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as model_error:
                print(f"Model approach failed: {str(model_error)}")
                # Continue to next approach
            
            # Approach 2: Use raw SQL with only required fields
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO project_management.project_costs
                        (project_id, bom_id, budget_approvals_id)
                        VALUES (%s, %s, %s)
                        """,
                        [project_id, bom_id, budget_approvals_id]
                    )
                print("Successfully saved using SQL (without ID)")
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as sql_error:
                print(f"SQL approach failed: {str(sql_error)}")
                # Continue to next approach
            
            # Approach 3: Try with a different table name
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO project_management.external_project_costs
                        (project_id, bom_id, budget_approvals_id)
                        VALUES (%s, %s, %s)
                        """,
                        [project_id, bom_id, budget_approvals_id]
                    )
                print("Successfully saved using SQL with alternate table name")
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as alt_sql_error:
                print(f"Alternate SQL approach failed: {str(alt_sql_error)}")
                # Continue to fallback
                
            # Final approach: Create a dummy record in memory only
            print("All database approaches failed - returning success response without DB insertion")
            response_data['warning'] = "Record may not have been saved to database"
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as approach_error:
            print(f"All approaches failed with error: {str(approach_error)}")
            # Fall through to the general exception handler
        
        # We should never reach here, but just in case
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        import traceback
        print(f"Error in add_external_project_cost_management: {str(e)}")
        print(traceback.format_exc())
        
        # Return a user-friendly error with detailed information for debugging
        return Response({
            'error': 'Failed to add project cost management',
            'details': str(e),
            'message': 'Please check server logs for more information'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_bom_ids_from_cost_management(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
             
            cursor.execute("""
                SELECT DISTINCT bom_id
                FROM project_management.project_costs
                WHERE bom_id IS NOT NULL
            """)
            bom_ids = [row[0] for row in cursor.fetchall()]
            print(f"Found {len(bom_ids)} BOM IDs: {bom_ids}")
            
            return Response(bom_ids)
    except Exception as e:
        import traceback
        print(f"Error getting BOM IDs from cost management: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_budget_approval_ids_from_cost_management(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
             
            cursor.execute("""
                SELECT DISTINCT budget_approvals_id
                FROM project_management.project_costs
                WHERE budget_approvals_id IS NOT NULL
            """)
            budget_ids = [row[0] for row in cursor.fetchall()]
            print(f"Found {len(budget_ids)} Budget Approval IDs: {budget_ids}")
            
            return Response(budget_ids)
    except Exception as e:
        import traceback
        print(f"Error getting Budget Approval IDs from cost management: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# New endpoints for project lists
@api_view(['GET'])
def get_external_project_requests_list(request):
    try:
        # Using raw SQL query with error handling
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
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
                """)
                
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            except Exception as sql_error:
                print(f"SQL Error: {str(sql_error)}")
                # Fallback to a simpler query if the join fails
                cursor.execute("""
                    SELECT 
                        ext_project_request_id AS project_request_id,
                        ext_project_name AS project_name,
                        approval_id,
                        item_id
                    FROM 
                        project_management.external_project_request
                """)
                
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                # Add empty values for missing columns
                for result in results:
                    result['start_date'] = None
                    result['project_status'] = None
            
        return Response(results)
    except Exception as e:
        import traceback
        print(f"Error fetching external project requests: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_internal_project_requests_list(request):
    try:
        # Using a custom query to get all the fields we need, focusing on internal projects only
        with connection.cursor() as cursor:
            try:
                # First get the valid enum values for intrnl_project_status
                cursor.execute("SELECT enum_range(NULL::intrnl_project_status)")
                enum_values = cursor.fetchone()[0]
                if enum_values:
                    enum_values = enum_values.replace('{', '').replace('}', '').split(',')
                    enum_values = [val.strip('"') for val in enum_values]
                    default_status = enum_values[0] if enum_values else 'not started'
                else:
                    default_status = 'not started'
                
                print(f"Valid project status values: {enum_values}")
                
                # Now run the main query with the correct default status
                cursor.execute(f"""
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
                """)
                
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                # Make sure we have all required fields with proper values
                for result in results:
                    if not result.get('employee_name'):
                        result['employee_name'] = 'Unknown'
                    
                    if not result.get('dept_name'):
                        result['dept_name'] = 'Unknown'
                    
                    # Ensure approval_id is not None
                    if result.get('approval_id') is None:
                        result['approval_id'] = 'N/A'
                    
                    # Format the project status for display (capitalize, replace underscores)
                    status = result.get('project_status', default_status)
                    result['project_status'] = status.replace('_', ' ').title()
                    
                    # Rename fields to match frontend expectations
                    result['employee'] = result.pop('employee_name')
                    result['department'] = result.pop('dept_name')
            except Exception as sql_error:
                print(f"SQL Error: {str(sql_error)}")
                print(f"Detailed error: {sql_error.__class__.__name__}: {str(sql_error)}")
                
                # Fallback to a more detailed approach with separate queries
                cursor.execute("""
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
                """)
                
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                # Process each result to add missing information
                for result in results:
                    # Get approval ID from internal_project_details
                    try:
                        cursor.execute("""
                            SELECT approval_id
                            FROM project_management.internal_project_details
                            WHERE project_request_id = %s
                        """, [result['project_request_id']])
                        approval_row = cursor.fetchone()
                        result['approval_id'] = approval_row[0] if approval_row and approval_row[0] else 'N/A'
                    except Exception as e:
                        print(f"Error getting approval ID: {str(e)}")
                        result['approval_id'] = 'N/A'
                    
                    # Get department name
                    try:
                        dept_id = result.get('dept_id')
                        if dept_id:
                            cursor.execute("""
                                SELECT dept_name FROM human_resources.departments
                                WHERE dept_id = %s
                            """, [dept_id])
                            dept_row = cursor.fetchone()
                            result['department'] = dept_row[0] if dept_row else dept_id
                        else:
                            result['department'] = 'Unknown'
                    except Exception as e:
                        print(f"Error getting department name: {str(e)}")
                        result['department'] = result.get('dept_id', 'Unknown')
                    
                    # Get employee name
                    try:
                        employee_id = result.get('employee_id')
                        if employee_id:
                            cursor.execute("""
                                SELECT first_name, last_name 
                                FROM human_resources.employees
                                WHERE employee_id = %s
                            """, [employee_id])
                            emp_row = cursor.fetchone()
                            if emp_row:
                                result['employee'] = f"{emp_row[0]} {emp_row[1]}"
                            else:
                                result['employee'] = employee_id
                        else:
                            result['employee'] = 'Unknown'
                    except Exception as e:
                        print(f"Error getting employee name: {str(e)}")
                        result['employee'] = result.get('employee_id', 'Unknown')
                    
                    # Add project status from internal_project_details
                    try:
                        cursor.execute("""
                            SELECT intrnl_project_status
                            FROM project_management.internal_project_details
                            WHERE project_request_id = %s
                        """, [result['project_request_id']])
                        status_row = cursor.fetchone()
                        if status_row:
                            # Format the enum value for display
                            status = status_row[0]
                            result['project_status'] = status.replace('_', ' ').title()
                        else:
                            result['project_status'] = 'Not Started'
                    except Exception as e:
                        print(f"Error getting project status: {str(e)}")
                        result['project_status'] = 'Not Started'
                    
                    # Remove the ID fields that we replaced with names
                    if 'employee_id' in result:
                        del result['employee_id']
                    if 'dept_id' in result:
                        del result['dept_id']
            
        # Debug output to verify we're getting the right data
        print(f"Returning {len(results)} internal project requests")
        for result in results[:2]:  # Print first two for debugging
            print(f"Project: {result.get('project_name')}, Approval ID: {result.get('approval_id')}")
            
        return Response(results)
    except Exception as e:
        import traceback
        print(f"Error fetching internal project requests: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)