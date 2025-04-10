from django.views.generic import TemplateView
from django.views import View
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
import logging
import uuid
from .models import DashboardService

logger = logging.getLogger(__name__)

class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get overdue tasks
            overdue_tasks = DashboardService.get_overdue_tasks()
            logger.info(f"Retrieved {len(overdue_tasks)} overdue tasks")
            context['overdue_tasks'] = overdue_tasks
            
            # Get today's tasks
            today_tasks = DashboardService.get_today_tasks()
            logger.info(f"Retrieved {len(today_tasks)} tasks for today")
            context['today_tasks'] = today_tasks
            
            # Get project summary
            projects = DashboardService.get_project_summary()
            logger.info(f"Retrieved {len(projects)} projects for summary")
            context['projects'] = projects
            
        except Exception as e:
            # Log the error
            logger.error(f"Error retrieving dashboard data: {str(e)}", exc_info=True)
            context['error'] = f"Error retrieving data: {str(e)}"
            # Initialize empty lists to prevent template errors
            context['overdue_tasks'] = []
            context['today_tasks'] = []
            context['projects'] = []
        
        return context

class ContractualWorkerRequestView(TemplateView):
    template_name = 'dashboard/contractual_worker_requests.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get contractual worker requests directly in the view
            contractual_requests = self.get_contractual_worker_requests()
            logger.info(f"Retrieved {len(contractual_requests)} contractual worker requests")
            context['contractual_requests'] = contractual_requests
            
            # Get departments for dropdown
            context['departments'] = self.get_departments()
            
            # Get projects for dropdown
            context['projects'] = self.get_internal_projects()
            
        except Exception as e:
            # Log the error
            logger.error(f"Error retrieving contractual worker requests: {str(e)}", exc_info=True)
            context['error'] = f"Error retrieving data: {str(e)}"
            # Initialize empty lists to prevent template errors
            context['contractual_requests'] = []
            context['departments'] = []
            context['projects'] = []
        
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            # Generate a unique request ID
            request_id = f"CWR-{uuid.uuid4().hex[:8].upper()}"
            
            # Extract data from the form
            job_title = request.POST.get('job_title', '')
            job_description = request.POST.get('job_description', '')
            required_position = request.POST.get('required_position', '')
            employment_type = request.POST.get('employment_type', '')
            dept_id = request.POST.get('department', '')
            project_id = request.POST.get('project_id', '')
            
            # Valid employment types based on database schema
            valid_types = ["fixed-term", "temporary employment", "freelance", "internships"]
            
            # Check if employment_type is valid
            if employment_type not in valid_types:
                logger.warning(f"Invalid employment type: {employment_type}")
                # Default to "fixed-term" if invalid
                employment_type = "fixed-term"
                logger.info(f"Using default employment type: {employment_type}")
            
            # Insert new request into database
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO contractual_worker_request 
                    (request_id, job_title, job_description, required_position, employment_type, dept_id, intrnl_project_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [
                    request_id, 
                    job_title, 
                    job_description, 
                    required_position, 
                    employment_type,
                    dept_id if dept_id else None, 
                    project_id if project_id else None
                ])
            
            logger.info(f"Created new contractual worker request with ID: {request_id}")
            messages.success(request, f"Request created successfully with ID: {request_id}")
            
        except Exception as e:
            logger.error(f"Error creating contractual worker request: {str(e)}", exc_info=True)
            messages.error(request, f"An error occurred: {str(e)}")
        
        # Redirect back to the same page to display the updated list
        return redirect('dashboard:contractual_requests')
    
    def get_contractual_worker_requests(self):
        """Get all contractual worker requests with related project information using raw SQL"""
        contractual_requests = []
        
        try:
            # Use raw SQL to get contractual worker requests
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        cwr.request_id, 
                        cwr.job_title, 
                        cwr.job_description, 
                        cwr.required_position, 
                        cwr.employment_type,
                        cwr.dept_id,
                        cwr.intrnl_project_id,
                        ipd.intrnl_project_status,
                        ipr.project_name,
                        d.dept_name
                    FROM 
                        contractual_worker_request cwr
                    LEFT JOIN 
                        internal_project_details ipd ON cwr.intrnl_project_id = ipd.intrnl_project_id
                    LEFT JOIN 
                        internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
                    LEFT JOIN 
                        departments d ON cwr.dept_id = d.dept_id
                    ORDER BY 
                        cwr.request_id
                """)
                
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                
                logger.info(f"Found {len(rows)} contractual worker requests")
                
                for row in rows:
                    # Convert row to dictionary
                    row_dict = dict(zip(columns, row))
                    
                    # Add formatted data to the list
                    contractual_requests.append({
                        'request_id': row_dict.get('request_id', 'N/A'),
                        'project_id': row_dict.get('intrnl_project_id', 'N/A'),
                        'project_name': row_dict.get('project_name', 'N/A'),
                        'project_status': row_dict.get('intrnl_project_status', 'N/A'),
                        'job_title': row_dict.get('job_title', 'N/A'),
                        'job_description': row_dict.get('job_description', 'No description provided'),
                        'required_position': row_dict.get('required_position', 'N/A'),
                        'employment_type': row_dict.get('employment_type', 'N/A'),
                        'department': row_dict.get('dept_name', 'N/A')
                    })
        
        except Exception as e:
            logger.error(f"Error in get_contractual_worker_requests: {str(e)}", exc_info=True)
            contractual_requests = []
        
        return contractual_requests
    
    def get_departments(self):
        """Get all departments for dropdown selection"""
        departments = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT dept_id, dept_name FROM departments ORDER BY dept_name")
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    departments.append(dict(zip(columns, row)))
        except Exception as e:
            logger.error(f"Error getting departments: {str(e)}")
        
        return departments
    
    def get_internal_projects(self):
        """Get active internal projects for dropdown selection"""
        projects = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ipd.intrnl_project_id, 
                        ipr.project_name
                    FROM 
                        internal_project_details ipd
                    JOIN 
                        internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
                    WHERE 
                        ipd.intrnl_project_status IN ('in progress', 'ongoing', 'In Progress', 'Ongoing', 'active', 'Active')
                    ORDER BY 
                        ipr.project_name
                """)
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    projects.append(dict(zip(columns, row)))
        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
        
        return projects

