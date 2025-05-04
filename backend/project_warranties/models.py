from django.db import models

class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50, null=True, blank=True)
    approval_id = models.CharField(max_length=255, null=True, blank=True)
    item_id = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'project_management"."external_project_request'

class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request_id = models.CharField(max_length=255, blank=True, null=True)
    project_status = models.CharField(max_length=50)
    project_milestone = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    estimated_end_date = models.DateField(blank=True, null=True)
    warranty_coverage_yr = models.IntegerField(blank=True, null=True)
    warranty_start_date = models.DateField(blank=True, null=True)
    warranty_end_date = models.DateField(blank=True, null=True)
    project_issues = models.TextField(blank=True, null=True)
    warranty_status = models.CharField(max_length=50, blank=True, null=True, default='not started')
    
    class Meta:
        managed = False
        db_table = 'project_management"."external_project_details'

class ProjectWarrantyView(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50, blank=True, null=True)
    warranty_coverage_yr = models.IntegerField(blank=True, null=True)
    warranty_status = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'project_management"."project_warranty_view'

class ExternalProjectsDetails(models.Model):
    ext_project_name = models.CharField(max_length=50, blank=True, null=True)
    item_name = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    special_requests = models.TextField(blank=True, null=True)
    project_status = models.CharField(max_length=50, blank=True, null=True)
    project_milestone = models.CharField(max_length=50, blank=True, null=True)
    warranty_status = models.CharField(max_length=50, blank=True, null=True)
    approval_status = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'project_management"."external_projects_details'