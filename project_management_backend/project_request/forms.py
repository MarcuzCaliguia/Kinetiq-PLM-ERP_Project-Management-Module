# forms.py
from django import forms
from .models import InternalProjectRequest, ExternalProjectRequest
from django.utils import timezone
from django.db import connection

class InternalProjectRequestForm(forms.ModelForm):
    class Meta:
        model = InternalProjectRequest
        fields = [
            'project_name', 'project_description', 'request_valid_date',
            'request_starting_date', 'employee_id', 'dept_id', 'project_type'
        ]
        widgets = {
            'request_valid_date': forms.DateInput(attrs={'type': 'date'}),
            'request_starting_date': forms.DateInput(attrs={'type': 'date'}),
            'project_description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get available employee IDs
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT employee_id, first_name, last_name FROM human_resources.employees LIMIT 100")
                employees = cursor.fetchall()
                if employees:
                    employee_choices = [('', '---------')] + [(emp[0], f"{emp[0]} - {emp[1]} {emp[2]}") for emp in employees]
                    self.fields['employee_id'] = forms.ChoiceField(choices=employee_choices, required=False)
        except Exception:
            # Keep as text field if query fails
            pass
            
        # Get available department IDs
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT dept_id, dept_name FROM human_resources.departments")
                departments = cursor.fetchall()
                if departments:
                    department_choices = [('', '---------')] + [(dept[0], f"{dept[0]} - {dept[1]}") for dept in departments]
                    self.fields['dept_id'] = forms.ChoiceField(choices=department_choices, required=False)
        except Exception:
            # Keep as text field if query fails
            pass
    
    def clean(self):
        cleaned_data = super().clean()
        request_valid_date = cleaned_data.get('request_valid_date')
        request_starting_date = cleaned_data.get('request_starting_date')
        
        if request_valid_date and request_starting_date:
            if request_valid_date < timezone.now().date():
                raise forms.ValidationError("Valid date cannot be in the past")
            if request_starting_date < timezone.now().date():
                raise forms.ValidationError("Starting date cannot be in the past")
        
        return cleaned_data


class ExternalProjectRequestForm(forms.ModelForm):
    class Meta:
        model = ExternalProjectRequest
        fields = ['ext_project_name', 'ext_project_description', 'item_id']
        widgets = {
            'ext_project_description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get available order IDs
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT order_id FROM sales.orders LIMIT 100")
                orders = cursor.fetchall()
                if orders:
                    order_choices = [('', '---------')] + [(order[0], order[0]) for order in orders]
                    self.fields['item_id'] = forms.ChoiceField(choices=order_choices, required=False)
        except Exception:
            # Keep as text field if query fails
            pass