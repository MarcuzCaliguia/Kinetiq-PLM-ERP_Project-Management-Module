from django.urls import path
from .views import DashboardView, ContractualWorkerRequestView, ProjectCostManagementView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('contractual-requests/', ContractualWorkerRequestView.as_view(), name='contractual_requests'),
    path('project-costs/', ProjectCostManagementView.as_view(), name='project_costs'),
    # Add other dashboard-related URLs here
]