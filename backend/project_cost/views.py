from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from .models import ProjectCosts

class ProjectCostViewSet(viewsets.ModelViewSet):
    queryset = ProjectCosts.objects.all()
    
    @action(detail=False, methods=['get'])
    def all_projects(self, request):
        """Get all project costs directly from the database"""
        try:
            # Get all project costs from the database
            project_costs = ProjectCosts.objects.all()
            print(f"Found {project_costs.count()} project costs in database")
            
            # Convert to a list of dictionaries
            data = []
            for cost in project_costs:
                project_data = {
                    'project_resources_id': cost.project_resources_id,
                    'project_id': cost.project_id,
                    'intrnl_project_id': cost.intrnl_project_id,
                    'bom_id': cost.bom_id,
                    'budget_approvals_id': cost.budget_approvals_id,
                    'outside_labor_costs': float(cost.outside_labor_costs) if cost.outside_labor_costs else 0,
                    'utility_costs': float(cost.utility_costs) if cost.utility_costs else 0,
                    'outsourced_costs': float(cost.outsourced_costs) if cost.outsourced_costs else 0,
                    'overall_project_costs': float(cost.overall_project_costs) if cost.overall_project_costs else 0
                }
                data.append(project_data)
            
            return Response(data)
        except Exception as e:
            print(f"Error in all_projects view: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)

# Simple direct SQL approach as a backup
@api_view(['GET'])
def direct_project_costs(request):
    """Get project costs using direct SQL"""
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    project_resources_id, project_id, bom_id, budget_approvals_id, 
                    intrnl_project_id, outside_labor_costs, utility_costs, 
                    outsourced_costs, overall_project_costs
                FROM project_management.project_costs
            """)
            columns = [col[0] for col in cursor.description]
            costs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return JsonResponse({
            'success': True,
            'count': len(costs),
            'data': costs
        })
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)