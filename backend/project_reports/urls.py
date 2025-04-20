from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.ReportMonitoringViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
    path('external-projects/', views.external_projects, name='external_projects'),
    path('internal-projects/', views.internal_projects, name='internal_projects'),
    path('equipment/', views.equipment_list, name='equipment-list'),
    path('employees/', views.employees_list, name='employees-list'),
    path('positions/', views.positions_list, name='positions-list'),
    path('project-autocomplete/', views.project_autocomplete, name='project-autocomplete'),
]