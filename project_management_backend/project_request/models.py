from django.db import models

class InternalProjectRequest(models.Model):
    project_request_id = models.CharField(max_length=255, primary_key=True)
    # Add other fields as needed
    
    class Meta:
        db_table = 'project_management.internal_project_request'
    
    def __str__(self):
        return f"Request {self.project_request_id}"

class InternalProjectDetails(models.Model):
    # Custom choices for the project status enum
    class InternalProjectStatus(models.TextChoices):
        # Replace these with your actual enum values
        PLANNING = 'PLANNING', 'Planning'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        ON_HOLD = 'ON_HOLD', 'On Hold'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    intrnl_project_id = models.CharField(max_length=255, primary_key=True)
    project_request_id = models.ForeignKey(
        InternalProjectRequest,
        on_delete=models.CASCADE,
        db_column='project_request_id',
        to_field='project_request_id',
        related_name='project_details',
        blank=True,
        null=True
    )
    intrnl_project_status = models.CharField(
        max_length=50,
        choices=InternalProjectStatus.choices
    )
    
    class Meta:
        db_table = 'project_management.internal_project_details'
    
    def __str__(self):
        return f"Project {self.intrnl_project_id}"

class InternalProjectLabor(models.Model):
    intrnl_project_labor_id = models.CharField(max_length=255, primary_key=True)
    # Add other fields as needed
    
    class Meta:
        db_table = 'project_management.internal_project_labor'
    
    def __str__(self):
        return f"Labor {self.intrnl_project_labor_id}"

class InternalProjectTaskList(models.Model):
    # Custom choices for the task status enum
    class InternalTaskStatus(models.TextChoices):
        # Replace these with your actual enum values
        PENDING = 'PENDING', 'Pending'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        OVERDUE = 'OVERDUE', 'Overdue'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    intrnl_task_id = models.CharField(max_length=255, primary_key=True)
    intrnl_project_id = models.ForeignKey(
        InternalProjectDetails,
        on_delete=models.CASCADE,
        db_column='intrnl_project_id',
        to_field='intrnl_project_id',
        related_name='tasks'
    )
    intrnl_task_description = models.TextField(blank=True, null=True)
    intrnl_task_status = models.CharField(
        max_length=50,
        choices=InternalTaskStatus.choices
    )
    intrnl_task_deadline = models.DateField()
    intrnl_project_labor_id = models.ForeignKey(
        InternalProjectLabor,
        on_delete=models.CASCADE,
        db_column='intrnl_project_labor_id',
        to_field='intrnl_project_labor_id',
        related_name='assigned_tasks',
        blank=True,
        null=True
    )
    
    class Meta:
        db_table = 'project_management.internal_project_task_list'
    
    def __str__(self):
        return f"Task {self.intrnl_task_id}"