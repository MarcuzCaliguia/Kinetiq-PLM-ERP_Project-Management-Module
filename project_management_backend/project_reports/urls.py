from django.urls import path
from django.views.generic import TemplateView  # Temporary import for testing

# Import your views
from .views import (
    ReportListView,
    ReportCreateView,
    ReportDetailView,
    ReportUpdateView,
    ReportDeleteView,
    AnalyticsView,
    BulkDeleteView
)

app_name = 'project_reports'

# Define URL patterns
urlpatterns = [
    path('', ReportListView.as_view(), name='report_list'),
    path('create/', ReportCreateView.as_view(), name='report_create'),
    path('<str:report_id>/', ReportDetailView.as_view(), name='report_detail'),
    path('<str:report_id>/update/', ReportUpdateView.as_view(), name='report_update'),
    path('<str:report_id>/delete/', ReportDeleteView.as_view(), name='report_delete'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('bulk-delete/', BulkDeleteView.as_view(), name='bulk_delete'),
]

# Print statement to confirm this file is being loaded
print("project_reports.urls loaded successfully with", len(urlpatterns), "patterns")