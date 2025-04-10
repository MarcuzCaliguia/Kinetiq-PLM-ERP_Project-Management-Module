from django import forms
from .models import ReportMonitoring
from datetime import date

class ReportMonitoringForm(forms.ModelForm):
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
    
    # Override all enum fields with ChoiceFields
    report_type = forms.ChoiceField(choices=REPORT_TYPE_CHOICES)
    received_from = forms.ChoiceField(choices=EXT_MODULES_CHOICES)
    assigned_to = forms.ChoiceField(choices=EXT_MODULES_CHOICES)
    
    class Meta:
        model = ReportMonitoring
        fields = ['report_type', 'report_title', 'received_from', 'date_created', 
                  'assigned_to', 'description']
        widgets = {
            'date_created': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'placeholder': 'Add Description', 'rows': 5}),
            'report_title': forms.TextInput(attrs={'placeholder': 'Name'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('date_created'):
            self.initial['date_created'] = date.today()
        
        # If editing an existing report, set the initial values
        if 'instance' in kwargs and kwargs['instance']:
            self.initial['report_type'] = kwargs['instance'].report_type
            self.initial['received_from'] = kwargs['instance'].received_from
            self.initial['assigned_to'] = kwargs['instance'].assigned_to