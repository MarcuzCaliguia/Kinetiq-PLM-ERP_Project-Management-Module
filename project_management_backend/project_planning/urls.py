from django.urls import path
from .views import ProjectPlanningView

app_name = 'project_planning'

urlpatterns = [
    path('', ProjectPlanningView.as_view(), name='index'),
]