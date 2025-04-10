from django.db import models
from django.db import connection
from django.utils import timezone
from datetime import timedelta
import uuid


def get_valid_external_projects():
    """Get a list of valid external projects with their names"""
    projects = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT epd.project_id, epr.ext_project_name
            FROM external_project_details epd
            JOIN external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
            ORDER BY epr.ext_project_name
        """)
        for row in cursor.fetchall():
            projects.append((row[0], f"{row[0]} - {row[1]}"))
    return projects

class ArchivedWarranty(models.Model):
    """Store IDs of archived warranties"""
    warranty_id = models.CharField(max_length=255, primary_key=True)
    archived_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'archived_warranties'
        managed = True
        
class ExternalProjectWarranty(models.Model):
    project_warranty_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey('ExternalProjectDetails', models.DO_NOTHING, blank=True, null=True)
    warranty_coverage_yr = models.IntegerField(verbose_name="Warranty Coverage (Years)")
    warranty_start_date = models.DateField(verbose_name="Start Date")
    warranty_end_date = models.DateField(verbose_name="End Date")

    class Meta:
        managed = False
        db_table = 'external_project_warranty'
        verbose_name = 'Project Warranty'
        verbose_name_plural = 'Project Warranties'
        ordering = ['-warranty_end_date']

    def __str__(self):
        return f"Warranty {self.project_warranty_id} - {self.project.project_id if self.project else 'No Project'}"
    
    def save(self, *args, **kwargs):
        # Generate ID if not provided
        if not self.project_warranty_id:
            self.project_warranty_id = f"EPW-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate end date based on warranty coverage years
        if self.warranty_start_date and self.warranty_coverage_yr:
            # Add years to the start date
            self.warranty_end_date = self.warranty_start_date + timedelta(days=365 * self.warranty_coverage_yr)
        
        # Ensure end date is at least one day after start date
        if self.warranty_start_date and self.warranty_end_date and self.warranty_end_date <= self.warranty_start_date:
            self.warranty_end_date = self.warranty_start_date + timedelta(days=1)
        
        super().save(*args, **kwargs)
    
    @property
    def days_remaining(self):
        if not self.warranty_end_date:
            return 0
        
        today = timezone.now().date()
        if today > self.warranty_end_date:
            return 0
        
        delta = self.warranty_end_date - today
        return delta.days
    
    @property
    def status(self):
        today = timezone.now().date()
        
        if not self.warranty_start_date or not self.warranty_end_date:
            return "Unknown"
        
        if today < self.warranty_start_date:
            return "Not Started"
        elif today > self.warranty_end_date:
            return "Expired"
        else:
            days_left = self.days_remaining
            if days_left <= 30:
                return "Expiring Soon"
            else:
                return "Active"


# Reference models for ForeignKey relationships
class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request = models.ForeignKey('ExternalProjectRequest', models.DO_NOTHING, blank=True, null=True)
    project_status = models.TextField()

    class Meta:
        managed = False
        db_table = 'external_project_details'
        
    def __str__(self):
        return self.project_id


class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'external_project_request'
        
    def __str__(self):
        return self.ext_project_name