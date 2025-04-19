from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExternalProjectRequestViewSet, ExternalProjectDetailsViewSet,
    ExternalProjectLaborViewSet, ExternalProjectEquipmentsViewSet,
    ExternalProjectWarrantyViewSet, InternalProjectRequestViewSet,
    InternalProjectDetailsViewSet
)

router = DefaultRouter()
router.register(r'external-requests', ExternalProjectRequestViewSet)
router.register(r'external-details', ExternalProjectDetailsViewSet)
router.register(r'external-labor', ExternalProjectLaborViewSet)
router.register(r'external-equipments', ExternalProjectEquipmentsViewSet)
router.register(r'external-warranty', ExternalProjectWarrantyViewSet)
router.register(r'internal-requests', InternalProjectRequestViewSet)
router.register(r'internal-details', InternalProjectDetailsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]