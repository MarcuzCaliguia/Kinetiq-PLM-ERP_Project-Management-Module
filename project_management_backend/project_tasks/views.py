from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date, timedelta 
import json
from .models import InternalProjectTask, ExternalProjectTask
from .serializers import InternalProjectTaskSerializer, ExternalProjectTaskSerializer
from .forms import InternalTaskForm, ExternalTaskForm


def calendar_view(request):
    # Get all tasks
    internal_tasks = InternalProjectTask.objects.all()
    external_tasks = ExternalProjectTask.objects.all()
    
    # Convert to calendar events
    events = []
    
    for task in internal_tasks:
        status_color = {
            'pending': '#ffc107',  # warning
            'in_progress': '#0d6efd',  # primary
            'completed': '#198754',  # success
            'canceled': '#6c757d',  # secondary
        }.get(task.intrnl_task_status, '#6c757d')
        
        events.append({
            'id': task.intrnl_task_id,
            'title': f"[INT] {task.intrnl_task_id}",
            'start': task.intrnl_task_deadline.isoformat(),
            'url': reverse('task_detail', args=['internal', task.intrnl_task_id]),
            'backgroundColor': status_color,
            'borderColor': status_color,
            'description': task.intrnl_task_description,
            'type': 'internal',
        })
    
    for task in external_tasks:
        status_color = {
            'pending': '#ffc107',  # warning
            'in_progress': '#0d6efd',  # primary
            'completed': '#198754',  # success
            'canceled': '#6c757d',  # secondary
        }.get(task.task_status, '#6c757d')
        
        events.append({
            'id': task.task_id,
            'title': f"[EXT] {task.task_id}",
            'start': task.task_deadline.isoformat(),
            'url': reverse('task_detail', args=['external', task.task_id]),
            'backgroundColor': status_color,
            'borderColor': status_color,
            'description': task.task_description,
            'type': 'external',
        })
    
    context = {
        'events_json': json.dumps(events),
    }
    
    return render(request, 'project_tasks/calendar.html', context)

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

class InternalProjectTaskViewSet(viewsets.ModelViewSet):
    queryset = InternalProjectTask.objects.all()
    serializer_class = InternalProjectTaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['intrnl_task_id', 'intrnl_project_id', 'intrnl_task_description']
    ordering_fields = ['intrnl_task_deadline', 'intrnl_task_status', 'intrnl_project_id']
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        project_id = request.query_params.get('project_id', None)
        if project_id:
            tasks = self.queryset.filter(intrnl_project_id=project_id)
            serializer = self.get_serializer(tasks, many=True)
            return Response(serializer.data)
        return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        task_status = request.query_params.get('status', None)
        if task_status:
            tasks = self.queryset.filter(intrnl_task_status=task_status)
            serializer = self.get_serializer(tasks, many=True)
            return Response(serializer.data)
        return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def upcoming_deadlines(self, request):
        days = request.query_params.get('days', 7)
        try:
            days = int(days)
        except ValueError:
            return Response({"error": "Days must be a number"}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        deadline = today + timedelta(days=days)
        
        tasks = self.queryset.filter(
            intrnl_task_deadline__gte=today,
            intrnl_task_deadline__lte=deadline
        ).order_by('intrnl_task_deadline')
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status', None)
        
        if not new_status:
            return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        task.intrnl_task_status = new_status
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)

class ExternalProjectTaskViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectTask.objects.all()
    serializer_class = ExternalProjectTaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['task_id', 'project_id', 'task_description']
    ordering_fields = ['task_deadline', 'task_status', 'project_id']
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        project_id = request.query_params.get('project_id', None)
        if project_id:
            tasks = self.queryset.filter(project_id=project_id)
            serializer = self.get_serializer(tasks, many=True)
            return Response(serializer.data)
        return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        task_status = request.query_params.get('status', None)
        if task_status:
            tasks = self.queryset.filter(task_status=task_status)
            serializer = self.get_serializer(tasks, many=True)
            return Response(serializer.data)
        return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def upcoming_deadlines(self, request):
        days = request.query_params.get('days', 7)
        try:
            days = int(days)
        except ValueError:
            return Response({"error": "Days must be a number"}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        deadline = today + timedelta(days=days)
        
        tasks = self.queryset.filter(
            task_deadline__gte=today,
            task_deadline__lte=deadline
        ).order_by('task_deadline')
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status', None)
        
        if not new_status:
            return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        task.task_status = new_status
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
# API endpoints for dropdown data
def get_internal_projects(request):
    with connection.cursor() as cursor:
        # Check if the column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'project_management' 
            AND table_name = 'internal_project_details'
        """)
        columns = [col[0] for col in cursor.fetchall()]
        
        # Adjust query based on available columns
        if 'intrnl_project_name' in columns:
            cursor.execute("""
                SELECT intrnl_project_id, intrnl_project_name 
                FROM project_management.internal_project_details
                ORDER BY intrnl_project_id
            """)
        else:
            cursor.execute("""
                SELECT intrnl_project_id
                FROM project_management.internal_project_details
                ORDER BY intrnl_project_id
            """)
        
        projects = dictfetchall(cursor)
    return JsonResponse(projects, safe=False)

def get_external_projects(request):
    with connection.cursor() as cursor:
        # Check if the column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'project_management' 
            AND table_name = 'external_project_details'
        """)
        columns = [col[0] for col in cursor.fetchall()]
        
        # Adjust query based on available columns
        if 'project_name' in columns:
            cursor.execute("""
                SELECT project_id, project_name 
                FROM project_management.external_project_details
                ORDER BY project_id
            """)
        else:
            cursor.execute("""
                SELECT project_id
                FROM project_management.external_project_details
                ORDER BY project_id
            """)
        
        projects = dictfetchall(cursor)
    return JsonResponse(projects, safe=False)

def get_internal_labor(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT intrnl_project_labor_id, employee_id 
            FROM project_management.internal_project_labor
            ORDER BY intrnl_project_labor_id
        """)
        labor = dictfetchall(cursor)
    return JsonResponse(labor, safe=False)

def get_external_labor(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT project_labor_id, employee_id 
            FROM project_management.external_project_labor
            ORDER BY project_labor_id
        """)
        labor = dictfetchall(cursor)
    return JsonResponse(labor, safe=False)

