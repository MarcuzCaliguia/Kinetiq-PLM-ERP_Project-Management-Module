from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
import logging
from .models import (
    InternalProjectTaskList,
    ExternalProjectTaskList,
    InternalProjectDetails,
    ExternalProjectDetails,
    InternalProjectLabor,
    ExternalProjectLabor
)

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_internal_tasks(request):
    try:
        tasks = InternalProjectTaskList.objects.all().values()
        logger.info(f"Internal tasks retrieved: {len(tasks)}")
        return Response(list(tasks))
    except Exception as e:
        logger.error(f"Error retrieving internal tasks: {str(e)}")
        return Response(
            {"detail": f"Error retrieving tasks: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_external_tasks(request):
    try:
        tasks = ExternalProjectTaskList.objects.all().values()
        logger.info(f"External tasks retrieved: {len(tasks)}")
        return Response(list(tasks))
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
            project_labor = ExternalProjectLabor.objects.get(project_labor_id=project_labor_id)
        except (ExternalProjectDetails.DoesNotExist, ExternalProjectLabor.DoesNotExist) as e:
            return Response(
                {"detail": f"Invalid project ID or labor ID: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO external_project_task_list
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
            
            task = ExternalProjectTaskList.objects.get(task_id=task_id)
            task_data = {
                'task_id': task.task_id,
                'project_id': project_id,
                'task_description': task.task_description,
                'task_status': task.task_status,
                'task_deadline': task.task_deadline,
                'project_labor_id': project_labor_id
            }
            
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
            project_labor = InternalProjectLabor.objects.get(intrnl_project_labor_id=project_labor_id)
        except (InternalProjectDetails.DoesNotExist, InternalProjectLabor.DoesNotExist) as e:
            return Response(
                {"detail": f"Invalid project ID or labor ID: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO internal_project_task_list
                (intrnl_project_id, intrnl_task_description, intrnl_task_status, intrnl_task_deadline, intrnl_project_labor_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING intrnl_task_id
            """, [project_id, task_description, task_status, task_deadline, project_labor_id])
            
            result = cursor.fetchone()
            if not result:
                return Response(
                    {"detail": "Task created but could not retrieve the task ID"},
                    status=status.HTTP_201_CREATED
                )
            
            task_id = result[0]
            
            task = InternalProjectTaskList.objects.get(intrnl_task_id=task_id)
            task_data = {
                'intrnl_task_id': task.intrnl_task_id,
                'intrnl_project_id': project_id,
                'intrnl_task_description': task.intrnl_task_description,
                'intrnl_task_status': task.intrnl_task_status,
                'intrnl_task_deadline': task.intrnl_task_deadline,
                'intrnl_project_labor_id': project_labor_id
            }
            
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
        task = ExternalProjectTaskList.objects.get(task_id=task_id)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ExternalProjectTaskList.DoesNotExist:
        return Response(
            {"detail": f"Task with ID {task_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting external task: {str(e)}")
        return Response(
            {"detail": f"Error deleting task: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def delete_internal_task(request, task_id):
    try:
        task = InternalProjectTaskList.objects.get(intrnl_task_id=task_id)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except InternalProjectTaskList.DoesNotExist:
        return Response(
            {"detail": f"Task with ID {task_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting internal task: {str(e)}")
        return Response(
            {"detail": f"Error deleting task: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_internal_projects(request):
    try:
        projects = InternalProjectDetails.objects.all().values('intrnl_project_id')
        logger.info(f"Internal projects retrieved: {len(projects)}")
        return Response(list(projects))
    except Exception as e:
        logger.error(f"Error retrieving internal projects: {str(e)}")
        return Response(
            {"detail": f"Error retrieving projects: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_external_projects(request):
    try:
        projects = ExternalProjectDetails.objects.all().values('project_id')
        logger.info(f"External projects retrieved: {len(projects)}")
        return Response(list(projects))
    except Exception as e:
        logger.error(f"Error retrieving external projects: {str(e)}")
        return Response(
            {"detail": f"Error retrieving projects: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_internal_labor(request):
    try:
        labor = InternalProjectLabor.objects.all().values('intrnl_project_labor_id', 'employee_id')
        logger.info(f"Internal labor retrieved: {len(labor)}")
        return Response(list(labor))
    except Exception as e:
        logger.error(f"Error retrieving internal labor: {str(e)}")
        return Response(
            {"detail": f"Error retrieving labor: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_external_labor(request):
    try:
        labor = ExternalProjectLabor.objects.all().values('project_labor_id', 'employee_id')
        logger.info(f"External labor retrieved: {len(labor)}")
        return Response(list(labor))
    except Exception as e:
        logger.error(f"Error retrieving external labor: {str(e)}")
        return Response(
            {"detail": f"Error retrieving labor: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )