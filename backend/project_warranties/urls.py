# project_warranties/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.ExternalProjectDetailsViewSet, basename='warranties')

urlpatterns = [
    path('', include(router.urls)),
    path('project-autocomplete/', views.project_autocomplete, name='project_autocomplete'),
    path('project-warranty-details/<str:project_id>/', views.project_warranty_details, name='project_warranty_details'),
]