from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib import messages
from datetime import date
from django.db.models import Q
from .models import ReportMonitoring, ExternalProject, InternalProject
from .forms import ReportFilterForm, ReportMonitoringForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required


class ReportListView(ListView):
    model = ReportMonitoring
    template_name = 'project_reports/report_list.html'
    context_object_name = 'reports'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter form
        self.filter_form = ReportFilterForm(self.request.GET)
        
        # Apply filters if form is valid
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            
            # Search filter
            search_query = data.get('search')
            if search_query:
                queryset = queryset.filter(
                    Q(report_title__icontains=search_query) |
                    Q(report_monitoring_id__icontains=search_query) |
                    Q(description__icontains=search_query)
                )
            
            # Report type filter
            report_type = data.get('report_type')
            if report_type:
                queryset = queryset.filter(report_type=report_type)
            
            # Date range filters
            date_from = data.get('date_from')
            if date_from:
                queryset = queryset.filter(date_created__gte=date_from)
                
            date_to = data.get('date_to')
            if date_to:
                queryset = queryset.filter(date_created__lte=date_to)
            
            # Project type filter
            project_type = data.get('project_type')
            if project_type == 'external':
                queryset = queryset.filter(project_id__isnull=False)
            elif project_type == 'internal':
                queryset = queryset.filter(intrnl_project_id__isnull=False)
        
        return queryset.order_by('-date_created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.filter_form
        return context

class ReportDetailView(DetailView):
    model = ReportMonitoring
    template_name = 'project_reports/report_detail.html'
    context_object_name = 'report'
    
    def get_object(self):
        return get_object_or_404(ReportMonitoring, report_monitoring_id=self.kwargs['report_id'])
    
@login_required
@permission_required('project_reports.add_reportmonitoring', raise_exception=True)
def create_report_view(request):
    if request.method == 'POST':
        form = ReportMonitoringForm(request.POST)
        if form.is_valid():
            try:
                # Get the project IDs from the form
                project_id = form.cleaned_data.get('project_id')
                if project_id == '':
                    project_id = None
                    
                intrnl_project_id = form.cleaned_data.get('intrnl_project_id')
                if intrnl_project_id == '':
                    intrnl_project_id = None
                
                # Use the custom method to create the report
                report_id = ReportMonitoring.create_report(
                    project_id=project_id,
                    intrnl_project_id=intrnl_project_id,
                    report_type=form.cleaned_data['report_type'],
                    report_title=form.cleaned_data['report_title'],
                    received_from=form.cleaned_data['received_from'],
                    date_created=form.cleaned_data['date_created'],
                    assigned_to=form.cleaned_data['assigned_to'],
                    description=form.cleaned_data.get('description', '')
                )
                
                if report_id:
                    messages.success(request, f'Report "{form.cleaned_data["report_title"]}" created successfully with ID {report_id}.')
                    return redirect('project_reports:report_list')
                else:
                    messages.error(request, 'Failed to create report. No report ID was returned.')
            except Exception as e:
                messages.error(request, f'Error creating report: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReportMonitoringForm()
    
    return render(request, 'project_reports/report_form.html', {
        'form': form,
    })

@login_required
@login_required
def update_report_view(request, report_id):
    report = get_object_or_404(ReportMonitoring, report_monitoring_id=report_id)
    
    # Check permissions
    if not request.user.has_perm('project_reports.change_reportmonitoring'):
        # Check if user is in the assigned department
        user_department = getattr(request.user, 'department', None)
        if not (user_department and report.assigned_to == user_department):
            return redirect('project_reports:report_detail', report_id=report_id)
        
    report = get_object_or_404(ReportMonitoring, report_monitoring_id=report_id)
    
    if request.method == 'POST':
        form = ReportMonitoringForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, f'Report "{form.cleaned_data["report_title"]}" updated successfully.')
            return redirect('project_reports:report_detail', report_id=report_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReportMonitoringForm(instance=report)
    
    return render(request, 'project_reports/report_form.html', {
        'form': form,
        'report': report,
    })

def delete_report_view(request, report_id):
    report = get_object_or_404(ReportMonitoring, report_monitoring_id=report_id)
    
    if request.method == 'POST':
        report.delete()
        messages.success(request, f'Report "{report.report_title}" deleted successfully.')
        return redirect('project_reports:report_list')
    
    return render(request, 'project_reports/report_confirm_delete.html', {
        'report': report,
    })

class ReportAccessMixin:
    """
    Mixin to check if user has access to a specific report.
    This allows for more granular access control beyond Django's default permissions.
    """
    def dispatch(self, request, *args, **kwargs):
        # First check if user is logged in and has basic permission
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get the report
        report = self.get_object()
        
        # Check if user is in the assigned department
        user_department = getattr(request.user, 'department', None)
        if user_department and report.assigned_to != user_department:
            # If user is not in management or admin, restrict access
            if not (request.user.is_superuser or 
                    request.user.groups.filter(name='Management').exists()):
                return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)