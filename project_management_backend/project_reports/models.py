from django.db import models
from django.db import connection
import uuid
from datetime import date

class ReportMonitoringManager(models.Manager):
    def create_report(self, report_type, report_title, received_from, date_created, assigned_to, description):
        # Generate a custom ID in the same format as the trigger would
        module_prefix = 'RPM'
        module_name = 'PROJ'
        unique_code = uuid.uuid4().hex[:6]
        report_id = f"{module_name}-{module_prefix}-{date.today().strftime('%Y')}-{unique_code}"
        
        # Use raw SQL to insert the record and explicitly set the ID
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO project_management.report_monitoring(
                    report_monitoring_id, report_type, report_title, 
                    received_from, date_created, assigned_to, description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING report_monitoring_id
            """, [
                report_id, report_type, report_title, 
                received_from, date_created, assigned_to, description
            ])
            result = cursor.fetchone()
            
        # Return the created report ID
        return result[0] if result else report_id

class ReportMonitoring(models.Model):
    report_monitoring_id = models.CharField(primary_key=True, max_length=255)
    report_type = models.TextField()
    report_title = models.CharField(max_length=255, blank=True, null=True)
    received_from = models.TextField(blank=True, null=True)
    date_created = models.DateField()
    assigned_to = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    objects = ReportMonitoringManager()

    class Meta:
        managed = False
        db_table = 'report_monitoring'  # Make sure to include the schema
    
    def __str__(self):
        return f"{self.report_title} ({self.report_type})"