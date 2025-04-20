from django.db import models
from django.db import connection

class ReportMonitoring(models.Model):
    report_monitoring_id = models.CharField(primary_key=True, max_length=255)
    project_id = models.CharField(max_length=255, blank=True, null=True)
    intrnl_project_id = models.CharField(max_length=255, blank=True, null=True)
    report_type = models.CharField(max_length=255)  
    report_title = models.CharField(max_length=255, blank=True, null=True)
    received_from = models.CharField(max_length=255, blank=True, null=True)  
    date_created = models.DateField()
    assigned_to = models.CharField(max_length=255, blank=True, null=True)  
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'report_monitoring'
    
    def __str__(self):
        return f"{self.report_title} ({self.report_type})"

    @classmethod
    def create_report(cls, report_type, report_title, received_from, date_created, assigned_to, description, project_id=None, intrnl_project_id=None):

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO report_monitoring(
                    project_id, intrnl_project_id, report_type, report_title, 
                    received_from, date_created, assigned_to, description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING report_monitoring_id
            """, [
                project_id, intrnl_project_id, report_type, report_title, 
                received_from, date_created, assigned_to, description
            ])
            result = cursor.fetchone()
            
        return result[0] if result else None

class ExternalProject(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request_id = models.CharField(max_length=255, blank=True, null=True)
    project_status = models.CharField(max_length=255)  

    class Meta:
        managed = False
        db_table = 'external_project_details'
    
    def __str__(self):
        return f"{self.project_id} ({self.project_status})"

class InternalProject(models.Model):
    intrnl_project_id = models.CharField(primary_key=True, max_length=255)
    project_request_id = models.CharField(max_length=255, blank=True, null=True)
    intrnl_project_status = models.CharField(max_length=255) 
    approval_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_details'
    
    def __str__(self):
        return f"{self.intrnl_project_id} ({self.intrnl_project_status})"
    
class Equipment(models.Model):
    equipment_id = models.CharField(primary_key=True, max_length=255)
    equipment_name = models.CharField(max_length=255)
    description = models.TextField()
    availability_status = models.CharField(max_length=50)
    last_maintenance_date = models.DateField()
    equipment_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'equipment'
        
class Employees(models.Model):
    employee_id = models.CharField(primary_key=True, max_length=255)
    position = models.ForeignKey('Positions', models.DO_NOTHING, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'employees'
        
class Positions(models.Model):
    position_id = models.CharField(primary_key=True, max_length=255)
    position_title = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'positions'