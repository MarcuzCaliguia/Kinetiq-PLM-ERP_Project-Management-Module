from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reports', views.ReportMonitoringViewSet, basename='report')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/external-projects/', views.external_projects, name='external_projects'),
    path('api/internal-projects/', views.internal_projects, name='internal_projects'),
]