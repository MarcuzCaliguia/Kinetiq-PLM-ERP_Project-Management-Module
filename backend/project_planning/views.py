from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
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
        project_id = request.data.get('ProjectID')
        project = get_object_or_404(ExternalProjectDetails, project_id=project_id)
        
        data = {
            'project_labor_id': generate_id('LABOR'),
            'project': project_id,
            'job_role_needed': request.data.get('JobRoleNeeded'),
            'employee_id': request.data.get('EmployeeID')
        }
        
        serializer = ExternalProjectLaborSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
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
         
        project_id = request.data.get('ProjectID')
        if not project_id:
            return Response({'error': 'ProjectID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
         
        try:
            project = ExternalProjectDetails.objects.get(project_id=project_id)
        except ExternalProjectDetails.DoesNotExist:
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
        
         
        warranty = ExternalProjectWarranty(
            project_warranty_id=generate_id('WARRANTY'),
            project=project,
            warranty_coverage_yr=warranty_coverage_yr,
            warranty_start_date=warranty_start_date,
            warranty_end_date=warranty_end_date
        )
        
        warranty.save()
        
         
        return Response({
            'project_warranty_id': warranty.project_warranty_id,
            'project_id': project_id,
            'warranty_coverage_yr': warranty_coverage_yr,
            'warranty_start_date': warranty_start_date,
            'warranty_end_date': warranty_end_date
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
         
        import traceback
        print(f"Error adding project warranty: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_internal_project(request):
    try:
        print(f"Received data: {request.data}")
        
      
        project_name = request.data.get('ProjectNameint')
        request_date = request.data.get('RequestDateint')
        starting_date = request.data.get('Startingdateint')
        employee_id = request.data.get('EmployeeIDint')
        department_id = request.data.get('DepartmentIDint')
        budget_request = request.data.get('Budgetrequestint')
        budget_description = request.data.get('Budgetdescriptionint')
        
      
        if not project_name:
            return Response({'error': 'Project name is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not request_date:
            return Response({'error': 'Request date is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not starting_date:
            return Response({'error': 'Starting date is required'}, status=status.HTTP_400_BAD_REQUEST)
        
       
        data = {
            'project_request_id': generate_id('INTREQ'),
            'project_name': project_name,
            'project_description': None, 
            'request_date': request_date,
            'target_starting_date': starting_date,
            'employee_id': employee_id,
            'dept_id': department_id,
            'project_budget_request': budget_request,
            'project_budget_description': budget_description
        }
        
        serializer = InternalProjectRequestSerializer(data=data)
        if serializer.is_valid():
            project_request = serializer.save()
            
             
            return Response({
                'project_request_id': project_request.project_request_id,
                'project_name': project_request.project_name,
                'message': 'Internal project request created successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
        
        
        try:
            project_request = InternalProjectRequest.objects.get(project_request_id=project_request_id)
            print(f"Found project request: {project_request.project_name}")
        except InternalProjectRequest.DoesNotExist:
            print(f"Project request with ID {project_request_id} not found")
            return Response(
                {'error': f'Project request with ID {project_request_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
       
        try:
            project_details = InternalProjectDetails.objects.filter(project_request_id=project_request_id).first()
            if project_details:
                print(f"Found existing project details with ID: {project_details.intrnl_project_id}")
            else:
                print(f"Creating new project details for request ID: {project_request_id}")
                project_details = InternalProjectDetails(
                    intrnl_project_id=generate_id('INTPRJ'),
                    project_request=project_request,
                    intrnl_project_status='Pending',
                    approval_id=None
                )
        except Exception as e:
            print(f"Error finding/creating project details: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
         
        if 'intrnl_project_status' in request.data:
            project_details.intrnl_project_status = request.data['intrnl_project_status']
        
        if 'approval_id' in request.data:
            project_details.approval_id = request.data['approval_id']
            
         
        project_details.save()
        
         
        if 'project_description' in request.data and request.data['project_description']:
            project_request.project_description = request.data['project_description']
            project_request.save()
        
         
        return Response({
            'intrnl_project_id': project_details.intrnl_project_id,
            'project_request_id': project_request_id,
            'intrnl_project_status': project_details.intrnl_project_status,
            'approval_id': project_details.approval_id,
            'project_description': project_request.project_description
        })
    except Exception as e:
        import traceback
        print(f"Error updating internal project details: {str(e)}")
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
        
         
        try:
            project = InternalProjectDetails.objects.get(intrnl_project_id=project_id)
        except InternalProjectDetails.DoesNotExist:
            return Response(
                {'error': f'Internal project with ID {project_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
         
        data = {
            'intrnl_project_labor_id': generate_id('INTLABOR'),
            'intrnl_project': project_id,
            'intrnl_job_role_needed': job_role,
            'employee_id': employee_id
        }
        
        serializer = InternalProjectLaborSerializer(data=data)
        if serializer.is_valid():
            labor = serializer.save()
            
             
            return Response({
                'intrnl_project_labor_id': labor.intrnl_project_labor_id,
                'intrnl_project_id': project_id,
                'intrnl_job_role_needed': job_role,
                'employee_id': employee_id,
                'message': 'Internal project labor added successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import traceback
        print(f"Error adding internal project labor: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
@api_view(['GET'])
def get_approval_ids(request):
    try:
        approval_ids = list(ExternalProjectRequest.objects.values_list('approval_id', flat=True).distinct())
        approval_ids = [id for id in approval_ids if id]   
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
        emp_ids = list(ExternalProjectLabor.objects.values_list('employee_id', flat=True).distinct())
        int_emp_ids = list(InternalProjectLabor.objects.values_list('employee_id', flat=True).distinct())
        int_req_emp_ids = list(InternalProjectRequest.objects.values_list('employee_id', flat=True).distinct())
        
        all_ids = emp_ids + int_emp_ids + int_req_emp_ids
        all_ids = [id for id in all_ids if id]   
        return Response(list(set(all_ids)))   
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        project_id = request.data.get('ProjectID')
        bom_id = request.data.get('BomID')
        budget_approvals_id = request.data.get('ProjectBudgetApproval')
        
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
         
        try:
            project = ExternalProjectDetails.objects.get(project_id=project_id)
        except ExternalProjectDetails.DoesNotExist:
            return Response(
                {'error': f'Project with ID {project_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
         
         
        cost_management = {
            'project_resources_id': generate_id('EXTRES'),   
            'project_id': project_id,
            'bom_id': bom_id,
            'budget_approvals_id': budget_approvals_id
        }
        
         
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO project_management.external_project_cost_management
                (project_id, bom_id, budget_approvals_id)
                VALUES (%s, %s, %s)
                RETURNING project_resources_id
                """,
                [project_id, bom_id, budget_approvals_id]
            )
            result = cursor.fetchone()
            if result:
                project_resources_id = result[0]
            else:
                project_resources_id = None
        
        return Response({
            'project_resources_id': project_resources_id,
            'project_id': project_id,
            'bom_id': bom_id,
            'budget_approvals_id': budget_approvals_id
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        print(f"Error adding project cost management: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_bom_ids_from_cost_management(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
             
            cursor.execute("""
                SELECT DISTINCT bom_id
                FROM project_management.external_project_cost_management
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
                FROM project_management.external_project_cost_management
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