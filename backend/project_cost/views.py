from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from .models import ProjectCosts

class ProjectCostViewSet(viewsets.ModelViewSet):
    queryset = ProjectCosts.objects.all()
    
    @action(detail=False, methods=['get'])
    def all_projects(self, request):
        """Get all project costs with proper project names"""
        try:
            with connection.cursor() as cursor:
                # Execute a query to get the raw project cost data with names
                cursor.execute("""
                    WITH project_data AS (
                        SELECT 
                            pc.project_resources_id,
                            pc.project_id,
                            pc.intrnl_project_id,
                            pc.bom_id,
                            pc.budget_approvals_id,
                            pc.outside_labor_costs,
                            pc.utility_costs,
                            pc.outsourced_costs,
                            pc.overall_project_costs,
                            epr.ext_project_name,
                            ipr.project_name as internal_project_name
                        FROM project_management.project_costs pc
                        LEFT JOIN project_management.external_project_request epr 
                            ON pc.project_id = epr.ext_project_request_id 
                        LEFT JOIN project_management.internal_project_request ipr 
                            ON pc.intrnl_project_id = ipr.project_request_id
                    )
                    SELECT * FROM project_data
                """)
                
                columns = [col[0] for col in cursor.description]
                results = cursor.fetchall()
            
            data = []
            for row in results:
                record = dict(zip(columns, row))
                
                # Fix project names
                project_name = None
                if record.get('internal_project_name') and record['internal_project_name'] != '[null]':
                    project_name = record['internal_project_name']
                elif record.get('ext_project_name') and record['ext_project_name'] != '[null]':
                    project_name = record['ext_project_name']
                else:
                    # Fallback to a formatted ID
                    if record.get('intrnl_project_id'):
                        project_name = f"Internal Project {record['intrnl_project_id']}"
                    elif record.get('project_id'):
                        project_name = f"External Project {record['project_id']}"
                    else:
                        project_name = "Unnamed Project"
                
                # Format numeric fields
                outside_labor = float(record['outside_labor_costs']) if record['outside_labor_costs'] is not None else 0
                utility_costs = float(record['utility_costs']) if record['utility_costs'] is not None else 0
                outsourced_costs = float(record['outsourced_costs']) if record['outsourced_costs'] is not None else 0
                overall_costs = float(record['overall_project_costs']) if record['overall_project_costs'] is not None else 0
                
                # Create the response object in the format expected by the frontend
                project_data = {
                    'project_resources_id': record['project_resources_id'],
                    'project_id': record['project_id'],
                    'intrnl_project_id': record['intrnl_project_id'],
                    'bom_id': record['bom_id'],
                    'budget_approvals_id': record['budget_approvals_id'],
                    'outside_labor_costs': outside_labor,
                    'utility_costs': utility_costs,
                    'outsourced_costs': outsourced_costs,
                    'overall_project_costs': overall_costs,
                    'project_name': project_name
                }
                data.append(project_data)
            
            return Response(data)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in all_projects view: {str(e)}\n{error_details}")
            return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def direct_project_costs(request):
    """Get project costs using direct SQL approach"""
    try:
        # Fetch raw data from database
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH project_data AS (
                    SELECT 
                        pc.project_resources_id,
                        pc.project_id,
                        pc.intrnl_project_id,
                        pc.bom_id,
                        pc.budget_approvals_id,
                        pc.outside_labor_costs,
                        pc.utility_costs,
                        pc.outsourced_costs,
                        pc.overall_project_costs,
                        epr.ext_project_name,
                        ipr.project_name as internal_project_name
                    FROM project_management.project_costs pc
                    LEFT JOIN project_management.external_project_request epr 
                        ON pc.project_id = epr.ext_project_request_id 
                    LEFT JOIN project_management.internal_project_request ipr 
                        ON pc.intrnl_project_id = ipr.project_request_id
                )
                SELECT * FROM project_data
            """)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
        
        # Process results
        formatted_costs = []
        for row in results:
            record = dict(zip(columns, row))
            
            # Determine project name with appropriate fallbacks
            project_name = None
            if record.get('internal_project_name') and record['internal_project_name'] != '[null]':
                project_name = record['internal_project_name']
            elif record.get('ext_project_name') and record['ext_project_name'] != '[null]':
                project_name = record['ext_project_name']
            else:
                # Fallback to a formatted ID
                if record.get('intrnl_project_id'):
                    project_name = f"Internal Project {record['intrnl_project_id']}"
                elif record.get('project_id'):
                    project_name = f"External Project {record['project_id']}"
                else:
                    project_name = "Unnamed Project"
            
            # Format numeric fields
            outside_labor = float(record['outside_labor_costs']) if record['outside_labor_costs'] is not None else 0
            utility_costs = float(record['utility_costs']) if record['utility_costs'] is not None else 0
            outsourced_costs = float(record['outsourced_costs']) if record['outsourced_costs'] is not None else 0
            overall_costs = float(record['overall_project_costs']) if record['overall_project_costs'] is not None else 0
            
            # Create the response object in the format expected by the frontend
            cost_data = {
                'project_resources_id': record['project_resources_id'],
                'project_id': record['project_id'],
                'intrnl_project_id': record['intrnl_project_id'],
                'bom_id': record['bom_id'],
                'budget_approvals_id': record['budget_approvals_id'],
                'outside_labor_costs': outside_labor,
                'utility_costs': utility_costs,
                'outsourced_costs': outsourced_costs,
                'overall_project_costs': overall_costs,
                'project_name': project_name
            }
            formatted_costs.append(cost_data)
        
        return JsonResponse({
            'success': True,
            'count': len(formatted_costs),
            'data': formatted_costs
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in direct_project_costs: {str(e)}\n{error_trace}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': error_trace
        }, status=500)