from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'external-projects', views.ExternalProjectDetailsViewSet, basename='external-projects')
router.register(r'external-requests', views.ExternalProjectRequestViewSet, basename='external-requests')
router.register(r'project-equipments', views.ExternalProjectEquipmentsViewSet, basename='project-equipments')
router.register(r'internal-projects', views.InternalProjectDetailsViewSet, basename='internal-projects')
router.register(r'internal-requests', views.InternalProjectRequestViewSet, basename='internal-requests')
router.register(r'project-warranty', views.ProjectWarrantyViewSet, basename='project-warranty')
router.register(r'archived-projects', views.ArchivedProjectsViewSet, basename='archived-projects')  # New endpoint for archived projects

urlpatterns = [
    path('', include(router.urls)),
]