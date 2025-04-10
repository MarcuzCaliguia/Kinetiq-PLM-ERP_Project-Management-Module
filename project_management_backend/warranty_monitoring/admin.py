from django.contrib import admin
from django.utils.html import format_html
from django import forms
from datetime import timedelta
from django.utils import timezone
import uuid

from .models import ExternalProjectWarranty, get_valid_external_projects

class WarrantyStatusFilter(admin.SimpleListFilter):
    title = 'Warranty Status'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('expiring_soon', 'Expiring Soon (30 days)'),
            ('expired', 'Expired'),
            ('not_started', 'Not Started'),
        )
    
    def queryset(self, request, queryset):
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)
        
        if self.value() == 'active':
            # Active warranties: started and not expired, with more than 30 days remaining
            return queryset.filter(
                warranty_start_date__lte=today,
                warranty_end_date__gt=thirty_days_later
            )
        elif self.value() == 'expiring_soon':
            # Expiring soon: started, not expired, but less than 30 days remaining
            return queryset.filter(
                warranty_start_date__lte=today,
                warranty_end_date__gt=today,
                warranty_end_date__lte=thirty_days_later
            )
        elif self.value() == 'expired':
            # Expired: end date is in the past
            return queryset.filter(warranty_end_date__lt=today)
        elif self.value() == 'not_started':
            # Not started: start date is in the future
            return queryset.filter(warranty_start_date__gt=today)
        return queryset


class WarrantyForm(forms.ModelForm):
    class Meta:
        model = ExternalProjectWarranty
        fields = ['project', 'warranty_coverage_yr', 'warranty_start_date']
        exclude = ['project_warranty_id', 'warranty_end_date']  # Exclude end date as it will be calculated
        widgets = {
            'warranty_start_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get project choices safely
        try:
            project_choices = get_valid_external_projects()
            if project_choices:
                self.fields['project'].choices = [('', '---------')] + project_choices
        except Exception as e:
            print(f"Error getting external projects: {e}")
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('warranty_start_date')
        coverage_yr = cleaned_data.get('warranty_coverage_yr')
        
        # Validate that we have required fields
        if not start_date:
            self.add_error('warranty_start_date', 'Start date is required')
        
        if not coverage_yr:
            self.add_error('warranty_coverage_yr', 'Warranty coverage years is required')
        elif coverage_yr <= 0:
            self.add_error('warranty_coverage_yr', 'Warranty coverage must be greater than 0')
        
        return cleaned_data
        return cleaned_data


@admin.register(ExternalProjectWarranty)
class WarrantyAdmin(admin.ModelAdmin):
    form = WarrantyForm
    list_display = ('project_warranty_id', 'get_project_id', 'get_project_name', 'warranty_coverage_yr', 
                   'warranty_start_date', 'warranty_end_date', 'get_status_badge', 'get_days_remaining')
    list_filter = (WarrantyStatusFilter, 'warranty_coverage_yr')
    search_fields = ('project_warranty_id', 'project__project_id', 'project__ext_project_request__ext_project_name')
    readonly_fields = ('project_warranty_id', 'warranty_end_date')
    
    def get_fieldsets(self, request, obj=None):
        if obj is None:  # Adding a new warranty
            return (
                (None, {
                    'fields': ('project', 'warranty_coverage_yr', 'warranty_start_date')
                }),
            )
        else:  # Editing an existing warranty
            return (
                (None, {
                    'fields': ('project_warranty_id', 'project', 'warranty_coverage_yr', 'warranty_start_date', 'warranty_end_date')
                }),
            )
    
    def get_project_id(self, obj):
        if obj.project:
            return obj.project.project_id
        return "N/A"
    get_project_id.short_description = 'Project ID'
    
    def get_project_name(self, obj):
        if obj.project and obj.project.ext_project_request:
            return obj.project.ext_project_request.ext_project_name
        return "N/A"
    get_project_name.short_description = 'Project Name'
    
    def get_status_badge(self, obj):
        status = obj.status
        if status == "Active":
            color = '#4CAF50'  # Green
        elif status == "Expiring Soon":
            color = '#FF9800'  # Orange
        elif status == "Expired":
            color = '#F44336'  # Red
        elif status == "Not Started":
            color = '#2196F3'  # Blue
        else:
            color = '#9E9E9E'  # Grey
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px;">{}</span>',
            color, status
        )
    get_status_badge.short_description = 'Status'
    
    def get_days_remaining(self, obj):
        days = obj.days_remaining
        if days <= 0 and obj.status == "Expired":
            return "Expired"
        elif days <= 0 and obj.status == "Not Started":
            return "Not Started"
        else:
            return f"{days} days"
    get_days_remaining.short_description = 'Days Remaining'
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True