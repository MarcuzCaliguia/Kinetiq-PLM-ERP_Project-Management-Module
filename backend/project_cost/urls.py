from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'costs', views.ProjectCostViewSet, basename='project-costs')

urlpatterns = [
    path('', include(router.urls)),
    path('direct-costs/', views.direct_project_costs, name='direct-costs'),
]