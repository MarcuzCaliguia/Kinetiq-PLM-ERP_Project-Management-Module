from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
import logging
from .models import (
    ProjectTasks,
    InternalProjectDetails,
    ExternalProjectDetails,
    ProjectLabor,
    ExternalProjectRequest,
    InternalProjectRequest
)

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_internal_tasks(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pt.task_id, ipr.project_name, pt.task_description, 
                       pt.task_status, pt.task_deadline, e.first_name, e.last_name
                FROM project_management.project_tasks pt
                JOIN project_management.project_labor pl ON pt.project_labor_id = pl.project_labor_id
                JOIN human_resources.employees e ON pl.employee_id = e.employee_id
                JOIN project_management.internal_project_details ipd ON pt.intrnl_project_id = ipd.intrnl_project_id
                JOIN project_management.internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
                WHERE pt.intrnl_project_id IS NOT NULL
            """)
            
            columns = [col[0] for col in cursor.description]
            tasks = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        logger.info(f"Internal tasks retrieved: {len(tasks)}")
        return Response(tasks)
    except Exception as e:
        logger.error(f"Error retrieving internal tasks: {str(e)}")
        return Response(
            {"detail": f"Error retrieving tasks: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_external_tasks(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pt.task_id, epr.ext_project_name, pt.task_description, 
                       pt.task_status, pt.task_deadline, e.first_name, e.last_name
                FROM project_management.project_tasks pt
                JOIN project_management.project_labor pl ON pt.project_labor_id = pl.project_labor_id
                JOIN human_resources.employees e ON pl.employee_id = e.employee_id
                JOIN project_management.external_project_details epd ON pt.project_id = epd.project_id
                JOIN project_management.external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
                WHERE pt.project_id IS NOT NULL
            """)
            
            columns = [col[0] for col in cursor.description]
            tasks = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        logger.info(f"External tasks retrieved: {len(tasks)}")
        return Response(tasks)
    except Exception as e:
        logger.error(f"Error retrieving external tasks: {str(e)}")
        return Response(
            {"detail": f"Error retrieving tasks: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def create_external_task(request):
    try:
        logger.info(f"Creating external task with data: {request.data}")
        
        project_id = request.data.get('ProjectID')
        task_description = request.data.get('TaskDescription')
        task_status = request.data.get('TaskStatus')
        task_deadline = request.data.get('Taskdeadline')
        project_labor_id = request.data.get('Laborid')
        
        logger.info(f"Extracted data: project_id={project_id}, task_description={task_description}, "
                   f"task_status={task_status}, task_deadline={task_deadline}, "
                   f"project_labor_id={project_labor_id}")
        
        if not all([project_id, task_status, task_deadline, project_labor_id]):
            missing_fields = []
            if not project_id: missing_fields.append('ProjectID')
            if not task_status: missing_fields.append('TaskStatus')
            if not task_deadline: missing_fields.append('Taskdeadline')
            if not project_labor_id: missing_fields.append('Laborid')
            
            return Response(
                {"detail": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            project = ExternalProjectDetails.objects.get(project_id=project_id)
            project_labor = ProjectLabor.objects.get(project_labor_id=project_labor_id)
        except (ExternalProjectDetails.DoesNotExist, ProjectLabor.DoesNotExist) as e:
            return Response(
                {"detail": f"Invalid project ID or labor ID: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO project_management.project_tasks
                (project_id, task_description, task_status, task_deadline, project_labor_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING task_id
            """, [project_id, task_description, task_status, task_deadline, project_labor_id])
            
            result = cursor.fetchone()
            if not result:
                return Response(
                    {"detail": "Task created but could not retrieve the task ID"},
                    status=status.HTTP_201_CREATED
                )
            
            task_id = result[0]
            
            # Get the created task details
            cursor.execute("""
                SELECT pt.task_id, epr.ext_project_name, pt.task_description, 
                       pt.task_status, pt.task_deadline, e.first_name, e.last_name
                FROM project_management.project_tasks pt
                JOIN project_management.project_labor pl ON pt.project_labor_id = pl.project_labor_id
                JOIN human_resources.employees e ON pl.employee_id = e.employee_id
                JOIN project_management.external_project_details epd ON pt.project_id = epd.project_id
                JOIN project_management.external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
                WHERE pt.task_id = %s
            """, [task_id])
            
            columns = [col[0] for col in cursor.description]
            task_data = dict(zip(columns, cursor.fetchone()))
            
            return Response(task_data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error creating external task: {str(e)}")
        return Response(
            {"detail": f"Error creating task: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
def create_internal_task(request):
    try:
        logger.info(f"Creating internal task with data: {request.data}")
        
        project_id = request.data.get('ProjectID')
        task_description = request.data.get('TaskDescription')
        task_status = request.data.get('TaskStatus')
        task_deadline = request.data.get('Taskdeadline')
        project_labor_id = request.data.get('Laborid')
        
        logger.info(f"Extracted data: project_id={project_id}, task_description={task_description}, "
                   f"task_status={task_status}, task_deadline={task_deadline}, "
                   f"project_labor_id={project_labor_id}")
        
        if not all([project_id, task_status, task_deadline, project_labor_id]):
            missing_fields = []
            if not project_id: missing_fields.append('ProjectID')
            if not task_status: missing_fields.append('TaskStatus')
            if not task_deadline: missing_fields.append('Taskdeadline')
            if not project_labor_id: missing_fields.append('Laborid')
            
            return Response(
                {"detail": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            project = InternalProjectDetails.objects.get(intrnl_project_id=project_id)
            project_labor = ProjectLabor.objects.get(project_labor_id=project_labor_id)
        except (InternalProjectDetails.DoesNotExist, ProjectLabor.DoesNotExist) as e:
            return Response(
                {"detail": f"Invalid project ID or labor ID: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO project_management.project_tasks
                (intrnl_project_id, task_description, task_status, task_deadline, project_labor_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING task_id
            """, [project_id, task_description, task_status, task_deadline, project_labor_id])
            
            result = cursor.fetchone()
            if not result:
                return Response(
                    {"detail": "Task created but could not retrieve the task ID"},
                    status=status.HTTP_201_CREATED
                )
            
            task_id = result[0]
            
            # Get the created task details
            cursor.execute("""
                SELECT pt.task_id, ipr.project_name, pt.task_description, 
                       pt.task_status, pt.task_deadline, e.first_name, e.last_name
                FROM project_management.project_tasks pt
                JOIN project_management.project_labor pl ON pt.project_labor_id = pl.project_labor_id
                JOIN human_resources.employees e ON pl.employee_id = e.employee_id
                JOIN project_management.internal_project_details ipd ON pt.intrnl_project_id = ipd.intrnl_project_id
                JOIN project_management.internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
                WHERE pt.task_id = %s
            """, [task_id])
            
            columns = [col[0] for col in cursor.description]
            task_data = dict(zip(columns, cursor.fetchone()))
            
            return Response(task_data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error creating internal task: {str(e)}")
        return Response(
            {"detail": f"Error creating task: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['DELETE'])
def delete_external_task(request, task_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM project_management.project_tasks
                WHERE task_id = %s AND project_id IS NOT NULL
            """, [task_id])
            
            if cursor.rowcount == 0:
                return Response(
                    {"detail": f"Task with ID {task_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting external task: {str(e)}")
        return Response(
            {"detail": f"Error deleting task: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def delete_internal_task(request, task_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM project_management.project_tasks
                WHERE task_id = %s AND intrnl_project_id IS NOT NULL
            """, [task_id])
            
            if cursor.rowcount == 0:
                return Response(
                    {"detail": f"Task with ID {task_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting internal task: {str(e)}")
        return Response(
            {"detail": f"Error deleting task: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_internal_projects(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ipd.intrnl_project_id, ipr.project_name
                FROM project_management.internal_project_details ipd
                JOIN project_management.internal_project_request ipr 
                ON ipd.project_request_id = ipr.project_request_id
            """)
            
            columns = [col[0] for col in cursor.description]
            projects = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        logger.info(f"Internal projects retrieved: {len(projects)}")
        return Response(projects)
    except Exception as e:
        logger.error(f"Error retrieving internal projects: {str(e)}")
        return Response(
            {"detail": f"Error retrieving projects: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_external_projects(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT epd.project_id, epr.ext_project_name
                FROM project_management.external_project_details epd
                JOIN project_management.external_project_request epr 
                ON epd.ext_project_request_id = epr.ext_project_request_id
            """)
            
            columns = [col[0] for col in cursor.description]
            projects = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        logger.info(f"External projects retrieved: {len(projects)}")
        return Response(projects)
    except Exception as e:
        logger.error(f"Error retrieving external projects: {str(e)}")
        return Response(
            {"detail": f"Error retrieving projects: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_internal_labor(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pl.project_labor_id, pl.intrnl_project_id, pl.employee_id, 
                       e.first_name, e.last_name
                FROM project_management.project_labor pl
                JOIN human_resources.employees e ON pl.employee_id = e.employee_id
                WHERE pl.intrnl_project_id IS NOT NULL
            """)
            
            columns = [col[0] for col in cursor.description]
            labor = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        logger.info(f"Internal labor retrieved: {len(labor)}")
        return Response(labor)
    except Exception as e:
        logger.error(f"Error retrieving internal labor: {str(e)}")
        return Response(
            {"detail": f"Error retrieving labor: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_external_labor(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pl.project_labor_id, pl.project_id, pl.employee_id, 
                       e.first_name, e.last_name
                FROM project_management.project_labor pl
                JOIN human_resources.employees e ON pl.employee_id = e.employee_id
                WHERE pl.project_id IS NOT NULL
            """)
            
            columns = [col[0] for col in cursor.description]
            labor = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        logger.info(f"External labor retrieved: {len(labor)}")
        return Response(labor)
    except Exception as e:
        logger.error(f"Error retrieving external labor: {str(e)}")
        return Response(
            {"detail": f"Error retrieving labor: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )