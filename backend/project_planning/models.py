from django.db import models

class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50, blank=True, null=True)
    ext_project_description = models.TextField(blank=True, null=True)
    approval_id = models.CharField(max_length=255, blank=True, null=True)
    item_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_request'

class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request = models.ForeignKey('ExternalProjectRequest', models.DO_NOTHING, db_column='ext_project_request_id', blank=True, null=True)
    project_status = models.TextField()  

    class Meta:
        managed = False
        db_table = 'external_project_details'
        
class ExternalProjectLabor(models.Model):
    project_labor_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, db_column='project_id', blank=True, null=True)
    job_role_needed = models.CharField(max_length=255, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_labor'

class ExternalProjectEquipments(models.Model):
    project_equipment_list_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, db_column='project_id', blank=True, null=True)
    project_equipment_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_equipments'

class ExternalProjectWarranty(models.Model):
    project_warranty_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, db_column='project_id', blank=True, null=True)
    warranty_coverage_yr = models.IntegerField()
    warranty_start_date = models.DateField()
    warranty_end_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'external_project_warranty'

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
        
class InternalProjectDetails(models.Model):
    intrnl_project_id = models.CharField(primary_key=True, max_length=255)
    project_request = models.ForeignKey('InternalProjectRequest', models.DO_NOTHING, db_column='project_request_id', blank=True, null=True)
    intrnl_project_status = models.TextField()  
    approval_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_details'
        
class InternalProjectLabor(models.Model):
    intrnl_project_labor_id = models.CharField(primary_key=True, max_length=255)
    intrnl_project = models.ForeignKey(InternalProjectDetails, models.DO_NOTHING, db_column='intrnl_project_id', blank=True, null=True)
    intrnl_job_role_needed = models.CharField(max_length=255, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_labor'