class ProjectCostManagementView(TemplateView):
    template_name = 'dashboard/project_cost_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get project cost data
            cost_data = self.get_project_cost_data()
            logger.info(f"Retrieved cost data for {len(cost_data)} projects")
            context['cost_data'] = cost_data
            
            # Get external projects for dropdown
            context['projects'] = self.get_external_projects()
            
        except Exception as e:
            # Log the error
            logger.error(f"Error retrieving cost management data: {str(e)}", exc_info=True)
            context['error'] = f"Error retrieving data: {str(e)}"
            # Initialize empty lists to prevent template errors
            context['cost_data'] = []
            context['projects'] = []
        
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            # Generate unique IDs
            project_resources_id = f"RES-{uuid.uuid4().hex[:8].upper()}"
            cost_id = f"COST-{uuid.uuid4().hex[:8].upper()}"
            
            # Extract data from the form
            project_id = request.POST.get('project_id', '')
            approval_status = request.POST.get('approval_status', 'pending')
            
            # Insert new cost record into database
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO external_project_cost_management 
                    (project_resources_id, project_id, cost_id, project_budget_approval)
                    VALUES (%s, %s, %s, %s)
                """, [
                    project_resources_id, 
                    project_id if project_id else None,
                    cost_id,
                    approval_status
                ])
            
            logger.info(f"Created new cost management record with ID: {project_resources_id}")
            messages.success(request, f"Cost management record created successfully")
            
        except Exception as e:
            logger.error(f"Error creating cost management record: {str(e)}", exc_info=True)
            messages.error(request, f"An error occurred: {str(e)}")
        
        # Redirect back to the same page to display the updated list
        return redirect('dashboard:project_costs')
    
    def get_project_cost_data(self):
        """Get project cost data with related information"""
        cost_data = []
        
        try:
            # Use raw SQL to get cost management data
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        epcm.project_resources_id, 
                        epcm.cost_id, 
                        epcm.project_budget_approval,
                        epd.project_id,
                        epr.ext_project_name,
                        epd.project_status
                    FROM 
                        external_project_cost_management epcm
                    LEFT JOIN 
                        external_project_details epd ON epcm.project_id = epd.project_id
                    LEFT JOIN 
                        external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
                    ORDER BY 
                        epcm.project_resources_id
                """)
                
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                
                logger.info(f"Found {len(rows)} cost management records")
                
                for row in rows:
                    # Convert row to dictionary
                    row_dict = dict(zip(columns, row))
                    
                    # Format approval status
                    approval_status = row_dict.get('project_budget_approval', 'pending')
                    
                    # Add formatted data to the list
                    cost_data.append({
                        'project_resources_id': row_dict.get('project_resources_id', 'N/A'),
                        'cost_id': row_dict.get('cost_id', 'N/A'),
                        'project_id': row_dict.get('project_id', 'N/A'),
                        'project_name': row_dict.get('ext_project_name', 'N/A'),
                        'project_status': row_dict.get('project_status', 'N/A'),
                        'approval_status': approval_status
                    })
        
        except Exception as e:
            logger.error(f"Error in get_project_cost_data: {str(e)}", exc_info=True)
            cost_data = []
        
        return cost_data
    
    def get_external_projects(self):
        """Get external projects for dropdown selection"""
        projects = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        epd.project_id, 
                        epr.ext_project_name
                    FROM 
                        external_project_details epd
                    JOIN 
                        external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
                    ORDER BY 
                        epr.ext_project_name
                """)
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    projects.append(dict(zip(columns, row)))
        except Exception as e:
            logger.error(f"Error getting external projects: {str(e)}")
        
        return projects