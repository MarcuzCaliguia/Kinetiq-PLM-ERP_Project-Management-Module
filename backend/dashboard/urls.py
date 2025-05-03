from django.urls import path
from . import views

urlpatterns = [
    path('overdue-tasks/', views.get_overdue_tasks, name='get_overdue_tasks'),
    path('today-tasks/', views.get_today_tasks, name='get_today_tasks'),
    path('internal-tasks/', views.get_internal_tasks, name='get_internal_tasks'),
    path('external-tasks/', views.get_external_tasks, name='get_external_tasks'),
    path('project-summary/', views.get_project_summary, name='get_project_summary'),
    path('project-detail/<str:project_type>/<str:project_id>/', views.get_project_detail, name='get_project_detail'),
    path('employee-details/<str:employee_id>/', views.get_employee_details, name='get_employee_details'),
    path('update-task-status/<str:task_id>/', views.update_task_status, name='update_task_status'),
]