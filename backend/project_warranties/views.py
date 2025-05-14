from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.db.models import Q, Prefetch, OuterRef, Subquery, F
from django.db import connection
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
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
            # Start with a base queryset - avoid select_related since ext_project_request_id is not a foreign key
            queryset = ExternalProjectDetails.objects.all()
            
            # Apply status filtering
            status_filter = self.request.query_params.get('status', None)
            if status_filter:
                if status_filter.lower() == 'active':
                    queryset = queryset.filter(warranty_status__icontains='active')
                elif status_filter.lower() == 'expired':
                    queryset = queryset.filter(warranty_status__icontains='expired')
                elif status_filter.lower() == 'pending':
                    queryset = queryset.filter(
                        Q(warranty_status__isnull=True) | 
                        (~Q(warranty_status__icontains='active') & 
                        ~Q(warranty_status__icontains='expired'))
                    )
            
            # Apply warranty filter
            warranty_filter = self.request.query_params.get('has_warranty', None)
            if warranty_filter:
                if warranty_filter.lower() == 'true':
                    queryset = queryset.filter(warranty_coverage_yr__isnull=False)
                elif warranty_filter.lower() == 'false':
                    queryset = queryset.filter(warranty_coverage_yr__isnull=True)
            else:
                # Default to showing only warranties
                queryset = queryset.filter(warranty_coverage_yr__isnull=False)
                
                # Fallback to all if no results with warranty
                if not queryset.exists():
                    queryset = ExternalProjectDetails.objects.all()
            
            # Apply project name filter - using join through a subquery since it's not a direct relation
            project_name = self.request.query_params.get('project_name', None)
            if project_name:
                # Get project request IDs matching the name
                project_request_ids = ExternalProjectRequest.objects.filter(
                    ext_project_name__icontains=project_name
                ).values_list('ext_project_request_id', flat=True)
                
                # Filter projects by these IDs
                queryset = queryset.filter(ext_project_request_id__in=project_request_ids)
                
            # Add .only() to limit fields if you don't need all columns
            return queryset.order_by('project_id')
        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}", exc_info=True)
            return ExternalProjectDetails.objects.none()
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        """Override list to handle errors and enhance search, with caching"""
        try:
            search_query = request.query_params.get('search', '')
            
            # If search is provided, build an optimized query
            if search_query:
                # Get base queryset with optimized joins
                queryset = self.filter_queryset(self.get_queryset())
                
                # Direct project ID matches
                direct_matches = queryset.filter(project_id__icontains=search_query)
                
                # Project name matches - need to join through project request IDs
                project_request_ids = ExternalProjectRequest.objects.filter(
                    ext_project_name__icontains=search_query
                ).values_list('ext_project_request_id', flat=True)
                
                name_matches = queryset.filter(ext_project_request_id__in=project_request_ids)
                
                # Combine results without duplicate DB hits
                queryset = (direct_matches | name_matches).distinct()
                
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
            
            # Use parent implementation for non-search cases
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
    
    # Try to get from cache first
    cache_key = f'project_autocomplete_{query}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return Response(cached_result)
    
    try:
        # Use a more efficient query with optimized eager loading
        projects = ProjectWarrantyView.objects.filter(
            Q(project_id__icontains=query) | Q(ext_project_name__icontains=query)
        ).values('project_id', 'ext_project_name')[:10]
        
        formatted_projects = [
            {
                'project_id': p['project_id'],
                'project_name': p['ext_project_name'] or f"Project {p['project_id']}"
            }
            for p in projects
        ]
        
        # Only if first approach returned nothing, try the fallback
        if not formatted_projects:
            # Get all project IDs matching the query
            project_details = ExternalProjectDetails.objects.filter(
                project_id__icontains=query
            ).values('project_id', 'ext_project_request_id')[:10]
            
            formatted_projects = []
            for proj in project_details:
                project_name = f"Project {proj['project_id']}"
                
                # Look up project name if request ID is available
                if proj['ext_project_request_id']:
                    try:
                        project_request = ExternalProjectRequest.objects.get(
                            ext_project_request_id=proj['ext_project_request_id']
                        )
                        if project_request.ext_project_name:
                            project_name = project_request.ext_project_name
                    except ExternalProjectRequest.DoesNotExist:
                        pass
                
                formatted_projects.append({
                    'project_id': proj['project_id'],
                    'project_name': project_name
                })
        
        # Cache the result for 1 hour
        cache.set(cache_key, formatted_projects, 60 * 60)
        return Response(formatted_projects)
    except Exception as e:
        logger.error(f"Error in project_autocomplete: {str(e)}", exc_info=True)
        return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def project_warranty_details(request, project_id):
    """Get warranty details for a specific project"""
    # Try to get from cache first
    cache_key = f'project_warranty_{project_id}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return Response(cached_result)
    
    try:
        # Use a single efficient query with select_related to get all related data
        warranty_view = ProjectWarrantyView.objects.filter(project_id=project_id).first()
        
        if warranty_view:
            # Prepare base response from warranty view
            response_data = {
                'project_id': warranty_view.project_id,
                'project_name': warranty_view.ext_project_name or f"Project {project_id}",
                'warranty_coverage_yr': warranty_view.warranty_coverage_yr,
                'warranty_status': warranty_view.warranty_status,
                'warranty_exists': warranty_view.warranty_coverage_yr is not None
            }
            
            # Get additional details if needed
            # This could possibly be included in the warranty view to avoid this query
            detailed_warranty = ExternalProjectDetails.objects.filter(
                project_id=project_id
            ).only('warranty_start_date', 'warranty_end_date').first()
            
            if detailed_warranty:
                response_data.update({
                    'warranty_start_date': detailed_warranty.warranty_start_date,
                    'warranty_end_date': detailed_warranty.warranty_end_date
                })
            
            # Cache the result for 30 minutes
            cache.set(cache_key, response_data, 30 * 60)
            return Response(response_data)
        
        # Fallback with optimized query
        project = ExternalProjectDetails.objects.filter(
            project_id=project_id
        ).first()
        
        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get project name efficiently
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
        
        response_data = {
            'project_id': project.project_id,
            'project_name': project_name,
            'warranty_coverage_yr': project.warranty_coverage_yr,
            'warranty_start_date': project.warranty_start_date,
            'warranty_end_date': project.warranty_end_date,
            'warranty_status': project.warranty_status,
            'warranty_exists': project.warranty_coverage_yr is not None
        }
        
        # Cache the result for 30 minutes
        cache.set(cache_key, response_data, 30 * 60)
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error in project_warranty_details: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)