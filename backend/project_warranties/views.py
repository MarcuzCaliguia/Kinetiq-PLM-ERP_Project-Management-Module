
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
import logging

from .models import ExternalProjectDetails, ExternalProjectRequest, ProjectWarrantyView
from .serializers import ExternalProjectDetailsSerializer, ProjectWarrantyViewSerializer


logger = logging.getLogger(__name__)

class ExternalProjectDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = ExternalProjectDetailsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['project_id', 'warranty_status']
    ordering_fields = ['project_id', 'warranty_coverage_yr', 'warranty_start_date', 'warranty_end_date']
    ordering = ['project_id']
    
    def get_queryset(self):
        """Filter queryset to include projects with warranty data and support filtering"""
        try:
            
            queryset = ExternalProjectDetails.objects.all()
            
            
            status_filter = self.request.query_params.get('status', None)
            if status_filter:
                if status_filter.lower() == 'active':
                    queryset = queryset.filter(warranty_status__icontains='active')
                elif status_filter.lower() == 'expired':
                    queryset = queryset.filter(warranty_status__icontains='expired')
                elif status_filter.lower() == 'pending':
                    queryset = queryset.filter(
                        Q(warranty_status__isnull=True) | 
                        ~Q(warranty_status__icontains='active') & 
                        ~Q(warranty_status__icontains='expired')
                    )
            
            
            warranty_filter = self.request.query_params.get('has_warranty', None)
            if warranty_filter:
                if warranty_filter.lower() == 'true':
                    queryset = queryset.filter(warranty_coverage_yr__isnull=False)
                elif warranty_filter.lower() == 'false':
                    queryset = queryset.filter(warranty_coverage_yr__isnull=True)
            else:
                
                queryset = queryset.filter(warranty_coverage_yr__isnull=False)
                
                
                if not queryset.exists():
                    queryset = ExternalProjectDetails.objects.all()
            
            
            project_name = self.request.query_params.get('project_name', None)
            if project_name:
                
                
                project_request_ids = ExternalProjectRequest.objects.filter(
                    ext_project_name__icontains=project_name
                ).values_list('ext_project_request_id', flat=True)
                
                queryset = queryset.filter(
                    ext_project_request_id__in=project_request_ids
                )
                
            return queryset.order_by('project_id')
        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}", exc_info=True)
            return ExternalProjectDetails.objects.none()
    
    def list(self, request, *args, **kwargs):
        """Override list to handle errors and enhance search"""
        try:
            
            search_query = request.query_params.get('search', '')
            
            
            if search_query:
                
                queryset = self.filter_queryset(self.get_queryset())
                
                
                direct_matches = queryset.filter(project_id__icontains=search_query)
                
                
                project_request_ids = ExternalProjectRequest.objects.filter(
                    ext_project_name__icontains=search_query
                ).values_list('ext_project_request_id', flat=True)
                
                name_matches = queryset.filter(ext_project_request_id__in=project_request_ids)
                
                
                queryset = (direct_matches | name_matches).distinct()
                
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
            
            
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in list: {str(e)}", exc_info=True)
            return Response(
                {"error": "An error occurred while fetching warranties."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
def project_autocomplete(request):
    query = request.GET.get('query', '')
    logger.debug(f"Project autocomplete query: {query}")
    
    if not query:
        return Response([])
    
    try:
        
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
        
        
        project_ids = ExternalProjectDetails.objects.filter(
            project_id__icontains=query
        ).values_list('project_id', 'ext_project_request_id')[:10]
        
        formatted_projects = []
        for project_id, request_id in project_ids:
            project_name = f"Project {project_id}"
            
            
            if request_id:
                try:
                    project_request = ExternalProjectRequest.objects.get(
                        ext_project_request_id=request_id
                    )
                    if project_request.ext_project_name:
                        project_name = project_request.ext_project_name
                except ExternalProjectRequest.DoesNotExist:
                    pass
                
            formatted_projects.append({
                'project_id': project_id,
                'project_name': project_name
            })
        
        return Response(formatted_projects)
    except Exception as e:
        logger.error(f"Error in project_autocomplete: {str(e)}", exc_info=True)
        return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def project_warranty_details(request, project_id):
    """Get warranty details for a specific project"""
    try:
        
        warranty_view = ProjectWarrantyView.objects.filter(project_id=project_id).first()
        
        if warranty_view:
            
            response_data = {
                'project_id': warranty_view.project_id,
                'project_name': warranty_view.ext_project_name or f"Project {project_id}",
                'warranty_coverage_yr': warranty_view.warranty_coverage_yr,
                'warranty_status': warranty_view.warranty_status,
                'warranty_exists': warranty_view.warranty_coverage_yr is not None
            }
            
            
            
            detailed_warranty = ExternalProjectDetails.objects.filter(
                project_id=project_id
            ).first()
            
            if detailed_warranty:
                
                response_data.update({
                    'warranty_start_date': detailed_warranty.warranty_start_date,
                    'warranty_end_date': detailed_warranty.warranty_end_date
                })
            
            return Response(response_data)
        
        
        project = ExternalProjectDetails.objects.filter(
            project_id=project_id
        ).first()
        
        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        project_name = f"Project {project_id}"
        if project.ext_project_request_id:
            try:
                project_request = ExternalProjectRequest.objects.get(
                    ext_project_request_id=project.ext_project_request_id
                )
                if project_request.ext_project_name:
                    project_name = project_request.ext_project_name
            except ExternalProjectRequest.DoesNotExist:
                pass
        
        
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
        logger.error(f"Error in project_warranty_details: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)