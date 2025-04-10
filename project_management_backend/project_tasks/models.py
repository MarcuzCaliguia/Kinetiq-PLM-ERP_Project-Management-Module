from django.db import models
from django.utils import timezone
from django.db import connection
from datetime import datetime
import uuid

class InternalProjectTaskList(models.Model):
    intrnl_task_id = models.CharField(primary_key=True, max_length=255, verbose_name="Task ID")
    intrnl_project = models.ForeignKey('InternalProjectDetails', models.DO_NOTHING, blank=True, null=True, verbose_name="Project")
    intrnl_task_description = models.TextField(blank=True, null=True, verbose_name="Description")
    intrnl_task_status = models.CharField(max_length=50, verbose_name="Status")
    intrnl_task_deadline = models.DateField(verbose_name="Deadline")
    intrnl_project_labor = models.ForeignKey('InternalProjectLabor', models.DO_NOTHING, blank=True, null=True, verbose_name="Assigned To")

    class Meta:
        managed = False
        db_table = 'internal_project_task_list'
        verbose_name = 'Internal Task'
        verbose_name_plural = 'Internal Tasks'
        ordering = ['intrnl_task_deadline']

    def __str__(self):
        return f"{self.intrnl_task_id}"
    
    def save(self, *args, **kwargs):
        if not self.intrnl_task_id:
            self.intrnl_task_id = f"ITASK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if self.intrnl_task_status.lower() in ['completed', 'canceled']:
            return False
        return self.intrnl_task_deadline < timezone.now().date()
    
    @property
    def days_remaining(self):
        today = timezone.now().date()
        if self.intrnl_task_status.lower() in ['completed', 'canceled']:
            return 0
        
        delta = self.intrnl_task_deadline - today
        return delta.days
    
    @property
    def project_name(self):
        """Get the project name using SQL join"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ipr.project_name
                FROM internal_project_request ipr
                JOIN internal_project_details ipd ON ipr.project_request_id = ipd.project_request_id
                WHERE ipd.intrnl_project_id = %s
            """, [self.intrnl_project.intrnl_project_id if self.intrnl_project else None])
            result = cursor.fetchone()
            return result[0] if result else "Unknown Project"
    
    @property
    def assigned_employee(self):
        """Get the assigned employee name using SQL join"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT CONCAT(e.first_name, ' ', e.last_name) as employee_name
                FROM employees e
                JOIN internal_project_labor ipl ON e.employee_id = ipl.employee_id
                WHERE ipl.intrnl_project_labor_id = %s
            """, [self.intrnl_project_labor.intrnl_project_labor_id if self.intrnl_project_labor else None])
            result = cursor.fetchone()
            return result[0] if result else "Unassigned"

class ExternalProjectTaskList(models.Model):
    task_id = models.CharField(primary_key=True, max_length=255, verbose_name="Task ID")
    project = models.ForeignKey('ExternalProjectDetails', models.DO_NOTHING, blank=True, null=True, verbose_name="Project")
    task_description = models.TextField(blank=True, null=True, verbose_name="Description")
    task_status = models.CharField(max_length=50, verbose_name="Status")
    task_deadline = models.DateField(verbose_name="Deadline")
    project_labor = models.ForeignKey('ExternalProjectLabor', models.DO_NOTHING, blank=True, null=True, verbose_name="Assigned To")

    class Meta:
        managed = False
        db_table = 'external_project_task_list'
        verbose_name = 'External Task'
        verbose_name_plural = 'External Tasks'
        ordering = ['task_deadline']

    def __str__(self):
        return f"{self.task_id}"
    
    def save(self, *args, **kwargs):
        if not self.task_id:
            self.task_id = f"ETASK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if self.task_status.lower() in ['completed', 'canceled']:
            return False
        return self.task_deadline < timezone.now().date()
    
    @property
    def days_remaining(self):
        today = timezone.now().date()
        if self.task_status.lower() in ['completed', 'canceled']:
            return 0
        
        delta = self.task_deadline - today
        return delta.days
    
    @property
    def project_name(self):
        """Get the project name using SQL join"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT epr.ext_project_name
                FROM external_project_request epr
                JOIN external_project_details epd ON epr.ext_project_request_id = epd.ext_project_request_id
                WHERE epd.project_id = %s
            """, [self.project.project_id if self.project else None])
            result = cursor.fetchone()
            return result[0] if result else "Unknown Project"
    
    @property
    def assigned_employee(self):
        """Get the assigned employee name using SQL join"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT CONCAT(e.first_name, ' ', e.last_name) as employee_name
                FROM employees e
                JOIN external_project_labor epl ON e.employee_id = epl.employee_id
                WHERE epl.project_labor_id = %s
            """, [self.project_labor.project_labor_id if self.project_labor else None])
            result = cursor.fetchone()
            return result[0] if result else "Unassigned"

# These are just references to other models that are needed for ForeignKey relationships
class InternalProjectDetails(models.Model):
    intrnl_project_id = models.CharField(primary_key=True, max_length=255)
    project_request = models.ForeignKey('InternalProjectRequest', models.DO_NOTHING, blank=True, null=True)
    intrnl_project_status = models.TextField()

    class Meta:
        managed = False
        db_table = 'internal_project_details'
        
    def __str__(self):
        return self.intrnl_project_id

