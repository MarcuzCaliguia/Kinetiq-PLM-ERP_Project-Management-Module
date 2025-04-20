"""
URL configuration for project_management_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from project_reports import api
from project_reports import views as report_views  
from project_warranties import views as warranty_views

router = DefaultRouter()
router.register(r'reports', api.ReportMonitoringViewSet)
router.register(r'external-projects', api.ExternalProjectViewSet)
router.register(r'internal-projects', api.InternalProjectViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('project-tasks/', include('project_tasks.urls')),
    path('api/reports/', include('project_reports.urls')),
    path('api/', include(router.urls)),
    path('api/warranties/', include('project_warranties.urls')),
    path('api/project-autocomplete/', warranty_views.project_autocomplete, name='project_autocomplete'),
    path('api/project-planning/', include('project_planning.urls')),    
    path('api/project-management/', include('project_list.urls')),
    path('api/project_request/', include('project_request.urls')),    
    
    path('api/equipment/', report_views.equipment_list, name='equipment-list'),
    path('api/employees/', report_views.employees_list, name='employees-list'),
    path('api/positions/', report_views.positions_list, name='positions-list'),
    
    path('api/', include('dashboard.urls')),
]