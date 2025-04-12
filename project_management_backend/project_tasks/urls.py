# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for API endpoints
router = DefaultRouter()
router.register(r'internal-tasks', views.InternalProjectTaskViewSet)
router.register(r'external-tasks', views.ExternalProjectTaskViewSet)

urlpatterns = [
    # Template views - these should come FIRST
    path('', views.task_list, name='task_list'),  # Make task_list the default view
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('tasks/new-internal/', views.new_internal_task, name='new_internal_task'),
    path('tasks/new-external/', views.new_external_task, name='new_external_task'),
    path('tasks/<str:task_type>/<str:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<str:task_type>/<str:task_id>/edit/', views.edit_task, name='edit_task'),
    
    # API endpoints for dropdown data
    path('api/internal-projects/', views.get_internal_projects, name='internal_projects_api'),
    path('api/external-projects/', views.get_external_projects, name='external_projects_api'),
    path('api/internal-labor/', views.get_internal_labor, name='internal_labor_api'),
    path('api/external-labor/', views.get_external_labor, name='external_labor_api'),
    
    # Include REST Framework router URLs under the /api/ prefix
    path('api/', include(router.urls)),
]