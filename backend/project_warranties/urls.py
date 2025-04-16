from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.ExternalProjectWarrantyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('project-autocomplete/', views.project_autocomplete, name='project_autocomplete'),
]