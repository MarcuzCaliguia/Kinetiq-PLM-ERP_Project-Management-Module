from django.urls import path
from . import views

app_name = 'project_reports'

urlpatterns = [
    path('', views.ReportListView.as_view(), name='report_list'),
    path('create/', views.create_report_view, name='report_create'),
    path('<str:report_id>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('<str:report_id>/update/', views.update_report_view, name='report_update'),
    path('<str:report_id>/delete/', views.delete_report_view, name='report_delete'),
]