from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from .models import ReportMonitoring
from datetime import date

class ReportMonitoringAddForm(forms.Form):
    # Define choices based on your database enum values
    REPORT_TYPE_CHOICES = [
        ('Sales Order', 'Sales Order'),
        ('Resource Availability', 'Resource Availability'),
        ('Bill of Material', 'Bill of Material'),
        ('Information', 'Information'),
        ('Progress Report', 'Progress Report'),
        ('Project Details', 'Project Details'),
    ]
    
    # Define choices for ext_modules enum (used by both received_from and assigned_to)
    EXT_MODULES_CHOICES = [
        ('Accounting', 'Accounting'),
        ('Admin', 'Admin'),
        ('Distribution', 'Distribution'),
        ('Finance', 'Finance'),
        ('Human Resources', 'Human Resources'),
        ('Inventory', 'Inventory'),
        ('Management', 'Management'),
        ('MRP', 'MRP'),
        ('Operations', 'Operations'),
        ('Production', 'Production'),
        ('Project Management', 'Project Management'),
        ('Purchasing', 'Purchasing'),
        ('Sales', 'Sales'),
        ('Services', 'Services'),
        ('Solution Customizing', 'Solution Customizing'),
    ]
    
    report_type = forms.ChoiceField(choices=REPORT_TYPE_CHOICES)
    report_title = forms.CharField(max_length=255)
    received_from = forms.ChoiceField(choices=EXT_MODULES_CHOICES)
    date_created = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=date.today)
    assigned_to = forms.ChoiceField(choices=EXT_MODULES_CHOICES)
    description = forms.CharField(widget=forms.Textarea, required=False)

class ReportMonitoringAdmin(admin.ModelAdmin):
    list_display = ('report_monitoring_id', 'report_type', 'report_title', 'received_from', 
                   'date_created', 'assigned_to')
    list_filter = ('report_type', 'date_created', 'received_from', 'assigned_to')
    search_fields = ('report_monitoring_id', 'report_title', 'report_type')
    ordering = ('-date_created',)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add-report/', self.admin_site.admin_view(self.add_report_view), name='add_report'),
        ]
        return custom_urls + urls
    
    def add_report_view(self, request):
        if request.method == 'POST':
            form = ReportMonitoringAddForm(request.POST)
            if form.is_valid():
                # Use the custom manager to create the report
                report_id = ReportMonitoring.objects.create_report(
                    report_type=form.cleaned_data['report_type'],
                    report_title=form.cleaned_data['report_title'],
                    received_from=form.cleaned_data['received_from'],
                    date_created=form.cleaned_data['date_created'],
                    assigned_to=form.cleaned_data['assigned_to'],
                    description=form.cleaned_data['description']
                )
                self.message_user(request, f"Report '{form.cleaned_data['report_title']}' was added successfully with ID {report_id}", messages.SUCCESS)
                return HttpResponseRedirect("../")
        else:
            form = ReportMonitoringAddForm()
        
        context = {
            'title': 'Add Report',
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/report_monitoring/add_report.html', context)
    
    def add_view(self, request, form_url='', extra_context=None):
        # Redirect the standard add view to our custom view
        return HttpResponseRedirect("add-report/")

admin.site.register(ReportMonitoring, ReportMonitoringAdmin)