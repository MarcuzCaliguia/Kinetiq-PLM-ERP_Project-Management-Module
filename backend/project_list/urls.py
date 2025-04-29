# urls.py for project_management app
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'external-projects', views.ExternalProjectDetailsViewSet, basename='external-projects')
router.register(r'external-requests', views.ExternalProjectRequestViewSet, basename='external-requests')
# Removed the project-labor registration
router.register(r'project-equipments', views.ExternalProjectEquipmentsViewSet, basename='project-equipments')
router.register(r'internal-projects', views.InternalProjectDetailsViewSet, basename='internal-projects')
router.register(r'internal-requests', views.InternalProjectRequestViewSet, basename='internal-requests')
router.register(r'project-warranty', views.ProjectWarrantyViewSet, basename='project-warranty')

urlpatterns = [
    path('', include(router.urls)),
]