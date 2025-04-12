from django.db import models

class TaskStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'

class InternalProjectTask(models.Model):
    intrnl_task_id = models.CharField(max_length=255, primary_key=True)
    intrnl_project_id = models.CharField(max_length=255)
    intrnl_task_description = models.TextField(null=True, blank=True)
    intrnl_task_status = models.CharField(max_length=20, choices=TaskStatus.choices)
    intrnl_task_deadline = models.DateField()
    intrnl_project_labor_id = models.CharField(max_length=255)

    class Meta:
        db_table = 'internal_project_task_list'
        managed = False

    def __str__(self):
        return self.intrnl_task_id

class ExternalProjectTask(models.Model):
    task_id = models.CharField(max_length=255, primary_key=True)
    project_id = models.CharField(max_length=255)
    task_description = models.TextField(null=True, blank=True)
    task_status = models.CharField(max_length=20, choices=TaskStatus.choices)
    task_deadline = models.DateField()
    project_labor_id = models.CharField(max_length=255)

    class Meta:
        db_table = 'external_project_task_list'
        managed = False

    def __str__(self):
        return self.task_id