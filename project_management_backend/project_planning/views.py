from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
import logging
import uuid
from .models import ProjectPlanService

logger = logging.getLogger(__name__)

class ProjectPlanningView(TemplateView):
    template_name = 'project_planning/project_planning.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get all projects (both external and internal)
            projects = ProjectPlanService.get_all_projects()
            context['projects'] = projects
            
            # Count projects by type
            external_count = sum(1 for p in projects if p.get('project_type') == 'External')
            internal_count = sum(1 for p in projects if p.get('project_type') == 'Internal')
            
            context['external_count'] = external_count
            context['internal_count'] = internal_count
            context['total_count'] = len(projects)
            
            # Get project requests for dropdown
            project_requests = ProjectPlanService.get_project_requests()
            context['external_requests'] = project_requests['external']
            context['internal_requests'] = project_requests['internal']
            
            # Generate a new project request ID
            context['new_request_id'] = f"PROJ-{str(len(projects) + 1).zfill(3)}"
            
        except Exception as e:
            logger.error(f"Error retrieving project planning data: {str(e)}")
            context['error'] = str(e)
            context['projects'] = []
            context['external_requests'] = []
            context['internal_requests'] = []
            context['external_count'] = 0
            context['internal_count'] = 0
            context['total_count'] = 0
        
        return context
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', 'create')
        
        try:
            if action == 'create':
                # Create a new project plan
                result = ProjectPlanService.create_project_plan(request.POST)
                
                if result['success']:
                    messages.success(request, result['message'])
                else:
                    messages.error(request, result['message'])
            
            elif action == 'update':
                # Update an existing project plan
                tracking_id = request.POST.get('tracking_id')
                result = ProjectPlanService.update_project_plan(tracking_id, request.POST)
                
                if result['success']:
                    messages.success(request, result['message'])
                else:
                    messages.error(request, result['message'])
        
        except Exception as e:
            logger.error(f"Error processing project planning form: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
        
        return redirect('project_planning:index')


