from django.db import models

class Employees(models.Model):
    employee_id = models.CharField(primary_key=True, max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'human_resources.employees'

class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50, blank=True, null=True)
    ext_project_description = models.TextField(blank=True, null=True)
    approval_id = models.CharField(max_length=255, blank=True, null=True)
    item_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'project_management.external_project_request'

class InternalProjectRequest(models.Model):
    project_request_id = models.CharField(primary_key=True, max_length=255)
    project_name = models.CharField(max_length=50, blank=True, null=True)
    request_date = models.DateField(blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)
    dept_id = models.CharField(max_length=255, blank=True, null=True)
    reason_for_request = models.TextField(blank=True, null=True)
    materials_needed = models.TextField(blank=True, null=True)
    equipments_needed = models.TextField(blank=True, null=True)
    project_type = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'project_management.internal_project_request'

class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request_id = models.CharField(max_length=255, blank=True, null=True)
    project_status = models.TextField()
    project_milestone = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    estimated_end_date = models.DateField(blank=True, null=True)
    warranty_coverage_yr = models.IntegerField(blank=True, null=True)
    warranty_start_date = models.DateField(blank=True, null=True)
    warranty_end_date = models.DateField(blank=True, null=True)
    project_issues = models.TextField(blank=True, null=True)
    warranty_status = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.external_project_details'

class InternalProjectDetails(models.Model):
    intrnl_project_id = models.CharField(primary_key=True, max_length=255)
    project_request_id = models.CharField(max_length=255, blank=True, null=True)
    intrnl_project_status = models.TextField()
    approval_id = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    estimated_end_date = models.DateField(blank=True, null=True)
    project_issues = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.internal_project_details'

class ProjectLabor(models.Model):
    project_labor_id = models.CharField(primary_key=True, max_length=255)
    project_id = models.CharField(max_length=255, blank=True, null=True)
    job_role_needed = models.CharField(max_length=255, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)
    intrnl_project_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.project_labor'

class ProjectTasks(models.Model):
    task_id = models.CharField(primary_key=True, max_length=255)
    project_id = models.CharField(max_length=255, blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    task_status = models.TextField()
    task_deadline = models.DateField()
    project_labor_id = models.CharField(max_length=255, blank=True, null=True)
    intrnl_project_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.project_tasks'

# Models for the views
class ExternalProjectTasks(models.Model):
    task_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50, blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    task_status = models.TextField()
    task_deadline = models.DateField()
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.external_project_tasks'

class InternalProjectTasks(models.Model):
    task_id = models.CharField(primary_key=True, max_length=255)
    project_name = models.CharField(max_length=50, blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    task_status = models.TextField()
    task_deadline = models.DateField()
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.internal_project_tasks'