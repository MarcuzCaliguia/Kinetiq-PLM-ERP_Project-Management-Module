# models.py updates
from django.db import models

class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50, blank=True, null=True)
    ext_project_description = models.TextField(blank=True, null=True)
    approval_id = models.CharField(max_length=255, blank=True, null=True)
    item_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.external_project_request'

class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request = models.ForeignKey('ExternalProjectRequest', models.DO_NOTHING, db_column='ext_project_request_id', blank=True, null=True)
    project_status = models.TextField()  # This field type is a guess.
    project_milestone = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    estimated_end_date = models.DateField(blank=True, null=True)
    warranty_coverage_yr = models.IntegerField(blank=True, null=True)
    warranty_start_date = models.DateField(blank=True, null=True)
    warranty_end_date = models.DateField(blank=True, null=True)
    project_issues = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.external_project_details'

class InternalProjectRequest(models.Model):
    project_request_id = models.CharField(primary_key=True, max_length=255)
    project_name = models.CharField(max_length=50, blank=True, null=True)
    project_description = models.TextField(blank=True, null=True)
    target_starting_date = models.DateField(blank=True, null=True)
    project_budget_request = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    project_budget_description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.internal_project_request'

class InternalProjectDetails(models.Model):
    intrnl_project_id = models.CharField(primary_key=True, max_length=255)
    project_request = models.ForeignKey('InternalProjectRequest', models.DO_NOTHING, db_column='project_request_id', blank=True, null=True)
    intrnl_project_status = models.TextField()  # This field type is a guess.
    approval_id = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    estimated_end_date = models.DateField(blank=True, null=True)
    project_issues = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.internal_project_details'

class Employee(models.Model):
    employee_id = models.CharField(primary_key=True, max_length=255)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    # Add other fields as needed

    class Meta:
        managed = False
        db_table = 'human_resources.employees'

class ProjectLabor(models.Model):
    project_labor_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, db_column='project_id', blank=True, null=True)
    job_role_needed = models.CharField(max_length=255, blank=True, null=True)
    employee = models.ForeignKey(Employee, models.DO_NOTHING, db_column='employee_id', blank=True, null=True)
    intrnl_project = models.ForeignKey(InternalProjectDetails, models.DO_NOTHING, db_column='intrnl_project_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.project_labor'

class ProjectTasks(models.Model):
    task_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, db_column='project_id', blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    task_status = models.TextField()  # This field type is a guess.
    task_deadline = models.DateField()
    project_labor = models.ForeignKey(ProjectLabor, models.DO_NOTHING, db_column='project_labor_id', blank=True, null=True)
    intrnl_project = models.ForeignKey(InternalProjectDetails, models.DO_NOTHING, db_column='intrnl_project_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_management.project_tasks'

# If you need Management Approvals model
class ManagementApproval(models.Model):
    approval_id = models.CharField(primary_key=True, max_length=255)
    # Add other fields as needed

    class Meta:
        managed = False
        db_table = 'management.management_approvals'