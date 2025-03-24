from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InternalProjectRequestViewSet,
    InternalProjectDetailsViewSet,
    InternalProjectLaborViewSet,
    InternalProjectTaskListViewSet
)

router = DefaultRouter()
router.register(r'requests', InternalProjectRequestViewSet)
router.register(r'projects', InternalProjectDetailsViewSet)
router.register(r'labor', InternalProjectLaborViewSet)
router.register(r'tasks', InternalProjectTaskListViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]