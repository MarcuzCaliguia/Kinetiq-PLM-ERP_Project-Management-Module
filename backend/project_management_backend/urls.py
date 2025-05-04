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
"""
URL configuration for project_management_backend project.
"""
"""
URL configuration for project_management_backend project.
"""
from django.urls import path, include
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('', health_check),
    
    path('project-tasks/', include('project_tasks.urls')),
    path('api/project-planning/', include('project_planning.urls')),
    path('api/project-management/', include('project_list.urls')),
    path('api/project-cost/', include('project_cost.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/warranties/', include('project_warranties.urls')),
]