# Enhanced task list view with pagination and filtering
def task_list(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    project_filter = request.GET.get('project', '')
    task_type_filter = request.GET.get('type', 'all')
    sort_by = request.GET.get('sort', 'deadline')
    
    # Get all tasks
    internal_tasks = InternalProjectTask.objects.all()
    external_tasks = ExternalProjectTask.objects.all()
    
    # Apply search filter
    if search_query:
        internal_tasks = internal_tasks.filter(
            intrnl_task_id__icontains=search_query
        ) | internal_tasks.filter(
            intrnl_project_id__icontains=search_query
        ) | internal_tasks.filter(
            intrnl_task_description__icontains=search_query
        )
        
        external_tasks = external_tasks.filter(
            task_id__icontains=search_query
        ) | external_tasks.filter(
            project_id__icontains=search_query
        ) | external_tasks.filter(
            task_description__icontains=search_query
        )
    
    # Apply status filter
    if status_filter:
        internal_tasks = internal_tasks.filter(intrnl_task_status=status_filter)
        external_tasks = external_tasks.filter(task_status=status_filter)
    
    # Apply project filter
    if project_filter:
        if project_filter.startswith('internal-'):
            project_id = project_filter.replace('internal-', '')
            internal_tasks = internal_tasks.filter(intrnl_project_id=project_id)
            external_tasks = ExternalProjectTask.objects.none()
        elif project_filter.startswith('external-'):
            project_id = project_filter.replace('external-', '')
            external_tasks = external_tasks.filter(project_id=project_id)
            internal_tasks = InternalProjectTask.objects.none()
    
    # Apply task type filter
    if task_type_filter == 'internal':
        external_tasks = ExternalProjectTask.objects.none()
    elif task_type_filter == 'external':
        internal_tasks = InternalProjectTask.objects.none()
    
    # Apply sorting
    if sort_by == 'deadline':
        internal_tasks = internal_tasks.order_by('intrnl_task_deadline')
        external_tasks = external_tasks.order_by('task_deadline')
    elif sort_by == 'deadline_desc':
        internal_tasks = internal_tasks.order_by('-intrnl_task_deadline')
        external_tasks = external_tasks.order_by('-task_deadline')
    elif sort_by == 'status':
        internal_tasks = internal_tasks.order_by('intrnl_task_status')
        external_tasks = external_tasks.order_by('task_status')
    elif sort_by == 'project':
        internal_tasks = internal_tasks.order_by('intrnl_project_id')
        external_tasks = external_tasks.order_by('project_id')
    
    # Get projects for dropdown
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT intrnl_project_id
            FROM project_management.internal_project_details
            ORDER BY intrnl_project_id
        """)
        internal_projects = dictfetchall(cursor)
        
        cursor.execute("""
            SELECT project_id
            FROM project_management.external_project_details
            ORDER BY project_id
        """)
        external_projects = dictfetchall(cursor)
    
    context = {
        'internal_tasks': internal_tasks,
        'external_tasks': external_tasks,
        'internal_projects': internal_projects,
        'external_projects': external_projects,
        'search_query': search_query,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'task_type_filter': task_type_filter,
        'sort_by': sort_by
    }
    return render(request, 'project_tasks/task_list.html', context)

# Enhanced task detail view with more information
def task_detail(request, task_type, task_id):
    if task_type == 'internal':
        task = get_object_or_404(InternalProjectTask, intrnl_task_id=task_id)
        
        # Get employee info
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT l.employee_id
                    FROM project_management.internal_project_labor l
                    WHERE l.intrnl_project_labor_id = %s
                """, [task.intrnl_project_labor_id])
                employee_info = dictfetchall(cursor)
                
                if employee_info and employee_info[0].get('employee_id'):
                    task.employee_id = employee_info[0].get('employee_id')
                    
                    # Try to get employee name from human_resources.employees and admin.users
                    try:
                        cursor.execute("""
                            SELECT e.first_name, e.last_name
                            FROM human_resources.employees e
                            WHERE e.employee_id = %s
                        """, [task.employee_id])
                        employee_name_info = dictfetchall(cursor)
                        
                        if employee_name_info:
                            first_name = employee_name_info[0].get('first_name', '')
                            last_name = employee_name_info[0].get('last_name', '')
                            task.employee_name = f"{first_name} {last_name}".strip()
                        else:
                            # Try to get from admin.users if not found in employees
                            cursor.execute("""
                                SELECT u.first_name, u.last_name
                                FROM admin.users u
                                WHERE u.employee_id = %s
                            """, [task.employee_id])
                            user_info = dictfetchall(cursor)
                            
                            if user_info:
                                first_name = user_info[0].get('first_name', '')
                                last_name = user_info[0].get('last_name', '')
                                task.employee_name = f"{first_name} {last_name}".strip()
                            else:
                                task.employee_name = 'Unknown Employee'
                    except Exception as e:
                        task.employee_name = f'Unknown (DB Error: {str(e)})'
                else:
                    task.employee_id = 'N/A'
                    task.employee_name = 'No Employee Assigned'
        except Exception as e:
            task.employee_id = 'Error'
            task.employee_name = f'Error: {str(e)}'
    else:
        task = get_object_or_404(ExternalProjectTask, task_id=task_id)
        
        # Get employee info
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT l.employee_id
                    FROM project_management.external_project_labor l
                    WHERE l.project_labor_id = %s
                """, [task.project_labor_id])
                employee_info = dictfetchall(cursor)
                
                if employee_info and employee_info[0].get('employee_id'):
                    task.employee_id = employee_info[0].get('employee_id')
                    
                    # Try to get employee name from human_resources.employees and admin.users
                    try:
                        cursor.execute("""
                            SELECT e.first_name, e.last_name
                            FROM human_resources.employees e
                            WHERE e.employee_id = %s
                        """, [task.employee_id])
                        employee_name_info = dictfetchall(cursor)
                        
                        if employee_name_info:
                            first_name = employee_name_info[0].get('first_name', '')
                            last_name = employee_name_info[0].get('last_name', '')
                            task.employee_name = f"{first_name} {last_name}".strip()
                        else:
                            # Try to get from admin.users if not found in employees
                            cursor.execute("""
                                SELECT u.first_name, u.last_name
                                FROM admin.users u
                                WHERE u.employee_id = %s
                            """, [task.employee_id])
                            user_info = dictfetchall(cursor)
                            
                            if user_info:
                                first_name = user_info[0].get('first_name', '')
                                last_name = user_info[0].get('last_name', '')
                                task.employee_name = f"{first_name} {last_name}".strip()
                            else:
                                task.employee_name = 'Unknown Employee'
                    except Exception as e:
                        task.employee_name = f'Unknown (DB Error: {str(e)})'
                else:
                    task.employee_id = 'N/A'
                    task.employee_name = 'No Employee Assigned'
        except Exception as e:
            task.employee_id = 'Error'
            task.employee_name = f'Error: {str(e)}'
    
    context = {
        'task': task,
        'task_type': task_type,
    }
    return render(request, 'project_tasks/task_detail.html', context)

# Enhanced form views with better validation and error handling
def new_internal_task(request):
    if request.method == 'POST':
        # Process form data with validation
        intrnl_project_id = request.POST.get('projectId')
        intrnl_task_description = request.POST.get('description', '')
        intrnl_task_status = request.POST.get('status')
        intrnl_task_deadline = request.POST.get('deadline')
        intrnl_project_labor_id = request.POST.get('laborId')
        
        # Validate required fields
        errors = {}
        if not intrnl_project_id:
            errors['projectId'] = 'Project ID is required'
        if not intrnl_task_status:
            errors['status'] = 'Status is required'
        if not intrnl_task_deadline:
            errors['deadline'] = 'Deadline is required'
        if not intrnl_project_labor_id:
            errors['laborId'] = 'Labor ID is required'
        
        # Validate deadline format
        try:
            deadline_date = parse_date(intrnl_task_deadline)
            if deadline_date is None:
                errors['deadline'] = 'Invalid date format'
        except:
            errors['deadline'] = 'Invalid date format'
        
        # If there are errors, return to form with error messages
        if errors:
            # Get projects for dropdown
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT intrnl_project_id
                    FROM project_management.internal_project_details
                    ORDER BY intrnl_project_id
                """)
                projects = dictfetchall(cursor)
                
                # Get labor for dropdown
                cursor.execute("""
                    SELECT intrnl_project_labor_id
                    FROM project_management.internal_project_labor
                    ORDER BY intrnl_project_labor_id
                """)
                labor = dictfetchall(cursor)
            
            context = {
                'projects': projects,
                'labor': labor,
                'errors': errors,
                'form_data': {
                    'projectId': intrnl_project_id,
                    'description': intrnl_task_description,
                    'status': intrnl_task_status,
                    'deadline': intrnl_task_deadline,
                    'laborId': intrnl_project_labor_id
                }
            }
            return render(request, 'project_tasks/new_internal_task.html', context)
        
        # Create new task with transaction
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO project_management.internal_project_task_list
                        (intrnl_project_id, intrnl_task_description, intrnl_task_status, intrnl_task_deadline, intrnl_project_labor_id)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING intrnl_task_id
                    """, [
                        intrnl_project_id,
                        intrnl_task_description,
                        intrnl_task_status,
                        intrnl_task_deadline,
                        intrnl_project_labor_id
                    ])
                    
                    result = cursor.fetchone()
                    task_id = result[0] if result else None
            
            messages.success(request, f'Internal task created successfully with ID: {task_id}')
            return redirect('task_list')
        except Exception as e:
            messages.error(request, f'Error creating task: {str(e)}')
            
            # Get projects for dropdown
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT intrnl_project_id
                    FROM project_management.internal_project_details
                    ORDER BY intrnl_project_id
                """)
                projects = dictfetchall(cursor)
                
                # Get labor for dropdown
                cursor.execute("""
                    SELECT intrnl_project_labor_id
                    FROM project_management.internal_project_labor
                    ORDER BY intrnl_project_labor_id
                """)
                labor = dictfetchall(cursor)
            
            context = {
                'projects': projects,
                'labor': labor,
                'form_data': {
                    'projectId': intrnl_project_id,
                    'description': intrnl_task_description,
                    'status': intrnl_task_status,
                    'deadline': intrnl_task_deadline,
                    'laborId': intrnl_project_labor_id
                }
            }
            return render(request, 'project_tasks/new_internal_task.html', context)
    
    # Get projects for dropdown
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT intrnl_project_id
            FROM project_management.internal_project_details
            ORDER BY intrnl_project_id
        """)
        projects = dictfetchall(cursor)
        
        # Get labor for dropdown
        cursor.execute("""
            SELECT intrnl_project_labor_id
            FROM project_management.internal_project_labor
            ORDER BY intrnl_project_labor_id
        """)
        labor = dictfetchall(cursor)
    
    context = {
        'projects': projects,
        'labor': labor,
    }
    return render(request, 'project_tasks/new_internal_task.html', context)

def new_external_task(request):
    if request.method == 'POST':
        # Process form data with validation
        project_id = request.POST.get('projectId')
        task_description = request.POST.get('description', '')
        task_status = request.POST.get('status')
        task_deadline = request.POST.get('deadline')
        project_labor_id = request.POST.get('laborId')
        
        # Validate required fields
        errors = {}
        if not project_id:
            errors['projectId'] = 'Project ID is required'
        if not task_status:
            errors['status'] = 'Status is required'
        if not task_deadline:
            errors['deadline'] = 'Deadline is required'
        if not project_labor_id:
            errors['laborId'] = 'Labor ID is required'
        
        # Validate deadline format
        try:
            deadline_date = parse_date(task_deadline)
            if deadline_date is None:
                errors['deadline'] = 'Invalid date format'
        except:
            errors['deadline'] = 'Invalid date format'
        
        # If there are errors, return to form with error messages
        if errors:
            # Get projects for dropdown
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT project_id
                    FROM project_management.external_project_details
                    ORDER BY project_id
                """)
                projects = dictfetchall(cursor)
                
                # Get labor for dropdown
                cursor.execute("""
                    SELECT project_labor_id
                    FROM project_management.external_project_labor
                    ORDER BY project_labor_id
                """)
                labor = dictfetchall(cursor)
            
            context = {
                'projects': projects,
                'labor': labor,
                'errors': errors,
                'form_data': {
                    'projectId': project_id,
                    'description': task_description,
                    'status': task_status,
                    'deadline': task_deadline,
                    'laborId': project_labor_id
                }
            }
            return render(request, 'project_tasks/new_external_task.html', context)
        
        # Create new task with transaction
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO project_management.external_project_task_list
                        (project_id, task_description, task_status, task_deadline, project_labor_id)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING task_id
                    """, [
                        project_id,
                        task_description,
                        task_status,
                        task_deadline,
                        project_labor_id
                    ])
                    
                    result = cursor.fetchone()
                    task_id = result[0] if result else None
            
            messages.success(request, f'External task created successfully with ID: {task_id}')
            return redirect('task_list')
        except Exception as e:
            messages.error(request, f'Error creating task: {str(e)}')
            
            # Get projects for dropdown
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT project_id
                    FROM project_management.external_project_details
                    ORDER BY project_id
                """)
                projects = dictfetchall(cursor)
                
                # Get labor for dropdown
                cursor.execute("""
                    SELECT project_labor_id
                    FROM project_management.external_project_labor
                    ORDER BY project_labor_id
                """)
                labor = dictfetchall(cursor)
            
            context = {
                'projects': projects,
                'labor': labor,
                'form_data': {
                    'projectId': project_id,
                    'description': task_description,
                    'status': task_status,
                    'deadline': task_deadline,
                    'laborId': project_labor_id
                }
            }
            return render(request, 'project_tasks/new_external_task.html', context)
    
    # Get projects for dropdown
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT project_id
            FROM project_management.external_project_details
            ORDER BY project_id
        """)
        projects = dictfetchall(cursor)
        
        # Get labor for dropdown
        cursor.execute("""
            SELECT project_labor_id
            FROM project_management.external_project_labor
            ORDER BY project_labor_id
        """)
        labor = dictfetchall(cursor)
    
    context = {
        'projects': projects,
        'labor': labor,
    }
    return render(request, 'project_tasks/new_external_task.html', context)

def edit_task(request, task_type, task_id):
    # Get the task
    if task_type == 'internal':
        task = get_object_or_404(InternalProjectTask, intrnl_task_id=task_id)
        
        if request.method == 'POST':
            # Process form data with validation
            intrnl_project_id = request.POST.get('projectId')
            intrnl_task_description = request.POST.get('description', '')
            intrnl_task_status = request.POST.get('status')
            intrnl_task_deadline = request.POST.get('deadline')
            intrnl_project_labor_id = request.POST.get('laborId')
            
            # Validate required fields
            errors = {}
            if not intrnl_project_id:
                errors['projectId'] = 'Project ID is required'
            if not intrnl_task_status:
                errors['status'] = 'Status is required'
            if not intrnl_task_deadline:
                errors['deadline'] = 'Deadline is required'
            if not intrnl_project_labor_id:
                errors['laborId'] = 'Labor ID is required'
            
            # Validate deadline format
            try:
                deadline_date = parse_date(intrnl_task_deadline)
                if deadline_date is None:
                    errors['deadline'] = 'Invalid date format'
            except:
                errors['deadline'] = 'Invalid date format'
            
            # If there are errors, return to form with error messages
            if errors:
                # Get projects for dropdown
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT intrnl_project_id
                        FROM project_management.internal_project_details
                        ORDER BY intrnl_project_id
                    """)
                    projects = dictfetchall(cursor)
                    
                    # Get labor for dropdown
                    cursor.execute("""
                        SELECT intrnl_project_labor_id
                        FROM project_management.internal_project_labor
                        ORDER BY intrnl_project_labor_id
                    """)
                    labor = dictfetchall(cursor)
                
                context = {
                    'task': task,
                    'task_type': task_type,
                    'projects': projects,
                    'labor': labor,
                    'errors': errors,
                    'form_data': {
                        'projectId': intrnl_project_id,
                        'description': intrnl_task_description,
                        'status': intrnl_task_status,
                        'deadline': intrnl_task_deadline,
                        'laborId': intrnl_project_labor_id
                    }
                }
                return render(request, 'project_tasks/edit_task.html', context)
            
            # Update task with transaction
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE project_management.internal_project_task_list
                            SET intrnl_project_id = %s, 
                                intrnl_task_description = %s, 
                                intrnl_task_status = %s, 
                                intrnl_task_deadline = %s, 
                                intrnl_project_labor_id = %s
                            WHERE intrnl_task_id = %s
                        """, [
                            intrnl_project_id,
                            intrnl_task_description,
                            intrnl_task_status,
                            intrnl_task_deadline,
                            intrnl_project_labor_id,
                            task_id
                        ])
                
                messages.success(request, f'Internal task updated successfully: {task_id}')
                return redirect('task_detail', task_type=task_type, task_id=task_id)
            except Exception as e:
                messages.error(request, f'Error updating task: {str(e)}')
                
                # Get projects for dropdown
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT intrnl_project_id
                        FROM project_management.internal_project_details
                        ORDER BY intrnl_project_id
                    """)
                    projects = dictfetchall(cursor)
                    
                    # Get labor for dropdown
                    cursor.execute("""
                        SELECT intrnl_project_labor_id
                        FROM project_management.internal_project_labor
                        ORDER BY intrnl_project_labor_id
                    """)
                    labor = dictfetchall(cursor)
                
                context = {
                    'task': task,
                    'task_type': task_type,
                    'projects': projects,
                    'labor': labor,
                    'form_data': {
                        'projectId': intrnl_project_id,
                        'description': intrnl_task_description,
                        'status': intrnl_task_status,
                        'deadline': intrnl_task_deadline,
                        'laborId': intrnl_project_labor_id
                    }
                }
                return render(request, 'project_tasks/edit_task.html', context)
        
        # Get projects for dropdown
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT intrnl_project_id
                FROM project_management.internal_project_details
                ORDER BY intrnl_project_id
            """)
            projects = dictfetchall(cursor)
            
            # Get labor for dropdown
            cursor.execute("""
                SELECT intrnl_project_labor_id
                FROM project_management.internal_project_labor
                ORDER BY intrnl_project_labor_id
            """)
            labor = dictfetchall(cursor)
        
        context = {
            'task': task,
            'task_type': task_type,
            'projects': projects,
            'labor': labor,
            'form_data': {
                'projectId': task.intrnl_project_id,
                'description': task.intrnl_task_description,
                'status': task.intrnl_task_status,
                'deadline': task.intrnl_task_deadline,
                'laborId': task.intrnl_project_labor_id
            }
        }
    else:
        task = get_object_or_404(ExternalProjectTask, task_id=task_id)
        
        if request.method == 'POST':
            # Process form data with validation
            project_id = request.POST.get('projectId')
            task_description = request.POST.get('description', '')
            task_status = request.POST.get('status')
            task_deadline = request.POST.get('deadline')
            project_labor_id = request.POST.get('laborId')
            
            # Validate required fields
            errors = {}
            if not project_id:
                errors['projectId'] = 'Project ID is required'
            if not task_status:
                errors['status'] = 'Status is required'
            if not task_deadline:
                errors['deadline'] = 'Deadline is required'
            if not project_labor_id:
                errors['laborId'] = 'Labor ID is required'
            
            # Validate deadline format
            try:
                deadline_date = parse_date(task_deadline)
                if deadline_date is None:
                    errors['deadline'] = 'Invalid date format'
            except:
                errors['deadline'] = 'Invalid date format'
            
            # If there are errors, return to form with error messages
            if errors:
                # Get projects for dropdown
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT project_id
                        FROM project_management.external_project_details
                        ORDER BY project_id
                    """)
                    projects = dictfetchall(cursor)
                    
                    # Get labor for dropdown
                    cursor.execute("""
                        SELECT project_labor_id
                        FROM project_management.external_project_labor
                        ORDER BY project_labor_id
                    """)
                    labor = dictfetchall(cursor)
                
                context = {
                    'task': task,
                    'task_type': task_type,
                    'projects': projects,
                    'labor': labor,
                    'errors': errors,
                    'form_data': {
                        'projectId': project_id,
                        'description': task_description,
                        'status': task_status,
                        'deadline': task_deadline,
                        'laborId': project_labor_id
                    }
                }
                return render(request, 'project_tasks/edit_task.html', context)
            
            # Update task with transaction
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE project_management.external_project_task_list
                            SET project_id = %s, 
                                task_description = %s, 
                                task_status = %s, 
                                task_deadline = %s, 
                                project_labor_id = %s
                            WHERE task_id = %s
                        """, [
                            project_id,
                            task_description,
                            task_status,
                            task_deadline,
                            project_labor_id,
                            task_id
                        ])
                
                messages.success(request, f'External task updated successfully: {task_id}')
                return redirect('task_detail', task_type=task_type, task_id=task_id)
            except Exception as e:
                messages.error(request, f'Error updating task: {str(e)}')
                
                # Get projects for dropdown
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT project_id
                        FROM project_management.external_project_details
                        ORDER BY project_id
                    """)
                    projects = dictfetchall(cursor)
                    
                    # Get labor for dropdown
                    cursor.execute("""
                        SELECT project_labor_id
                        FROM project_management.external_project_labor
                        ORDER BY project_labor_id
                    """)
                    labor = dictfetchall(cursor)
                
                context = {
                    'task': task,
                    'task_type': task_type,
                    'projects': projects,
                    'labor': labor,
                    'form_data': {
                        'projectId': project_id,
                        'description': task_description,
                        'status': task_status,
                        'deadline': task_deadline,
                        'laborId': project_labor_id
                    }
                }
                return render(request, 'project_tasks/edit_task.html', context)
        
        # Get projects for dropdown
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT project_id
                FROM project_management.external_project_details
                ORDER BY project_id
            """)
            projects = dictfetchall(cursor)
            
            # Get labor for dropdown
            cursor.execute("""
                SELECT project_labor_id
                FROM project_management.external_project_labor
                ORDER BY project_labor_id
            """)
            labor = dictfetchall(cursor)
        
        context = {
            'task': task,
            'task_type': task_type,
            'projects': projects,
            'labor': labor,
            'form_data': {
                'projectId': task.project_id,
                'description': task.task_description,
                'status': task.task_status,
                'deadline': task.task_deadline,
                'laborId': task.project_labor_id
            }
        }
    
    return render(request, 'project_tasks/edit_task.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_delete_tasks(request):
    task_ids = request.data.get('task_ids', [])
    task_types = request.data.get('task_types', [])
    
    if not task_ids or not task_types:
        return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(task_ids) != len(task_types):
        return Response({"error": "Task IDs and types must have the same length"}, status=status.HTTP_400_BAD_REQUEST)
    
    results = []
    errors = []
    
    for i, task_id in enumerate(task_ids):
        task_type = task_types[i]
        
        try:
            if task_type == 'internal':
                task = InternalProjectTask.objects.get(intrnl_task_id=task_id)
                task.delete()
            else:
                task = ExternalProjectTask.objects.get(task_id=task_id)
                task.delete()
            
            results.append({
                'task_id': task_id,
                'task_type': task_type,
                'status': 'deleted'
            })
        except Exception as e:
            errors.append({
                'task_id': task_id,
                'task_type': task_type,
                'error': str(e)
            })
    
    return Response({
        'results': results,
        'errors': errors
    })