from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.utils.dateparse import parse_date
import calendar
import datetime
import json
from datetime import timedelta
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone

from .models import InternalProjectTaskList, ExternalProjectTaskList, get_all_tasks_with_joins
from .forms import InternalTaskForm, ExternalTaskForm

class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'project_tasks/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        task_type = self.request.GET.get('type', 'all')
        view_type = self.request.GET.get('view', 'default')
        search_query = self.request.GET.get('search', '')
        
        if task_type == 'internal':
            queryset = InternalProjectTaskList.objects.all()
            if search_query:
                queryset = queryset.filter(
                    Q(intrnl_task_id__icontains=search_query) |
                    Q(intrnl_task_description__icontains=search_query)
                )
            return queryset
        elif task_type == 'external':
            queryset = ExternalProjectTaskList.objects.all()
            if search_query:
                queryset = queryset.filter(
                    Q(task_id__icontains=search_query) |
                    Q(task_description__icontains=search_query)
                )
            return queryset
        else:
            # Get all tasks with joins for combined view
            internal_tasks, external_tasks = get_all_tasks_with_joins()
            
            # Filter by search query if provided
            if search_query:
                internal_tasks = [task for task in internal_tasks if 
                                 search_query.lower() in str(task.get('intrnl_task_id', '')).lower() or 
                                 search_query.lower() in str(task.get('intrnl_task_description', '')).lower()]
                external_tasks = [task for task in external_tasks if 
                                 search_query.lower() in str(task.get('task_id', '')).lower() or 
                                 search_query.lower() in str(task.get('task_description', '')).lower()]
            
            # Combine and return all tasks
            all_tasks = []
            for task in internal_tasks:
                all_tasks.append({
                    'id': task.get('intrnl_task_id'),
                    'type': 'internal',
                    'project_id': task.get('intrnl_project_id'),
                    'description': task.get('intrnl_task_description'),
                    'status': task.get('intrnl_task_status'),
                    'deadline': task.get('intrnl_task_deadline'),
                    'project_name': task.get('project_name'),
                    'assigned_to': task.get('employee_name'),
                    'employee_id': task.get('employee_id'),
                    'dependencies': ''  # Add this field for purchase view
                })
            
            for task in external_tasks:
                all_tasks.append({
                    'id': task.get('task_id'),
                    'type': 'external',
                    'project_id': task.get('project_id'),
                    'description': task.get('task_description'),
                    'status': task.get('task_status'),
                    'deadline': task.get('task_deadline'),
                    'project_name': task.get('project_name'),
                    'assigned_to': task.get('employee_name'),
                    'employee_id': task.get('employee_id'),
                    'dependencies': ''  # Add this field for purchase view
                })
            
            return all_tasks
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_type'] = self.request.GET.get('type', 'all')
        context['view_type'] = self.request.GET.get('view', 'default')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class InternalTaskDetailView(LoginRequiredMixin, DetailView):
    model = InternalProjectTaskList
    template_name = 'project_tasks/internal_task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    
    def get_object(self, queryset=None):
        return get_object_or_404(InternalProjectTaskList, intrnl_task_id=self.kwargs['task_id'])

class ExternalTaskDetailView(LoginRequiredMixin, DetailView):
    model = ExternalProjectTaskList
    template_name = 'project_tasks/external_task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    
    def get_object(self, queryset=None):
        return get_object_or_404(ExternalProjectTaskList, task_id=self.kwargs['task_id'])

class InternalTaskCreateView(LoginRequiredMixin, CreateView):
    model = InternalProjectTaskList
    form_class = InternalTaskForm
    template_name = 'project_tasks/internal_task_form.html'
    success_url = reverse_lazy('task_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Internal task created successfully!')
        return super().form_valid(form)

class ExternalTaskCreateView(LoginRequiredMixin, CreateView):
    model = ExternalProjectTaskList
    form_class = ExternalTaskForm
    template_name = 'project_tasks/external_task_form.html'
    success_url = reverse_lazy('task_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'External task created successfully!')
        return super().form_valid(form)

class InternalTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = InternalProjectTaskList
    form_class = InternalTaskForm
    template_name = 'project_tasks/internal_task_form.html'
    success_url = reverse_lazy('task_list')
    
    def get_object(self, queryset=None):
        return get_object_or_404(InternalProjectTaskList, intrnl_task_id=self.kwargs['task_id'])
    
    def form_valid(self, form):
        messages.success(self.request, 'Internal task updated successfully!')
        return super().form_valid(form)

class ExternalTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = ExternalProjectTaskList
    form_class = ExternalTaskForm
    template_name = 'project_tasks/external_task_form.html'
    success_url = reverse_lazy('task_list')
    
    def get_object(self, queryset=None):
        return get_object_or_404(ExternalProjectTaskList, task_id=self.kwargs['task_id'])
    
    def form_valid(self, form):
        messages.success(self.request, 'External task updated successfully!')
        return super().form_valid(form)

class InternalTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = InternalProjectTaskList
    template_name = 'project_tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')
    
    def get_object(self, queryset=None):
        return get_object_or_404(InternalProjectTaskList, intrnl_task_id=self.kwargs['task_id'])
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Internal task deleted successfully!')
        return super().delete(request, *args, **kwargs)

class ExternalTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = ExternalProjectTaskList
    template_name = 'project_tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')
    
    def get_object(self, queryset=None):
        return get_object_or_404(ExternalProjectTaskList, task_id=self.kwargs['task_id'])
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'External task deleted successfully!')
        return super().delete(request, *args, **kwargs)

