from django.db import models
from django.utils import timezone

class InternalProjectRequest(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('plans', 'Plans'),
        ('changes', 'Changes'),
        ('trainings', 'Trainings'),
    ]
    
    project_request_id = models.CharField(primary_key=True, max_length=255)
    project_name = models.CharField(max_length=50)
    project_description = models.TextField(blank=True, null=True)
    request_date = models.DateField(default=timezone.now)
    request_valid_date = models.DateField()
    request_starting_date = models.DateField()
    approval_id = models.CharField(max_length=255, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)
    dept_id = models.CharField(max_length=255, blank=True, null=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    
    class Meta:
        managed = False
        db_table = 'internal_project_request'
        verbose_name = 'Internal Project Request'
        verbose_name_plural = 'Internal Project Requests'
    
    def __str__(self):
        return f"{self.project_name} ({self.project_request_id})"


class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50)
    ext_project_description = models.TextField(blank=True, null=True)
    approval_id = models.CharField(max_length=255, blank=True, null=True)
    item_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'external_project_request'
        verbose_name = 'External Project Request'
        verbose_name_plural = 'External Project Requests'
    
    def __str__(self):
        return f"{self.ext_project_name} ({self.ext_project_request_id})"