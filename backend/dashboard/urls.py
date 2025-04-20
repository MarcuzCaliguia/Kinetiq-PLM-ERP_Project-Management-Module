
from django.urls import path
from .views import (
    OverdueTasksView, TodayTasksView, ExternalProjectTrackingView,
    InternalProjectTrackingView, CreateExternalProjectView,
    CreateInternalProjectView, ProjectSummaryView,
    SearchExternalProjectView, SearchInternalProjectView,
    SearchWarrantyView, SearchProjectRequestView
)

urlpatterns = [
    path('overdue-tasks/', OverdueTasksView.as_view(), name='overdue-tasks'),
    path('today-tasks/', TodayTasksView.as_view(), name='today-tasks'),
    path('external-projects/', ExternalProjectTrackingView.as_view(), name='external-projects'),
    path('internal-projects/', InternalProjectTrackingView.as_view(), name='internal-projects'),
    path('create-external-project/', CreateExternalProjectView.as_view(), name='create-external-project'),
    path('create-internal-project/', CreateInternalProjectView.as_view(), name='create-internal-project'),
    path('project-summary/', ProjectSummaryView.as_view(), name='project-summary'),
    path('search-external-project/', SearchExternalProjectView.as_view(), name='search-external-project'),
    path('search-internal-project/', SearchInternalProjectView.as_view(), name='search-internal-project'),
    path('search-warranty/', SearchWarrantyView.as_view(), name='search-warranty'),
    path('search-project-request/', SearchProjectRequestView.as_view(), name='search-project-request'),
]