from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import InternalProjectTask, ExternalProjectTask

class InternalTaskForm(forms.ModelForm):
    class Meta:
        model = InternalProjectTask
        fields = ['intrnl_project_id', 'intrnl_task_description', 'intrnl_task_status', 'intrnl_task_deadline', 'intrnl_project_labor_id']
        
    def clean_intrnl_task_deadline(self):
        deadline = self.cleaned_data.get('intrnl_task_deadline')
        if deadline and deadline < date.today():
            raise ValidationError("Deadline cannot be in the past")
        return deadline

class ExternalTaskForm(forms.ModelForm):
    class Meta:
        model = ExternalProjectTask
        fields = ['project_id', 'task_description', 'task_status', 'task_deadline', 'project_labor_id']
        
    def clean_task_deadline(self):
        deadline = self.cleaned_data.get('task_deadline')
        if deadline and deadline < date.today():
            raise ValidationError("Deadline cannot be in the past")
        return deadline