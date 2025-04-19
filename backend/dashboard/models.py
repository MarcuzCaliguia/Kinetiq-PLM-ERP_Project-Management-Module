from django.db import models

class ExternalProjectLabor(models.Model):
    project_labor_id = models.CharField(primary_key=True, max_length=255)
    job_role_needed = models.CharField(max_length=255, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_labor'

class InternalProjectLabor(models.Model):
    intrnl_project_labor_id = models.CharField(primary_key=True, max_length=255)
    intrnl_job_role_needed = models.CharField(max_length=255, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_labor'
        
class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    project_status = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'external_project_details'

class InternalProjectDetails(models.Model):
    intrnl_project_id = models.CharField(primary_key=True, max_length=255)
    project_request = models.ForeignKey('InternalProjectRequest', models.DO_NOTHING, blank=True, null=True)
    intrnl_project_status = models.TextField()  # This field type is a guess.
    approval_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_details'
    
class ExternalProjectTracking(models.Model):
    project_tracking_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    project_milestone = models.TextField()  # This field type is a guess.
    start_date = models.DateField()
    estimated_end_date = models.DateField()
    project_warranty = models.ForeignKey('ExternalProjectWarranty', models.DO_NOTHING, blank=True, null=True)
    project_issue = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_tracking'

class InternalProjectTracking(models.Model):
    intrnl_project_tracking_id = models.CharField(primary_key=True, max_length=255)
    intrnl_project = models.ForeignKey(InternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    intrnl_start_date = models.DateField()
    intrnl_estimated_end_date = models.DateField()
    intrnl_project_issue = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_tracking'
        
class ExternalProjectTaskList(models.Model):
    task_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    task_status = models.TextField()  # This field type is a guess.
    task_deadline = models.DateField()
    project_labor = models.ForeignKey(ExternalProjectLabor, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_task_list'

class InternalProjectTaskList(models.Model):
    intrnl_task_id = models.CharField(primary_key=True, max_length=255)
    intrnl_project = models.ForeignKey(InternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    intrnl_task_description = models.TextField(blank=True, null=True)
    intrnl_task_status = models.TextField()  # This field type is a guess.
    intrnl_task_deadline = models.DateField()
    intrnl_project_labor = models.ForeignKey(InternalProjectLabor, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_task_list'
        
class ExternalProjectWarranty(models.Model):
    project_warranty_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    warranty_coverage_yr = models.IntegerField()
    warranty_start_date = models.DateField()
    warranty_end_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'external_project_warranty'

class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50, blank=True, null=True)
    ext_project_description = models.TextField(blank=True, null=True)
    approval_id = models.CharField(max_length=255, blank=True, null=True)
    item_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_request'
        
class InternalProjectRequest(models.Model):
    project_request_id = models.CharField(primary_key=True, max_length=255)
    project_name = models.CharField(max_length=50)
    project_description = models.TextField(blank=True, null=True)
    request_date = models.DateField()
    target_starting_date = models.DateField()
    employee_id = models.CharField(max_length=255, blank=True, null=True)
    dept_id = models.CharField(max_length=255, blank=True, null=True)
    project_budget_request = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    project_budget_description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_request'