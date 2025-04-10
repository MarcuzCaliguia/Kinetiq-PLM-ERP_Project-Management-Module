from django import forms
from .models import (
    InternalProjectTaskList, ExternalProjectTaskList,
    get_valid_internal_project_ids, get_valid_external_project_ids,
    get_valid_internal_labor_ids, get_valid_external_labor_ids
)
import uuid

class InternalTaskForm(forms.ModelForm):
    class Meta:
        model = InternalProjectTaskList
        fields = ['intrnl_project', 'intrnl_task_description', 'intrnl_task_status', 
                 'intrnl_task_deadline', 'intrnl_project_labor']
        exclude = ['intrnl_task_id']
        widgets = {
            'intrnl_task_deadline': forms.DateInput(attrs={'type': 'date'}),
            'intrnl_task_description': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update these values to match the database enum values
        self.fields['intrnl_task_status'].widget = forms.Select(choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled')
        ])
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.intrnl_task_id:
            instance.intrnl_task_id = f"ITASK-{uuid.uuid4().hex[:8].upper()}"
        if commit:
            instance.save()
        return instance

class ExternalTaskForm(forms.ModelForm):
    class Meta:
        model = ExternalProjectTaskList
        fields = ['project', 'task_description', 'task_status', 
                 'task_deadline', 'project_labor']
        exclude = ['task_id']
        widgets = {
            'task_deadline': forms.DateInput(attrs={'type': 'date'}),
            'task_description': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update these values to match the database enum values
        self.fields['task_status'].widget = forms.Select(choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled')
        ])
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.task_id:
            instance.task_id = f"ETASK-{uuid.uuid4().hex[:8].upper()}"
        if commit:
            instance.save()
        return instance