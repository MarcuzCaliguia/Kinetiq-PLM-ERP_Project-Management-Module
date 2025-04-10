# /urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task_list'),
    
    # Internal task URLs
    path('internal/add/', views.InternalTaskCreateView.as_view(), name='internal_task_add'),
    path('internal/<str:task_id>/', views.InternalTaskDetailView.as_view(), name='internal_task_detail'),
    path('internal/<str:task_id>/edit/', views.InternalTaskUpdateView.as_view(), name='internal_task_edit'),
    path('internal/<str:task_id>/delete/', views.InternalTaskDeleteView.as_view(), name='internal_task_delete'),
    
    # External task URLs
    path('external/add/', views.ExternalTaskCreateView.as_view(), name='external_task_add'),
    path('external/<str:task_id>/', views.ExternalTaskDetailView.as_view(), name='external_task_detail'),
    path('external/<str:task_id>/edit/', views.ExternalTaskUpdateView.as_view(), name='external_task_edit'),
    path('external/<str:task_id>/delete/', views.ExternalTaskDeleteView.as_view(), name='external_task_delete'),
    
    # Calendar view
    path('calendar/', views.CalendarView.as_view(), name='task_calendar'),
    path('calendar/tasks/', views.calendar_tasks_json, name='calendar_tasks_json'),
    path('calendar/add-task/<str:date>/', views.calendar_add_task, name='calendar_add_task'),
    
    # API endpoints
    path('api/update-status/', views.task_status_update, name='task_status_update'),
]