from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection
from datetime import datetime, timedelta
import traceback

@api_view(['GET'])
def get_overdue_tasks(request):
    try:
        today = datetime.now().date()
        
        # Use raw SQL to query the normalized database structure
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pt.task_id,
                    pt.task_description,
                    pt.task_deadline,
                    pt.task_status,
                    pt.project_id,
                    pt.intrnl_project_id,
                    pt.project_labor_id,
                    pl.employee_id,
                    COALESCE(e.first_name || ' ' || e.last_name, 'Unassigned') as employee_name
                FROM 
                    project_management.project_tasks pt
                LEFT JOIN 
                    project_management.project_labor pl ON pt.project_labor_id = pl.project_labor_id
                LEFT JOIN 
                    human_resources.employees e ON pl.employee_id = e.employee_id
                WHERE 
                    pt.task_deadline < %s
                    AND pt.task_status NOT IN ('completed', 'canceled')
                ORDER BY 
                    pt.task_deadline ASC
            """, [today])
            
            overdue_tasks = []
            for row in cursor.fetchall():
                task_id, task_description, task_deadline, task_status, project_id, intrnl_project_id, project_labor_id, employee_id, employee_name = row
                
                overdue_days = (today - task_deadline).days
                
                overdue_tasks.append({
                    'Overdue': f"{overdue_days} days",
                    'Task': task_description,
                    'Deadline': task_deadline.strftime('%Y-%m-%d'),
                    'Employee': employee_name,
                    'ProjectID': project_id or intrnl_project_id,
                    'TaskID': task_id
                })
                
        return Response(overdue_tasks)
    except Exception as e:
        print(f"Error fetching overdue tasks: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_today_tasks(request):
    try:
        today = datetime.now().date()
        
        # Use raw SQL to query the normalized database structure
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pt.task_id,
                    pt.task_description,
                    pt.task_status,
                    pt.project_id,
                    pt.intrnl_project_id,
                    COALESCE(epr.ext_project_name, ipr.project_name, 'Unknown Project') as project_name
                FROM 
                    project_management.project_tasks pt
                LEFT JOIN 
                    project_management.external_project_details epd ON pt.project_id = epd.project_id
                LEFT JOIN 
                    project_management.external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
                LEFT JOIN 
                    project_management.internal_project_details ipd ON pt.intrnl_project_id = ipd.intrnl_project_id
                LEFT JOIN 
                    project_management.internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
                WHERE 
                    pt.task_deadline = %s
                ORDER BY 
                    pt.task_status
            """, [today])
            
            today_tasks = []
            for row in cursor.fetchall():
                task_id, task_description, task_status, project_id, intrnl_project_id, project_name = row
                
                today_tasks.append({
                    'Task': task_description,
                    'ProjectID': project_id or intrnl_project_id,
                    'ProjectName': project_name,
                    'Status': task_status,
                    'TaskID': task_id
                })
                
        return Response(today_tasks)
    except Exception as e:
        print(f"Error fetching today's tasks: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_project_summary(request):
    try:
        # Use raw SQL to query the normalized database structure
        with connection.cursor() as cursor:
            # External projects
            cursor.execute("""
                SELECT 
                    epd.project_id,
                    epr.ext_project_name,
                    epd.project_status,
                    epd.start_date,
                    epd.estimated_end_date,
                    epd.project_issues IS NOT NULL AND epd.project_issues != '' as has_issues
                FROM 
                    project_management.external_project_details epd
                LEFT JOIN 
                    project_management.external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
                ORDER BY 
                    epd.start_date DESC NULLS LAST
            """)
            
            external_projects = []
            for row in cursor.fetchall():
                project_id, project_name, status, start_date, end_date, has_issues = row
                
                external_projects.append({
                    'id': project_id,
                    'projectId': project_name or "Unnamed Project",
                    'type': 'External',
                    'startDate': start_date.strftime('%Y-%m-%d') if start_date else 'Not set',
                    'endDate': end_date.strftime('%Y-%m-%d') if end_date else 'Not set',
                    'status': status,
                    'issue': has_issues
                })
            
            # Internal projects
            cursor.execute("""
                SELECT 
                    ipd.intrnl_project_id,
                    ipr.project_name,
                    ipd.intrnl_project_status,
                    ipd.start_date,
                    ipd.estimated_end_date,
                    ipd.project_issues IS NOT NULL AND ipd.project_issues != '' as has_issues
                FROM 
                    project_management.internal_project_details ipd
                LEFT JOIN 
                    project_management.internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
                ORDER BY 
                    ipd.start_date DESC NULLS LAST
            """)
            
            internal_projects = []
            for row in cursor.fetchall():
                project_id, project_name, status, start_date, end_date, has_issues = row
                
                internal_projects.append({
                    'id': project_id,
                    'projectId': project_name or "Unnamed Project",
                    'type': 'Internal',
                    'startDate': start_date.strftime('%Y-%m-%d') if start_date else 'Not set',
                    'endDate': end_date.strftime('%Y-%m-%d') if end_date else 'Not set',
                    'status': status,
                    'issue': has_issues
                })
                
        # Combine both project types
        all_projects = external_projects + internal_projects
                
        return Response(all_projects)
    except Exception as e:
        print(f"Error fetching project summary: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_project_detail(request, project_type, project_id):
    try:
        if project_type == 'External':
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        epd.project_id,
                        epr.ext_project_name,
                        epr.ext_project_description,
                        epd.project_status,
                        epd.project_milestone,
                        epd.start_date,
                        epd.estimated_end_date,
                        epd.warranty_coverage_yr,
                        epd.warranty_start_date,
                        epd.warranty_end_date,
                        epd.project_issues
                    FROM 
                        project_management.external_project_details epd
                    LEFT JOIN 
                        project_management.external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
                    WHERE 
                        epd.project_id = %s
                """, [project_id])
                
                row = cursor.fetchone()
                if not row:
                    return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
                    
                project_id, project_name, project_description, project_status, milestone, start_date, end_date, warranty_yr, warranty_start, warranty_end, issues = row
                
                # Get tasks for this project
                cursor.execute("""
                    SELECT 
                        task_id,
                        task_description,
                        task_status,
                        task_deadline
                    FROM 
                        project_management.project_tasks
                    WHERE 
                        project_id = %s
                    ORDER BY 
                        task_deadline
                """, [project_id])
                
                tasks = []
                for task_row in cursor.fetchall():
                    task_id, task_desc, task_status, task_deadline = task_row
                    tasks.append({
                        'id': task_id,
                        'description': task_desc,
                        'status': task_status,
                        'deadline': task_deadline.strftime('%Y-%m-%d') if task_deadline else None
                    })
                
                # Get labor assignments for this project
                cursor.execute("""
                    SELECT 
                        pl.project_labor_id,
                        pl.job_role_needed,
                        pl.employee_id,
                        COALESCE(e.first_name || ' ' || e.last_name, 'Unassigned') as employee_name
                    FROM 
                        project_management.project_labor pl
                    LEFT JOIN 
                        human_resources.employees e ON pl.employee_id = e.employee_id
                    WHERE 
                        pl.project_id = %s
                """, [project_id])
                
                labor = []
                for labor_row in cursor.fetchall():
                    labor_id, job_role, emp_id, emp_name = labor_row
                    labor.append({
                        'id': labor_id,
                        'role': job_role,
                        'employeeId': emp_id,
                        'employeeName': emp_name
                    })
                
                result = {
                    'project_tracking_id': project_id,
                    'project_id': project_id,
                    'project_name': project_name,
                    'project_description': project_description,
                    'project_status': project_status,
                    'project_milestone': milestone,
                    'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                    'estimated_end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
                    'warranty_coverage_yr': warranty_yr,
                    'warranty_start_date': warranty_start.strftime('%Y-%m-%d') if warranty_start else None,
                    'warranty_end_date': warranty_end.strftime('%Y-%m-%d') if warranty_end else None,
                    'project_issues': issues,
                    'tasks': tasks,
                    'labor': labor
                }
                
        elif project_type == 'Internal':
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ipd.intrnl_project_id,
                        ipr.project_name,
                        ipd.intrnl_project_status,
                        ipd.start_date,
                        ipd.estimated_end_date,
                        ipd.approval_id,
                        ipd.project_issues
                    FROM 
                        project_management.internal_project_details ipd
                    LEFT JOIN 
                        project_management.internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
                    WHERE 
                        ipd.intrnl_project_id = %s
                """, [project_id])
                                
                row = cursor.fetchone()
                if not row:
                    return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
                    
                project_id, project_name, project_status, start_date, end_date, approval_id, issues = row
                
                # Get tasks for this project
                cursor.execute("""
                    SELECT 
                        task_id,
                        task_description,
                        task_status,
                        task_deadline
                    FROM 
                        project_management.project_tasks
                    WHERE 
                        intrnl_project_id = %s
                    ORDER BY 
                        task_deadline
                """, [project_id])
                
                tasks = []
                for task_row in cursor.fetchall():
                    task_id, task_desc, task_status, task_deadline = task_row
                    tasks.append({
                        'id': task_id,
                        'description': task_desc,
                        'status': task_status,
                        'deadline': task_deadline.strftime('%Y-%m-%d') if task_deadline else None
                    })
                
                # Get labor assignments for this project - now using project_labor table
                cursor.execute("""
                    SELECT 
                        pl.project_labor_id,
                        pl.job_role_needed,
                        pl.employee_id,
                        COALESCE(e.first_name || ' ' || e.last_name, 'Unassigned') as employee_name
                    FROM 
                        project_management.project_labor pl
                    LEFT JOIN 
                        human_resources.employees e ON pl.employee_id = e.employee_id
                    WHERE 
                        pl.intrnl_project_id = %s
                """, [project_id])
                
                labor = []
                for labor_row in cursor.fetchall():
                    labor_id, job_role, emp_id, emp_name = labor_row
                    labor.append({
                        'id': labor_id,
                        'role': job_role,
                        'employeeId': emp_id,
                        'employeeName': emp_name
                    })
                
                result = {
                    'intrnl_project_tracking_id': project_id,
                    'intrnl_project_id': project_id,
                    'project_name': project_name,
                    'project_description': "No description available",  # Providing a default since the column doesn't exist
                    'intrnl_project_status': project_status,
                    'intrnl_start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                    'intrnl_estimated_end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
                    'budget': None,
                    'budget_description': None,
                    'approval_id': approval_id,
                    'intrnl_project_issue': issues,
                    'tasks': tasks,
                    'labor': labor
                }
        else:
            return Response({'error': 'Invalid project type'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
    except Exception as e:
        print(f"Error fetching project detail: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_task_status(request, task_id):
    try:
        new_status = request.data.get('status')
        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE project_management.project_tasks
                SET task_status = %s
                WHERE task_id = %s
                RETURNING task_id
            """, [new_status, task_id])
            
            if cursor.rowcount == 0:
                return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
                
        return Response({'message': 'Task status updated successfully'})
    except Exception as e:
        print(f"Error updating task status: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_project_task(request):
    try:
        project_id = request.data.get('project_id')
        intrnl_project_id = request.data.get('intrnl_project_id')
        task_description = request.data.get('task_description')
        task_deadline = request.data.get('task_deadline')
        task_status = request.data.get('task_status', 'not started')
        project_labor_id = request.data.get('project_labor_id')
        
        if not task_description:
            return Response({'error': 'Task description is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not task_deadline:
            return Response({'error': 'Task deadline is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not (project_id or intrnl_project_id):
            return Response({'error': 'Either project_id or intrnl_project_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # The task_id will be generated by the database trigger
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO project_management.project_tasks
                (project_id, intrnl_project_id, task_description, task_status, task_deadline, project_labor_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING task_id
            """, [project_id, intrnl_project_id, task_description, task_status, task_deadline, project_labor_id])
            
            result = cursor.fetchone()
            if not result:
                return Response({'error': 'Failed to create task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            task_id = result[0]
                
        return Response({
            'task_id': task_id,
            'message': 'Task created successfully'
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"Error adding project task: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)