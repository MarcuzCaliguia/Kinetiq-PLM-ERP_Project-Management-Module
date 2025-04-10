from django.urls import path
from .views import ProjectListView

app_name = 'project_request'

urlpatterns = [
    path('', ProjectListView.as_view(), name='project_list'),
]