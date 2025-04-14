from django import forms
from datetime import date
from .models import ReportMonitoring, ExternalProject, InternalProject


class ReportMonitoringForm(forms.ModelForm):
    REPORT_TYPE_CHOICES = [
        ('Sales Order', 'Sales Order'),
        ('Resource Availability', 'Resource Availability'),
        ('Bill of Material', 'Bill of Material'),
        ('Information', 'Information'),
        ('Progress Report', 'Progress Report'),
        ('Project Details', 'Project Details'),
        ('Inventory Movement', 'Inventory Movement'),
    ]
    
    MODULE_CHOICES = [
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
        ('Department - IT Team', 'Department - IT Team'),
        ('Department - Project Management', 'Department - Project Management'),
    ]
    
    def get_external_project_choices():
        choices = [('', '---------')]
        projects = ExternalProject.objects.all().order_by('project_id')
        for project in projects:
            choices.append((project.project_id, f"{project.project_id}"))
        return choices
    
    def get_internal_project_choices():
        choices = [('', '---------')]
        projects = InternalProject.objects.all().order_by('intrnl_project_id')
        for project in projects:
            choices.append((project.intrnl_project_id, f"{project.intrnl_project_id}"))
        return choices
    
    project_id = forms.ChoiceField(
        choices=get_external_project_choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    intrnl_project_id = forms.ChoiceField(
        choices=get_internal_project_choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    report_title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter report title',
            'class': 'form-control'
        })
    )
    
    received_from = forms.ChoiceField(
        choices=MODULE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assigned_to = forms.ChoiceField(
        choices=MODULE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_created = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': 'Enter report description',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = ReportMonitoring
        fields = ['project_id', 'intrnl_project_id', 'report_type', 'report_title', 
                  'received_from', 'date_created', 'assigned_to', 'description']
    
    def clean(self):
        cleaned_data = super().clean()
        project_id = cleaned_data.get('project_id')
        intrnl_project_id = cleaned_data.get('intrnl_project_id')
        
        if project_id == '':
            project_id = None
            cleaned_data['project_id'] = None
            
        if intrnl_project_id == '':
            intrnl_project_id = None
            cleaned_data['intrnl_project_id'] = None
        
        if not project_id and not intrnl_project_id:
            self.add_error(None, "Either Project ID or Internal Project ID must be provided.")
        
        if project_id and intrnl_project_id:
            self.add_error(None, "Please provide either Project ID or Internal Project ID, not both.")
        
        return cleaned_data

class ReportFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by title or ID',
            'class': 'form-control'
        })
    )
    
    report_type = forms.ChoiceField(
        choices=[('', '-- All Report Types --')] + ReportMonitoringForm.REPORT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'From'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'To'
        })
    )
    
    project_type = forms.ChoiceField(
        choices=[
            ('', '-- All Projects --'),
            ('external', 'External Projects'),
            ('internal', 'Internal Projects')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_report_title(self):
        title = self.cleaned_data.get('report_title')
        if title:
            if len(title) < 5:
                raise forms.ValidationError("Report title must be at least 5 characters long.")
            
            generic_titles = ['report', 'test', 'new report', 'project report']
            if title.lower() in generic_titles:
                raise forms.ValidationError("Please provide a more descriptive title.")
        
        return title

    def clean_date_created(self):
        date_created = self.cleaned_data.get('date_created')
        if date_created:
            if date_created > date.today():
                raise forms.ValidationError("Date created cannot be in the future.")
        
        return date_created
    
    


