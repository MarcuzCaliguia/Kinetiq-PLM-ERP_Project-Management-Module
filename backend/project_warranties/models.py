from django.db import models

class ExternalProjectWarranty(models.Model):
    project_warranty_id = models.CharField(max_length=255, primary_key=True)
    project_id = models.CharField(max_length=255)
    warranty_coverage_yr = models.IntegerField()
    warranty_start_date = models.DateField()
    warranty_end_date = models.DateField()
    
    class Meta:
        db_table = 'external_project_warranty'
        managed = False

class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request = models.ForeignKey(
        to='ExternalProjectRequest',  
        on_delete=models.DO_NOTHING,
        db_column='ext_project_request_id',  
        blank=True,
        null=True
    )
    project_status = models.TextField()
    
    class Meta:
        managed = False
        db_table = 'external_project_details'

class ExternalProjectRequest(models.Model):
    request_id = models.CharField(primary_key=True, max_length=255)
    
    class Meta:
        managed = False
        db_table = 'external_project_request'