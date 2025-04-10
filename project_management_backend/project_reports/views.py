from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .models import ReportMonitoring
from .forms import ReportMonitoringForm

class ReportListView(ListView):
    model = ReportMonitoring
    template_name = 'project_reports/report_list.html'
    context_object_name = 'reports'

class ReportDetailView(DetailView):
    model = ReportMonitoring
    template_name = 'project_reports/report_detail.html'
    context_object_name = 'report'
    pk_url_kwarg = 'report_id'

class ReportCreateView(CreateView):
    model = ReportMonitoring
    form_class = ReportMonitoringForm
    template_name = 'project_reports/report_form.html'
    success_url = reverse_lazy('project_reports:report_list')

    def form_valid(self, form):
        messages.success(self.request, 'Report created successfully.')
        return super().form_valid(form)

class ReportUpdateView(UpdateView):
    model = ReportMonitoring
    form_class = ReportMonitoringForm
    template_name = 'project_reports/report_form.html'
    pk_url_kwarg = 'report_id'
    success_url = reverse_lazy('project_reports:report_list')

    def form_valid(self, form):
        messages.success(self.request, 'Report updated successfully.')
        return super().form_valid(form)

class ReportDeleteView(DeleteView):
    model = ReportMonitoring
    template_name = 'project_reports/report_confirm_delete.html'
    pk_url_kwarg = 'report_id'
    success_url = reverse_lazy('project_reports:report_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Report deleted successfully.')
        return super().delete(request, *args, **kwargs)

class AnalyticsView(View):
    def get(self, request):
        total_reports = ReportMonitoring.objects.count()
        # Add more analytics data as needed
        context = {
            'total_reports': total_reports,
        }
        return render(request, 'project_reports/analytics.html', context)

class BulkDeleteView(View):
    def post(self, request):
        report_ids = request.POST.getlist('report_ids')
        if report_ids:
            ReportMonitoring.objects.filter(report_monitoring_id__in=report_ids).delete()
            messages.success(request, f'{len(report_ids)} reports removed successfully.')
        else:
            messages.error(request, 'No reports selected for deletion.')
        return redirect('project_reports:report_list')