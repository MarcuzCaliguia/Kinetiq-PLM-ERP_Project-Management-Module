# models.py
from django.db import models

class ProjectCosts(models.Model):
    project_resources_id = models.CharField(primary_key=True, max_length=255)
    project_id = models.CharField(max_length=255, null=True, blank=True)
    bom_id = models.CharField(max_length=255, null=True, blank=True)
    budget_approvals_id = models.CharField(max_length=255, null=True, blank=True)
    intrnl_project_id = models.CharField(max_length=255, null=True, blank=True)
    outside_labor_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    utility_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    outsourced_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    overall_project_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'project_management.project_costs'

class ExternalProjectDetails(models.Model):
    PROJECT_STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    MILESTONE_CHOICES = [
        ('planning', 'Planning'),
        ('design', 'Design'),
        ('implementation', 'Implementation'),
        ('testing', 'Testing'),
        ('deployment', 'Deployment'),
        ('maintenance', 'Maintenance'),
    ]
    
    WARRANTY_STATUS_CHOICES = [
        ('not started', 'Not Started'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]
    
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request_id = models.CharField(max_length=255, null=True, blank=True)
    project_status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES)
    project_milestone = models.CharField(max_length=20, choices=MILESTONE_CHOICES, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    estimated_end_date = models.DateField(null=True, blank=True)
    warranty_coverage_yr = models.IntegerField(null=True, blank=True)
    warranty_start_date = models.DateField(null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)
    project_issues = models.TextField(null=True, blank=True)
    warranty_status = models.CharField(max_length=20, choices=WARRANTY_STATUS_CHOICES, default='not started')
    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = 'project_management.external_project_details'

class InternalProjectDetails(models.Model):
    PROJECT_STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    intrnl_project_id = models.CharField(primary_key=True, max_length=255)
    project_request_id = models.CharField(max_length=255, null=True, blank=True)
    intrnl_project_status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES)
    approval_id = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    estimated_end_date = models.DateField(null=True, blank=True)
    project_issues = models.TextField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = 'project_management.internal_project_details'