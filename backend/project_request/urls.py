from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('test/', views.test_view, name='test_view'),
    path('project-requests/', csrf_exempt(views.project_requests), name='project_requests'),
    path('project-requests/<str:project_id>/', csrf_exempt(views.project_request_detail), name='project_request_detail'),
    path('search-employees/', views.search_employees, name='search_employees'),
    path('search-departments/', views.search_departments, name='search_departments'),
]