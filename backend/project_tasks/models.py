from django.db import models

class Employees(models.Model):
    employee_id = models.CharField(primary_key=True, max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employees'

class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    
    class Meta:
        managed = False
        db_table = 'external_project_request'

class InternalProjectRequest(models.Model):
    intrnl_project_request_id = models.CharField(primary_key=True, max_length=255)
    
    class Meta:
        managed = False
        db_table = 'internal_project_request'

class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request = models.ForeignKey('ExternalProjectRequest', models.DO_NOTHING, blank=True, null=True)
    project_status = models.TextField() 

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

class ExternalProjectLabor(models.Model):
    project_labor_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    job_role_needed = models.CharField(max_length=255, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_labor'
        
class InternalProjectLabor(models.Model):
    intrnl_project_labor_id = models.CharField(primary_key=True, max_length=255)
    intrnl_project = models.ForeignKey(InternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    intrnl_job_role_needed = models.CharField(max_length=255, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_labor'

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
    intrnl_task_status = models.TextField() 
    intrnl_task_deadline = models.DateField()
    intrnl_project_labor = models.ForeignKey(InternalProjectLabor, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_task_list'