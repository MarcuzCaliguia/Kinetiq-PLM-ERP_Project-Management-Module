# project_warranties/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
import traceback

from .models import ExternalProjectDetails, ExternalProjectRequest, ProjectWarrantyView
from .serializers import ExternalProjectDetailsSerializer, ProjectWarrantyViewSerializer

class ExternalProjectDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = ExternalProjectDetailsSerializer
    
    def get_queryset(self):
        """Filter queryset to only include projects with warranty data"""
        try:
            # First, try to get all projects with warranty data
            queryset = ExternalProjectDetails.objects.filter(
                warranty_coverage_yr__isnull=False
            ).order_by('project_id')
            
            # If no projects with warranty data, return all projects
            if not queryset.exists():
                queryset = ExternalProjectDetails.objects.all().order_by('project_id')
                
            return queryset
        except Exception as e:
            print(f"Error in get_queryset: {str(e)}")
            traceback.print_exc()
            # Return empty queryset on error
            return ExternalProjectDetails.objects.none()
    
    def list(self, request, *args, **kwargs):
        """Override list to handle errors gracefully"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(f"Error in list: {str(e)}")
            traceback.print_exc()
            return Response(
                {"error": "An error occurred while fetching warranties."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
def project_autocomplete(request):
    query = request.GET.get('query', '')
    print(f"Project autocomplete query: {query}")
    
    if not query:
        print("No query provided, returning empty list")
        return Response([])
    
    try:
        # Try to search in ProjectWarrantyView first as it has project names already
        projects = ProjectWarrantyView.objects.filter(
            Q(project_id__icontains=query) | Q(ext_project_name__icontains=query)
        ).values('project_id', 'ext_project_name')[:10]
        
        if projects.exists():
            formatted_projects = [
                {
                    'project_id': p['project_id'],
                    'project_name': p['ext_project_name'] or f"Project {p['project_id']}"
                }
                for p in projects
            ]
            return Response(formatted_projects)
        
        # If not found in view, search in project details
        projects = ExternalProjectDetails.objects.filter(
            project_id__icontains=query
        ).values('project_id', 'ext_project_request_id')[:10]
        
        # Get project names
        formatted_projects = []
        for project in projects:
            project_id = project['project_id']
            project_name = f"Project {project_id}"
            
            # Try to get project name from request
            if project['ext_project_request_id']:
                try:
                    project_request = ExternalProjectRequest.objects.get(
                        ext_project_request_id=project['ext_project_request_id']
                    )
                    if project_request.ext_project_name:
                        project_name = project_request.ext_project_name
                except Exception as e:
                    print(f"Error getting project request: {str(e)}")
                
            formatted_projects.append({
                'project_id': project_id,
                'project_name': project_name
            })
        
        return Response(formatted_projects)
    except Exception as e:
        print(f"Error in project_autocomplete: {str(e)}")
        traceback.print_exc()
        return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def project_warranty_details(request, project_id):
    """Get warranty details for a specific project"""
    try:
        # Try to get from the warranty view first
        warranty_view = ProjectWarrantyView.objects.filter(project_id=project_id).first()
        
        if warranty_view:
            return Response({
                'project_id': warranty_view.project_id,
                'project_name': warranty_view.ext_project_name or f"Project {project_id}",
                'warranty_coverage_yr': warranty_view.warranty_coverage_yr,
                'warranty_status': warranty_view.warranty_status,
                'warranty_exists': warranty_view.warranty_coverage_yr is not None
            })
        
        # If not in view, get from project details
        project = ExternalProjectDetails.objects.filter(project_id=project_id).first()
        
        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Try to get project name
        project_name = f"Project {project_id}"
        if project.ext_project_request_id:
            try:
                project_request = ExternalProjectRequest.objects.get(
                    ext_project_request_id=project.ext_project_request_id
                )
                if project_request.ext_project_name:
                    project_name = project_request.ext_project_name
            except Exception as e:
                print(f"Error getting project request: {str(e)}")
        
        # Return project details with warranty information
        return Response({
            'project_id': project.project_id,
            'project_name': project_name,
            'warranty_coverage_yr': project.warranty_coverage_yr,
            'warranty_start_date': project.warranty_start_date,
            'warranty_end_date': project.warranty_end_date,
            'warranty_status': project.warranty_status,
            'warranty_exists': project.warranty_coverage_yr is not None
        })
    except Exception as e:
        print(f"Error in project_warranty_details: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)