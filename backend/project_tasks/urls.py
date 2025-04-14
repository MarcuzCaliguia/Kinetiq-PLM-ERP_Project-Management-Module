from django.urls import path
from . import views

app_name = 'project_tasks'

urlpatterns = [
    path('api/internal-tasks/', views.get_internal_tasks, name='get-internal-tasks'),
    path('api/external-tasks/', views.get_external_tasks, name='get-external-tasks'),
    path('api/internal-tasks/create/', views.create_internal_task, name='create-internal-task'),
    path('api/external-tasks/create/', views.create_external_task, name='create-external-task'),
    path('api/internal-tasks/<str:task_id>/', views.delete_internal_task, name='delete-internal-task'),
    path('api/external-tasks/<str:task_id>/', views.delete_external_task, name='delete-external-task'),
    
    path('api/internal-projects/', views.get_internal_projects, name='internal-projects'),
    path('api/external-projects/', views.get_external_projects, name='external-projects'),
    path('api/internal-labor/', views.get_internal_labor, name='internal-labor'),
    path('api/external-labor/', views.get_external_labor, name='external-labor'),
]