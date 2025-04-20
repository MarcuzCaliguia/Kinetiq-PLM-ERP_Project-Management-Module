from django.db import models

class Department(models.Model):
    dept_id = models.CharField(max_length=255, primary_key=True)
    dept_name = models.CharField(max_length=100)
    
    class Meta:
        managed = False
        db_table = 'human_resources.departments'

class Employee(models.Model):
    employee_id = models.CharField(max_length=255, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    class Meta:
        managed = False
        db_table = 'human_resources.employees'

class InternalProjectRequest(models.Model):
    project_request_id = models.CharField(max_length=255, primary_key=True)
    project_name = models.CharField(max_length=50)
    project_description = models.TextField(null=True, blank=True)
    request_date = models.DateField()
    target_starting_date = models.DateField()
    employee_id = models.CharField(max_length=255, null=True)
    dept_id = models.CharField(max_length=255, null=True)
    project_budget_request = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    project_budget_description = models.TextField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'project_management.internal_project_request'