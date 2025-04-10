from django.contrib import admin
from django.db import connection
from django.contrib import messages
from django import forms
from .models import InternalProjectRequest, ExternalProjectRequest
import uuid

class InternalProjectRequestForm(forms.ModelForm):
    class Meta:
        model = InternalProjectRequest
        fields = ['project_name', 'project_description', 'request_date', 
                 'request_valid_date', 'request_starting_date', 'project_type']


class ExternalProjectRequestForm(forms.ModelForm):
    class Meta:
        model = ExternalProjectRequest
        fields = ['ext_project_name', 'ext_project_description']


@admin.register(InternalProjectRequest)
class InternalProjectRequestAdmin(admin.ModelAdmin):
    form = InternalProjectRequestForm
    list_display = ('project_request_id', 'project_name', 'request_date', 
                   'request_starting_date', 'project_type', 'approval_id', 
                   'employee_id', 'dept_id')
    search_fields = ('project_request_id', 'project_name')
    list_filter = ('project_type', 'request_date')
    readonly_fields = ('project_request_id', 'approval_id', 'employee_id', 'dept_id')
    
    fieldsets = (
        (None, {
            'fields': ('project_name', 'project_description', 'project_type'),
        }),
        ('Dates', {
            'fields': ('request_date', 'request_valid_date', 'request_starting_date'),
        }),
    )
    
    def has_change_permission(self, request, obj=None):
        # Only allow adding new records, not editing existing ones
        return False
    
    def save_model(self, request, obj, form, change):
        # Generate a unique ID
        obj.project_request_id = f"INT-{uuid.uuid4().hex[:8]}"
        
        try:
            # Insert directly using SQL to handle enum type
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO internal_project_request 
                    (project_request_id, project_name, project_description, request_date, 
                    request_valid_date, request_starting_date, project_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::project_type)
                """, [
                    obj.project_request_id, 
                    obj.project_name, 
                    obj.project_description or '', 
                    obj.request_date, 
                    obj.request_valid_date, 
                    obj.request_starting_date, 
                    obj.project_type
                ])
            messages.success(request, "Created internal project request successfully. Other departments will add the necessary reference IDs.")
        except Exception as e:
            messages.error(request, f"Error creating project: {str(e)}")


@admin.register(ExternalProjectRequest)
class ExternalProjectRequestAdmin(admin.ModelAdmin):
    form = ExternalProjectRequestForm
    list_display = ('ext_project_request_id', 'ext_project_name', 'approval_id', 'item_id')
    search_fields = ('ext_project_request_id', 'ext_project_name')
    readonly_fields = ('ext_project_request_id', 'approval_id', 'item_id')
    
    fieldsets = (
        (None, {
            'fields': ('ext_project_name', 'ext_project_description'),
        }),
    )
    
    def has_change_permission(self, request, obj=None):
        # Only allow adding new records, not editing existing ones
        return False
    
    def save_model(self, request, obj, form, change):
        # Generate a unique ID
        obj.ext_project_request_id = f"EXT-{uuid.uuid4().hex[:8]}"
        
        try:
            # Insert directly using SQL
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO external_project_request 
                    (ext_project_request_id, ext_project_name, ext_project_description)
                    VALUES (%s, %s, %s)
                """, [
                    obj.ext_project_request_id, 
                    obj.ext_project_name, 
                    obj.ext_project_description or ''
                ])
            messages.success(request, "Created external project request successfully. Other departments will add the necessary reference IDs.")
        except Exception as e:
            messages.error(request, f"Error creating project: {str(e)}")