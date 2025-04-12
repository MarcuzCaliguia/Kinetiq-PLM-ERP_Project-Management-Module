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
from django.urls import path, include, re_path
from project_request.views import ProjectListView
from rest_framework.routers import DefaultRouter
from dashboard.views import DashboardView
from project_reports import views
from project_reports import api

# Create a router for the API
router = DefaultRouter()
router.register(r'reports', api.ReportMonitoringViewSet)
router.register(r'external-projects', api.ExternalProjectViewSet)
router.register(r'internal-projects', api.InternalProjectViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('projects/', include('project_request.urls')),
    path('project-tasks/', include('project_tasks.urls')),
    path('warranties/', include('warranty_monitoring.urls')),
    path('', DashboardView.as_view(), name='home'),
    path('dashboard/', include('dashboard.urls')),
    path('project-planning/', include('project_planning.urls', namespace='project_planning')),
    path('reports/', include('project_reports.urls')),
    
    # API endpoints
    path('api/', include(router.urls)),
]
