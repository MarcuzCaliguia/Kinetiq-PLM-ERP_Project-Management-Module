from django.views.generic import TemplateView
from django.db.models import Q
from django.db import connection
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import InternalProjectRequest, ExternalProjectRequest
import datetime

class ProjectListView(TemplateView):
    template_name = 'project_request/project_list.html'
    
    def get_project_statuses(self):
        """Get status information for all projects based on correct schema"""
        internal_statuses = {}
        external_statuses = {}
        
        # Get today's date for comparison
        today = timezone.now().date()
        
        # Get internal project statuses using intrnl_project_status
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ipr.project_request_id,
                        ipd.intrnl_project_status
                    FROM 
                        internal_project_request ipr
                    LEFT JOIN 
                        internal_project_details ipd ON ipr.project_request_id = ipd.project_request_id
                """)
                
                for row in cursor.fetchall():
                    project_id, project_status = row
                    
                    # Default to ongoing
                    status = 'ongoing'
                    
                    # If project_status is explicitly set, use it
                    if project_status:
                        if project_status.lower() == 'completed':
                            status = 'completed'
                        elif project_status.lower() in ['delayed', 'frozen']:
                            status = 'delayed'
                    
                    internal_statuses[project_id] = status
        except Exception as e:
            print(f"Error fetching internal project statuses: {e}")
        
        # Get external project statuses using project_status
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        epr.ext_project_request_id,
                        epd.project_status
                    FROM 
                        external_project_request epr
                    LEFT JOIN 
                        external_project_details epd ON epr.ext_project_request_id = epd.ext_project_request_id
                """)
                
                for row in cursor.fetchall():
                    project_id, project_status = row
                    
                    # Default to ongoing
                    status = 'ongoing'
                    
                    # If project_status is explicitly set, use it
                    if project_status:
                        if project_status.lower() == 'completed':
                            status = 'completed'
                        elif project_status.lower() in ['delayed', 'frozen']:
                            status = 'delayed'
                    
                    external_statuses[project_id] = status
        except Exception as e:
            print(f"Error fetching external project statuses: {e}")
        
        # Assign default statuses for projects without status info
        for project in InternalProjectRequest.objects.all():
            if project.project_request_id not in internal_statuses:
                internal_statuses[project.project_request_id] = 'ongoing'
                
        for project in ExternalProjectRequest.objects.all():
            if project.ext_project_request_id not in external_statuses:
                external_statuses[project.ext_project_request_id] = 'ongoing'
        
        return internal_statuses, external_statuses
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests for removing projects"""
        if 'remove_projects' in request.POST:
            project_ids = request.POST.getlist('project_ids[]')
            
            if project_ids:
                # Delete selected projects
                try:
                    # Separate internal and external project IDs
                    internal_ids = []
                    external_ids = []
                    
                    for project_id in project_ids:
                        if project_id.startswith('INT-') or project_id.startswith('INTPRJ-'):
                            internal_ids.append(project_id)
                        elif project_id.startswith('EXT-') or project_id.startswith('EXTPRJ-'):
                            external_ids.append(project_id)
                    
                    # Delete internal projects
                    if internal_ids:
                        InternalProjectRequest.objects.filter(project_request_id__in=internal_ids).delete()
                    
                    # Delete external projects
                    if external_ids:
                        ExternalProjectRequest.objects.filter(ext_project_request_id__in=external_ids).delete()
                    
                except Exception as e:
                    print(f"Error removing projects: {e}")
            
            # Redirect to the same page to refresh
            return HttpResponseRedirect(reverse('project_request:project_list'))
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Debug: Print all GET parameters
        print("DEBUG: Request GET parameters:", self.request.GET)
        
        # Get filter parameters
        project_type = self.request.GET.get('type', 'all')
        search_query = self.request.GET.get('q', '')
        status_filter = self.request.GET.get('status', 'all')
        
        # Print debug info
        print(f"Search query: '{search_query}'")
        print(f"Project type: {project_type}")
        print(f"Status filter: {status_filter}")
        
        # Get all projects
        internal_projects = list(InternalProjectRequest.objects.all())
        external_projects = list(ExternalProjectRequest.objects.all())
        
        # Get project statuses
        internal_statuses, external_statuses = self.get_project_statuses()
        
        # Apply search if provided
        if search_query:
            search_query_lower = search_query.lower()
            
            # Filter internal projects
            filtered_internal = []
            for p in internal_projects:
                if (search_query_lower in p.project_name.lower() or 
                    search_query_lower in p.project_request_id.lower()):
                    filtered_internal.append(p)
            internal_projects = filtered_internal
            
            # Filter external projects
            filtered_external = []
            for p in external_projects:
                if (search_query_lower in p.ext_project_name.lower() or 
                    search_query_lower in p.ext_project_request_id.lower()):
                    filtered_external.append(p)
            external_projects = filtered_external
            
            print(f"After search: Found {len(internal_projects)} internal and {len(external_projects)} external projects")
        
        # Apply status filter
        if status_filter != 'all':
            # Filter internal projects by status
            internal_projects = [
                p for p in internal_projects 
                if internal_statuses.get(p.project_request_id) == status_filter
            ]
            
            # Filter external projects by status
            external_projects = [
                p for p in external_projects 
                if external_statuses.get(p.ext_project_request_id) == status_filter
            ]
        
        # Apply type filter
        if project_type == 'internal':
            external_projects = []
        elif project_type == 'external':
            internal_projects = []
        
        # Add to context
        context['internal_projects'] = internal_projects
        context['external_projects'] = external_projects
        context['project_type'] = project_type
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        context['internal_statuses'] = internal_statuses
        context['external_statuses'] = external_statuses
        
        return context