class InternalProjectLabor(models.Model):
    intrnl_project_labor_id = models.CharField(primary_key=True, max_length=255)
    intrnl_project = models.ForeignKey(InternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_labor'
        
    def __str__(self):
        return self.intrnl_project_labor_id

class InternalProjectRequest(models.Model):
    project_request_id = models.CharField(primary_key=True, max_length=255)
    project_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'internal_project_request'
        
    def __str__(self):
        return self.project_name

class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request = models.ForeignKey('ExternalProjectRequest', models.DO_NOTHING, blank=True, null=True)
    project_status = models.TextField()

    class Meta:
        managed = False
        db_table = 'external_project_details'
        
    def __str__(self):
        return self.project_id

class ExternalProjectLabor(models.Model):
    project_labor_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_labor'
        
    def __str__(self):
        return self.project_labor_id

class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'external_project_request'
        
    def __str__(self):
        return self.ext_project_name

# Helper functions to get valid project and labor IDs
def get_valid_internal_project_ids():
    """Get a list of valid internal project IDs with their names"""
    projects = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ipd.intrnl_project_id, ipr.project_name
            FROM internal_project_details ipd
            JOIN internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
            ORDER BY ipr.project_name
        """)
        for row in cursor.fetchall():
            projects.append((row[0], f"{row[0]} - {row[1]}"))
    return projects

def get_valid_external_project_ids():
    """Get a list of valid external project IDs with their names"""
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

def get_valid_internal_labor_ids():
    """Get a list of valid internal labor IDs with employee names"""
    labors = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ipl.intrnl_project_labor_id, CONCAT(e.first_name, ' ', e.last_name) as employee_name
            FROM internal_project_labor ipl
            JOIN employees e ON ipl.employee_id = e.employee_id
            ORDER BY employee_name
        """)
        for row in cursor.fetchall():
            labors.append((row[0], f"{row[0]} - {row[1]}"))
    return labors

def get_valid_external_labor_ids():
    """Get a list of valid external labor IDs with employee names"""
    labors = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT epl.project_labor_id, CONCAT(e.first_name, ' ', e.last_name) as employee_name
            FROM external_project_labor epl
            JOIN employees e ON epl.employee_id = e.employee_id
            ORDER BY employee_name
        """)
        for row in cursor.fetchall():
            labors.append((row[0], f"{row[0]} - {row[1]}"))
    return labors

def get_all_tasks_with_joins():
    """Get all tasks with related information using SQL joins"""
    internal_tasks = []
    external_tasks = []
    
    # Get internal tasks with joins
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    iptl.intrnl_task_id,
                    iptl.intrnl_project_id,
                    iptl.intrnl_task_description,
                    iptl.intrnl_task_status,
                    iptl.intrnl_task_deadline,
                    iptl.intrnl_project_labor_id,
                    ipr.project_name,
                    CONCAT(e.first_name, ' ', e.last_name) as employee_name
                FROM 
                    internal_project_task_list iptl
                LEFT JOIN 
                    internal_project_details ipd ON iptl.intrnl_project_id = ipd.intrnl_project_id
                LEFT JOIN 
                    internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
                LEFT JOIN 
                    internal_project_labor ipl ON iptl.intrnl_project_labor_id = ipl.intrnl_project_labor_id
                LEFT JOIN 
                    employees e ON ipl.employee_id = e.employee_id
            """)
            
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                task_dict = dict(zip(columns, row))
                
                # Convert date objects to strings
                if task_dict.get('intrnl_task_deadline'):
                    if isinstance(task_dict['intrnl_task_deadline'], datetime):
                        task_dict['intrnl_task_deadline'] = task_dict['intrnl_task_deadline'].date()
                
                internal_tasks.append(task_dict)
    except Exception as e:
        print(f"Error fetching internal tasks: {e}")
    
    # Get external tasks with joins
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    eptl.task_id,
                    eptl.project_id,
                    eptl.task_description,
                    eptl.task_status,
                    eptl.task_deadline,
                    eptl.project_labor_id,
                    epr.ext_project_name as project_name,
                    CONCAT(e.first_name, ' ', e.last_name) as employee_name
                FROM 
                    external_project_task_list eptl
                LEFT JOIN 
                    external_project_details epd ON eptl.project_id = epd.project_id
                LEFT JOIN 
                    external_project_request epr ON epd.ext_project_request_id = epr.ext_project_request_id
                LEFT JOIN 
                    external_project_labor epl ON eptl.project_labor_id = epl.project_labor_id
                LEFT JOIN 
                    employees e ON epl.employee_id = e.employee_id
            """)
            
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                task_dict = dict(zip(columns, row))
                
                # Convert date objects to strings
                if task_dict.get('task_deadline'):
                    if isinstance(task_dict['task_deadline'], datetime):
                        task_dict['task_deadline'] = task_dict['task_deadline'].date()
                
                external_tasks.append(task_dict)
    except Exception as e:
        print(f"Error fetching external tasks: {e}")
    
    return internal_tasks, external_tasks