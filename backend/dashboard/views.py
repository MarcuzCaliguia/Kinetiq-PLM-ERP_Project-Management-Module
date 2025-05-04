from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection
from datetime import datetime, timedelta
import traceback
import logging

logger = logging.getLogger(__name__)


def db_operation(operation_description):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                logger.info(f"Starting {operation_description}")
                result = func(*args, **kwargs)
                logger.info(f"Completed {operation_description}")
                return result
            except Exception as e:
                logger.error(f"Error {operation_description}: {str(e)}")
                logger.error(traceback.format_exc())
                return Response(
                    {"detail": f"Error {operation_description}: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return wrapper
    return decorator


def execute_query(query, params=None, fetch_all=True):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [col[0] for col in cursor.description]
        
        if fetch_all:
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            row = cursor.fetchone()
            result = dict(zip(columns, row)) if row else None
            
    return result

@api_view(['GET'])
@db_operation("retrieving overdue tasks")
def get_overdue_tasks(request):
    today = datetime.now().date()
    
    
    tasks = execute_query("""
        SELECT 
            pt.task_id,
            pt.task_description,
            pt.task_deadline,
            pt.task_status,
            pt.project_id,
            pt.intrnl_project_id,
            pt.project_labor_id,
            pl.employee_id,
            COALESCE(e.first_name || ' ' || e.last_name, 'Unassigned') as employee_name,
            e.first_name,
            e.last_name,
            e.phone,
            e.employment_type,
            e.status
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
    
    formatted_tasks = []
    for task in tasks:
        
        task_deadline = task['task_deadline']
        if hasattr(task_deadline, 'date'):
            task_deadline = task_deadline.date()
        
        overdue_days = (today - task_deadline).days
        
        formatted_tasks.append({
            'TaskID': task['task_id'],
            'Overdue': f"{overdue_days} days",
            'Task': task['task_description'],
            'Deadline': task['task_deadline'].strftime('%Y-%m-%d') if hasattr(task['task_deadline'], 'strftime') else str(task['task_deadline']),
            'Employee': task['employee_name'],
            'EmployeeID': task['employee_id'],
            'ProjectID': task['project_id'] or task['intrnl_project_id'],
            'EmploymentType': task['employment_type'],
            'Phone': task['phone']
        })
    
    logger.info(f"Overdue tasks retrieved: {len(formatted_tasks)}")
    return Response(formatted_tasks)

@api_view(['GET'])
@db_operation("retrieving today's tasks")
def get_today_tasks(request):
    today = datetime.now().date()
    
    
    tasks = execute_query("""
        SELECT 
            pt.task_id,
            pt.task_description,
            pt.task_status,
            pt.task_deadline,
            pt.project_id,
            pt.intrnl_project_id,
            pl.employee_id,
            COALESCE(e.first_name, '') || ' ' || COALESCE(e.last_name, '') as employee_name,
            e.first_name,
            e.last_name,
            e.phone,
            e.employment_type,
            e.status,
            COALESCE(epr.ext_project_name, ipr.project_name, 'Unknown Project') as project_name
        FROM 
            project_management.project_tasks pt
        LEFT JOIN 
            project_management.project_labor pl ON pt.project_labor_id = pl.project_labor_id
        LEFT JOIN 
            human_resources.employees e ON pl.employee_id = e.employee_id
        LEFT JOIN 
            project_management.external_project_details epd ON pt.project_id = epd.project_id
        LEFT JOIN 
            project_management.external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
        LEFT JOIN 
            project_management.internal_project_details ipd ON pt.intrnl_project_id = ipd.intrnl_project_id
        LEFT JOIN 
            project_management.internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
        WHERE 
            pt.task_deadline::date = %s
        ORDER BY 
            pt.task_status
    """, [today])
    
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            'TaskID': task['task_id'],
            'Task': task['task_description'],
            'ProjectID': task['project_id'] or task['intrnl_project_id'],
            'ProjectName': task['project_name'],
            'Status': task['task_status'],
            'Deadline': task['task_deadline'].strftime('%Y-%m-%d') if hasattr(task['task_deadline'], 'strftime') else str(task['task_deadline']),
            'EmployeeID': task['employee_id'],
            'EmployeeName': task['employee_name'].strip() or 'Unassigned',
            'EmploymentType': task['employment_type'],
            'Phone': task['phone']
        })
    
    logger.info(f"Today's tasks retrieved: {len(formatted_tasks)}")
    return Response(formatted_tasks)

@api_view(['GET'])
@db_operation("retrieving internal tasks")
def get_internal_tasks(request):
    
    tasks = execute_query("""
        SELECT 
            pt.task_id,
            pt.task_description,
            pt.task_deadline,
            pt.task_status,
            pt.intrnl_project_id,
            ipr.project_name,
            pl.employee_id,
            e.first_name,
            e.last_name,
            e.phone,
            e.employment_type,
            e.status
        FROM 
            project_management.project_tasks pt
        LEFT JOIN 
            project_management.project_labor pl ON pt.project_labor_id = pl.project_labor_id
        LEFT JOIN 
            human_resources.employees e ON pl.employee_id = e.employee_id
        LEFT JOIN
            project_management.internal_project_details ipd ON pt.intrnl_project_id = ipd.intrnl_project_id
        LEFT JOIN
            project_management.internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
        WHERE
            pt.intrnl_project_id IS NOT NULL
    """)
    
    
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            'TaskID': task['task_id'],
            'Task': task['task_description'],
            'ProjectID': task['intrnl_project_id'],
            'ProjectName': task['project_name'] or 'Internal Project',
            'Status': task['task_status'],
            'Deadline': task['task_deadline'].strftime('%Y-%m-%d') if hasattr(task['task_deadline'], 'strftime') else str(task['task_deadline']),
            'EmployeeID': task['employee_id'],
            'EmployeeName': f"{task['first_name'] or ''} {task['last_name'] or ''}".strip() or 'Unassigned',
            'EmploymentType': task['employment_type'],
            'Phone': task['phone']
        })
    
    logger.info(f"Internal tasks retrieved: {len(formatted_tasks)}")
    return Response(formatted_tasks)

@api_view(['GET'])
@db_operation("retrieving external tasks")
def get_external_tasks(request):
    
    tasks = execute_query("""
        SELECT 
            pt.task_id,
            pt.task_description,
            pt.task_deadline,
            pt.task_status,
            pt.project_id,
            epr.ext_project_name as project_name,
            pl.employee_id,
            e.first_name,
            e.last_name,
            e.phone,
            e.employment_type,
            e.status
        FROM 
            project_management.project_tasks pt
        LEFT JOIN 
            project_management.project_labor pl ON pt.project_labor_id = pl.project_labor_id
        LEFT JOIN 
            human_resources.employees e ON pl.employee_id = e.employee_id
        LEFT JOIN
            project_management.external_project_details epd ON pt.project_id = epd.project_id
        LEFT JOIN
            project_management.external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
        WHERE
            pt.project_id IS NOT NULL
    """)
    
    
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            'TaskID': task['task_id'],
            'Task': task['task_description'],
            'ProjectID': task['project_id'],
            'ProjectName': task['project_name'] or 'External Project',
            'Status': task['task_status'],
            'Deadline': task['task_deadline'].strftime('%Y-%m-%d') if hasattr(task['task_deadline'], 'strftime') else str(task['task_deadline']),
            'EmployeeID': task['employee_id'],
            'EmployeeName': f"{task['first_name'] or ''} {task['last_name'] or ''}".strip() or 'Unassigned',
            'EmploymentType': task['employment_type'],
            'Phone': task['phone']
        })
    
    logger.info(f"External tasks retrieved: {len(formatted_tasks)}")
    return Response(formatted_tasks)

@api_view(['GET'])
@db_operation("retrieving project summary")
def get_project_summary(request):
    
    external_projects = execute_query("""
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
    
    formatted_external = []
    for project in external_projects:
        formatted_external.append({
            'id': project['project_id'],
            'projectId': project['ext_project_name'] or "Unnamed Project",
            'type': 'External',
            'startDate': project['start_date'].strftime('%Y-%m-%d') if hasattr(project['start_date'], 'strftime') else str(project['start_date']),
            'endDate': project['estimated_end_date'].strftime('%Y-%m-%d') if hasattr(project['estimated_end_date'], 'strftime') else str(project['estimated_end_date']),
            'status': project['project_status'],
            'issue': project['has_issues']
        })
    
    
    internal_projects = execute_query("""
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
    
    formatted_internal = []
    for project in internal_projects:
        formatted_internal.append({
            'id': project['intrnl_project_id'],
            'projectId': project['project_name'] or "Unnamed Project",
            'type': 'Internal',
            'startDate': project['start_date'].strftime('%Y-%m-%d') if hasattr(project['start_date'], 'strftime') else str(project['start_date']),
            'endDate': project['estimated_end_date'].strftime('%Y-%m-%d') if hasattr(project['estimated_end_date'], 'strftime') else str(project['estimated_end_date']),
            'status': project['intrnl_project_status'],
            'issue': project['has_issues']
        })
    
    
    all_projects = formatted_external + formatted_internal
    
    logger.info(f"Project summary retrieved: {len(all_projects)} projects")
    return Response(all_projects)

@api_view(['GET'])
@db_operation("retrieving project details")
def get_project_detail(request, project_type, project_id):
    if project_type == 'External':
        
        project = execute_query("""
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
        """, [project_id], fetch_all=False)
        
        if not project:
            return Response({"detail": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        tasks = execute_query("""
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
        
        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append({
                'id': task['task_id'],
                'description': task['task_description'],
                'status': task['task_status'],
                'deadline': task['task_deadline'].strftime('%Y-%m-%d') if hasattr(task['task_deadline'], 'strftime') else str(task['task_deadline'])
            })
        
        
        labor = execute_query("""
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
        
        formatted_labor = []
        for item in labor:
            formatted_labor.append({
                'id': item['project_labor_id'],
                'role': item['job_role_needed'],
                'employeeId': item['employee_id'],
                'employeeName': item['employee_name']
            })
        
        result = {
            'project_tracking_id': project['project_id'],
            'project_id': project['project_id'],
            'project_name': project['ext_project_name'],
            'project_description': project['ext_project_description'],
            'project_status': project['project_status'],
            'project_milestone': project['project_milestone'],
            'start_date': project['start_date'].strftime('%Y-%m-%d') if hasattr(project['start_date'], 'strftime') else str(project['start_date']),
            'estimated_end_date': project['estimated_end_date'].strftime('%Y-%m-%d') if hasattr(project['estimated_end_date'], 'strftime') else str(project['estimated_end_date']),
            'warranty_coverage_yr': project['warranty_coverage_yr'],
            'warranty_start_date': project['warranty_start_date'].strftime('%Y-%m-%d') if hasattr(project['warranty_start_date'], 'strftime') else str(project['warranty_start_date']),
            'warranty_end_date': project['warranty_end_date'].strftime('%Y-%m-%d') if hasattr(project['warranty_end_date'], 'strftime') else str(project['warranty_end_date']),
            'project_issues': project['project_issues'],
            'tasks': formatted_tasks,
            'labor': formatted_labor
        }
    
    elif project_type == 'Internal':
        
        project = execute_query("""
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
        """, [project_id], fetch_all=False)
        
        if not project:
            return Response({"detail": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        tasks = execute_query("""
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
        
        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append({
                'id': task['task_id'],
                'description': task['task_description'],
                'status': task['task_status'],
                'deadline': task['task_deadline'].strftime('%Y-%m-%d') if hasattr(task['task_deadline'], 'strftime') else str(task['task_deadline'])
            })
        
        
        labor = execute_query("""
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
        
        formatted_labor = []
        for item in labor:
            formatted_labor.append({
                'id': item['project_labor_id'],
                'role': item['job_role_needed'],
                'employeeId': item['employee_id'],
                'employeeName': item['employee_name']
            })
        
        result = {
            'intrnl_project_tracking_id': project['intrnl_project_id'],
            'intrnl_project_id': project['intrnl_project_id'],
            'project_name': project['project_name'],
            'project_description': "No description available",  
            'intrnl_project_status': project['intrnl_project_status'],
            'intrnl_start_date': project['start_date'].strftime('%Y-%m-%d') if hasattr(project['start_date'], 'strftime') else str(project['start_date']),
            'intrnl_estimated_end_date': project['estimated_end_date'].strftime('%Y-%m-%d') if hasattr(project['estimated_end_date'], 'strftime') else str(project['estimated_end_date']),
            'approval_id': project['approval_id'],
            'intrnl_project_issue': project['project_issues'],
            'tasks': formatted_tasks,
            'labor': formatted_labor
        }
    else:
        return Response({"detail": "Invalid project type"}, status=status.HTTP_400_BAD_REQUEST)
    
    logger.info(f"Project details retrieved for {project_type} project {project_id}")
    return Response(result)

@api_view(['GET'])
@db_operation("retrieving employee details")
def get_employee_details(request, employee_id):
    """Get details for a specific employee"""
    if not employee_id:
        return Response(
            {"detail": "Employee ID is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    employee = execute_query("""
        SELECT 
            e.employee_id, 
            e.dept_id,
            d.dept_name,
            e.position_id,
            p.position_title,
            e.first_name, 
            e.last_name, 
            e.phone, 
            e.employment_type, 
            e.status
        FROM 
            human_resources.employees e
        LEFT JOIN
            human_resources.departments d ON e.dept_id = d.dept_id
        LEFT JOIN
            human_resources.positions p ON e.position_id = p.position_id
        WHERE 
            e.employee_id = %s
    """, [employee_id], fetch_all=False)
    
    if not employee:
        return Response(
            {"detail": f"Employee with ID {employee_id} not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    logger.info(f"Employee details retrieved for employee ID {employee_id}")
    return Response(employee)

@api_view(['POST'])
@db_operation("updating task status")
def update_task_status(request, task_id):
    new_status = request.data.get('status')
    if not new_status:
        return Response({"detail": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    
    result = execute_query("""
        UPDATE project_management.project_tasks
        SET task_status = %s
        WHERE task_id = %s
        RETURNING task_id
    """, [new_status, task_id], fetch_all=False)
    
    if not result:
        return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    
    logger.info(f"Task status updated for task ID {task_id}")
    return Response({"detail": "Task status updated successfully"})