# API endpoints for AJAX operations
def task_status_update(request):
    if request.method == 'POST' and request.is_ajax():
        task_id = request.POST.get('task_id')
        task_type = request.POST.get('task_type')
        new_status = request.POST.get('status')
        
        try:
            if task_type == 'internal':
                task = get_object_or_404(InternalProjectTaskList, intrnl_task_id=task_id)
                task.intrnl_task_status = new_status
                task.save()
            else:
                task = get_object_or_404(ExternalProjectTaskList, task_id=task_id)
                task.task_status = new_status
                task.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'project_tasks/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current year and month
        today = datetime.date.today()
        year = self.request.GET.get('year', today.year)
        month = self.request.GET.get('month', today.month)
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            year = today.year
            month = today.month
        
        # Create calendar for the month
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        
        # Get previous and next month
        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year
            
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year
        
        # Get all tasks for the month
        start_date = datetime.date(year, month, 1)
        if month == 12:
            end_date = datetime.date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime.date(year, month + 1, 1) - timedelta(days=1)
        
        internal_tasks = InternalProjectTaskList.objects.filter(
            intrnl_task_deadline__gte=start_date,
            intrnl_task_deadline__lte=end_date
        )
        
        external_tasks = ExternalProjectTaskList.objects.filter(
            task_deadline__gte=start_date,
            task_deadline__lte=end_date
        )
        
        # Prepare tasks for calendar display
        tasks_by_date = {}
        
        for task in internal_tasks:
            date_str = task.intrnl_task_deadline.strftime('%Y-%m-%d')
            if date_str not in tasks_by_date:
                tasks_by_date[date_str] = []
            tasks_by_date[date_str].append({
                'id': task.intrnl_task_id,
                'type': 'internal',
                'description': task.intrnl_task_description,
                'status': task.intrnl_task_status,
                'project_id': task.intrnl_project.intrnl_project_id if task.intrnl_project else 'N/A'
            })
        
        for task in external_tasks:
            date_str = task.task_deadline.strftime('%Y-%m-%d')
            if date_str not in tasks_by_date:
                tasks_by_date[date_str] = []
            tasks_by_date[date_str].append({
                'id': task.task_id,
                'type': 'external',
                'description': task.task_description,
                'status': task.task_status,
                'project_id': task.project.project_id if task.project else 'N/A'
            })
        
        context.update({
            'calendar': cal,
            'month_name': month_name,
            'year': year,
            'month': month,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'today': today,
            'tasks_by_date': json.dumps(tasks_by_date),
            'current_date': today.strftime('%Y-%m-%d')
        })
        
        return context

def calendar_tasks_json(request):
    """Return tasks for a specific month as JSON for AJAX requests"""
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        today = datetime.date.today()
        year = today.year
        month = today.month
    
    # Get all tasks for the month
    start_date = datetime.date(year, month, 1)
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime.date(year, month + 1, 1) - timedelta(days=1)
    
    internal_tasks = InternalProjectTaskList.objects.filter(
        intrnl_task_deadline__gte=start_date,
        intrnl_task_deadline__lte=end_date
    )
    
    external_tasks = ExternalProjectTaskList.objects.filter(
        task_deadline__gte=start_date,
        task_deadline__lte=end_date
    )
    
    # Prepare tasks for calendar display
    tasks_by_date = {}
    
    for task in internal_tasks:
        date_str = task.intrnl_task_deadline.strftime('%Y-%m-%d')
        if date_str not in tasks_by_date:
            tasks_by_date[date_str] = []
        tasks_by_date[date_str].append({
            'id': task.intrnl_task_id,
            'type': 'internal',
            'description': task.intrnl_task_description,
            'status': task.intrnl_task_status,
            'project_id': task.intrnl_project.intrnl_project_id if task.intrnl_project else 'N/A'
        })
    
    for task in external_tasks:
        date_str = task.task_deadline.strftime('%Y-%m-%d')
        if date_str not in tasks_by_date:
            tasks_by_date[date_str] = []
        tasks_by_date[date_str].append({
            'id': task.task_id,
            'type': 'external',
            'description': task.task_description,
            'status': task.task_status,
            'project_id': task.project.project_id if task.project else 'N/A'
        })
    
    return JsonResponse(tasks_by_date)

def calendar_add_task(request, date):
    """View to add a task from the calendar for a specific date"""
    try:
        task_date = parse_date(date)
        if task_date is None:
            raise ValueError("Invalid date format")
    except ValueError:
        messages.error(request, "Invalid date format")
        return redirect('task_calendar')
    
    task_type = request.GET.get('type', 'internal')
    
    if task_type == 'internal':
        form = InternalTaskForm(initial={'intrnl_task_deadline': task_date})
        template = 'project_tasks/internal_task_form.html'
    else:
        form = ExternalTaskForm(initial={'task_deadline': task_date})
        template = 'project_tasks/external_task_form.html'
    
    if request.method == 'POST':
        if task_type == 'internal':
            form = InternalTaskForm(request.POST)
        else:
            form = ExternalTaskForm(request.POST)
        
        if form.is_valid():
            task = form.save()
            messages.success(request, f"{task_type.capitalize()} task created successfully!")
            return redirect('task_calendar')
    
    return render(request, template, {
        'form': form,
        'selected_date': task_date,
        'task_type': task_type
    })