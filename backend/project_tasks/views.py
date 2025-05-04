from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def db_operation(operation_name):
    """Decorator to handle database operations with proper error handling and logging"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            try:
                logger.info(f"Starting {operation_name}")
                return view_func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {operation_name}: {str(e)}")
                return Response(
                    {"detail": f"Operation failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return wrapper
    return decorator

def execute_query(query, params=None, fetch_all=True):
    """Execute SQL query and return results"""
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            if fetch_all:
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                row = cursor.fetchone()
                return dict(zip(columns, row)) if row else None
        return cursor.rowcount if not fetch_all else []

@api_view(['GET'])
@db_operation("retrieving internal tasks")
def get_internal_tasks(request):
    
    tasks = execute_query("""
        SELECT 
            t.*,
            pl.employee_id,
            e.first_name,
            e.last_name,
            e.phone,
            e.employment_type,
            e.status
        FROM 
            project_management.internal_project_tasks t
        LEFT JOIN 
            project_management.project_tasks pt ON t.task_id = pt.task_id
        LEFT JOIN 
            project_management.project_labor pl ON pt.project_labor_id = pl.project_labor_id
        LEFT JOIN 
            human_resources.employees e ON pl.employee_id = e.employee_id
    """)
    logger.info(f"Internal tasks retrieved: {len(tasks)}")
    return Response(tasks)

@api_view(['GET'])
@db_operation("retrieving external tasks")
def get_external_tasks(request):
    
    tasks = execute_query("""
        SELECT 
            t.*,
            pl.employee_id,
            e.first_name,
            e.last_name,
            e.phone,
            e.employment_type,
            e.status
        FROM 
            project_management.external_project_tasks t
        LEFT JOIN 
            project_management.project_tasks pt ON t.task_id = pt.task_id
        LEFT JOIN 
            project_management.project_labor pl ON pt.project_labor_id = pl.project_labor_id
        LEFT JOIN 
            human_resources.employees e ON pl.employee_id = e.employee_id
    """)
    logger.info(f"External tasks retrieved: {len(tasks)}")
    return Response(tasks)
@api_view(['POST'])
@db_operation("creating external task")
def create_external_task(request):
    logger.info(f"Creating external task with data: {request.data}")
    
    
    data = request.data
    project_id = data.get('ProjectID')
    task_description = data.get('TaskDescription', '')
    task_status = data.get('TaskStatus')
    task_deadline = data.get('Taskdeadline')
    project_labor_id = data.get('Laborid')
    
    
    required_fields = {'ProjectID': project_id, 'TaskStatus': task_status, 
                      'Taskdeadline': task_deadline, 'Laborid': project_labor_id}
    missing = [k for k, v in required_fields.items() if not v]
    
    if missing:
        return Response(
            {"detail": f"Missing required fields: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    project_exists = execute_query(
        "SELECT COUNT(*) as count FROM project_management.external_project_details WHERE project_id = %s",
        [project_id], fetch_all=False
    )
    
    if not project_exists or project_exists.get('count', 0) == 0:
        return Response(
            {"detail": f"Invalid project ID: {project_id}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    labor_exists = execute_query(
        "SELECT COUNT(*) as count FROM project_management.project_labor WHERE project_labor_id = %s",
        [project_labor_id], fetch_all=False
    )
    
    if not labor_exists or labor_exists.get('count', 0) == 0:
        return Response(
            {"detail": f"Invalid labor ID: {project_labor_id}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    result = execute_query("""
        INSERT INTO project_management.project_tasks
        (project_id, task_description, task_status, task_deadline, project_labor_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING task_id
    """, [project_id, task_description, task_status, task_deadline, project_labor_id], fetch_all=False)
    
    if not result:
        return Response(
            {"detail": "Task created but could not retrieve the task ID"},
            status=status.HTTP_201_CREATED
        )
    
    task_id = result.get('task_id')
    
    
    task_data = execute_query("""
        SELECT * FROM project_management.external_project_tasks
        WHERE task_id = %s
    """, [task_id], fetch_all=False) or {"task_id": task_id}
    
    return Response(task_data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@db_operation("creating internal task")
def create_internal_task(request):
    logger.info(f"Creating internal task with data: {request.data}")
    
    
    data = request.data
    project_id = data.get('ProjectID')
    task_description = data.get('TaskDescription', '')
    task_status = data.get('TaskStatus')
    task_deadline = data.get('Taskdeadline')
    project_labor_id = data.get('Laborid')
    
    
    required_fields = {'ProjectID': project_id, 'TaskStatus': task_status, 
                      'Taskdeadline': task_deadline, 'Laborid': project_labor_id}
    missing = [k for k, v in required_fields.items() if not v]
    
    if missing:
        return Response(
            {"detail": f"Missing required fields: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    project_exists = execute_query(
        "SELECT COUNT(*) as count FROM project_management.internal_project_details WHERE intrnl_project_id = %s",
        [project_id], fetch_all=False
    )
    
    if not project_exists or project_exists.get('count', 0) == 0:
        return Response(
            {"detail": f"Invalid project ID: {project_id}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    labor_exists = execute_query(
        "SELECT COUNT(*) as count FROM project_management.project_labor WHERE project_labor_id = %s",
        [project_labor_id], fetch_all=False
    )
    
    if not labor_exists or labor_exists.get('count', 0) == 0:
        return Response(
            {"detail": f"Invalid labor ID: {project_labor_id}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    
    result = execute_query("""
        INSERT INTO project_management.project_tasks
        (intrnl_project_id, task_description, task_status, task_deadline, project_labor_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING task_id
    """, [project_id, task_description, task_status, task_deadline, project_labor_id], fetch_all=False)
    
    if not result:
        return Response(
            {"detail": "Task created but could not retrieve the task ID"},
            status=status.HTTP_201_CREATED
        )
    
    task_id = result.get('task_id')
    
    
    task_data = execute_query("""
        SELECT * FROM project_management.internal_project_tasks
        WHERE task_id = %s
    """, [task_id], fetch_all=False) or {"task_id": task_id}
    
    return Response(task_data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@db_operation("deleting external task")
def delete_external_task(request, task_id):
    result = execute_query("""
        DELETE FROM project_management.project_tasks
        WHERE task_id = %s AND project_id IS NOT NULL
        RETURNING task_id
    """, [task_id], fetch_all=False)
    
    if not result:
        return Response(
            {"detail": f"Task with ID {task_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@db_operation("deleting internal task")
def delete_internal_task(request, task_id):
    result = execute_query("""
        DELETE FROM project_management.project_tasks
        WHERE task_id = %s AND intrnl_project_id IS NOT NULL
        RETURNING task_id
    """, [task_id], fetch_all=False)
    
    if not result:
        return Response(
            {"detail": f"Task with ID {task_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@db_operation("retrieving internal projects")
def get_internal_projects(request):
    projects = execute_query("""
        SELECT ipd.intrnl_project_id, ipr.project_name
        FROM project_management.internal_project_details ipd
        JOIN project_management.internal_project_request ipr 
        ON ipd.project_request_id = ipr.project_request_id
    """)
    
    logger.info(f"Internal projects retrieved: {len(projects)}")
    return Response(projects)

@api_view(['GET'])
@db_operation("retrieving external projects")
def get_external_projects(request):
    projects = execute_query("""
        SELECT epd.project_id, epr.ext_project_name
        FROM project_management.external_project_details epd
        JOIN project_management.external_project_request epr 
        ON epd.ext_project_request_id = epr.ext_project_request_id
    """)
    
    logger.info(f"External projects retrieved: {len(projects)}")
    return Response(projects)

@api_view(['GET'])
@db_operation("retrieving internal labor")
def get_internal_labor(request):
    labor = execute_query("""
        SELECT pl.project_labor_id, pl.intrnl_project_id, pl.employee_id, 
               e.first_name, e.last_name
        FROM project_management.project_labor pl
        JOIN human_resources.employees e ON pl.employee_id = e.employee_id
        WHERE pl.intrnl_project_id IS NOT NULL
    """)
    
    logger.info(f"Internal labor retrieved: {len(labor)}")
    return Response(labor)

@api_view(['GET'])
@db_operation("retrieving external labor")
def get_external_labor(request):
    labor = execute_query("""
        SELECT pl.project_labor_id, pl.project_id, pl.employee_id, 
               e.first_name, e.last_name
        FROM project_management.project_labor pl
        JOIN human_resources.employees e ON pl.employee_id = e.employee_id
        WHERE pl.project_id IS NOT NULL
    """)
    
    logger.info(f"External labor retrieved: {len(labor)}")
    return Response(labor)

@api_view(['GET'])
def get_employee_details(request, employee_id):
    """Get details for a specific employee"""
    if not employee_id:
        return Response(
            {"detail": "Employee ID is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        
        logger.info(f"Fetching details for employee ID: {employee_id}")
        
        
        employee = execute_query("""
            SELECT 
                e.employee_id, 
                e.dept_id,
                d.dept_name,  -- Get department name
                e.position_id,
                p.position_title,  -- Get position title
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
        
        
        logger.info(f"Employee details retrieved: {employee}")
        
        if not employee:
            return Response(
                {"detail": f"Employee with ID {employee_id} not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        
        return Response(employee)
    except Exception as e:
        logger.error(f"Error fetching employee details: {str(e)}")
        return Response(
            {"detail": f"Error fetching employee details: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )