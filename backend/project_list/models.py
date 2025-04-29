from django.db import models

class ProjectStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    ONGOING = 'ongoing', 'Ongoing'
    COMPLETED = 'completed', 'Completed'

class ProjectMilestone(models.TextChoices):
    PLANNING = 'planning', 'Planning'
    DESIGN = 'design', 'Design'
    IMPLEMENTATION = 'implementation', 'Implementation'
    TESTING = 'testing', 'Testing'
    DEPLOYMENT = 'deployment', 'Deployment'
    MAINTENANCE = 'maintenance', 'Maintenance'

class WarrantyStatus(models.TextChoices):
    NOT_STARTED = 'not started', 'Not Started'
    ACTIVE = 'active', 'Active'
    EXPIRED = 'expired', 'Expired'

class InternalProjectStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    ONGOING = 'ongoing', 'Ongoing'
    COMPLETED = 'completed', 'Completed'

class InternalProjectType(models.TextChoices):
    MAINTENANCE = 'maintenance', 'Maintenance'
    UPGRADE = 'upgrade', 'Upgrade'
    EXPANSION = 'expansion', 'Expansion'
    RESEARCH = 'research', 'Research'
    OTHER = 'other', 'Other'

class TaskStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    DELAYED = 'delayed', 'Delayed'
    CANCELLED = 'cancelled', 'Cancelled'

class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(max_length=255, primary_key=True)
    ext_project_name = models.CharField(max_length=50, null=True)
    ext_project_description = models.TextField(null=True)
    approval_id = models.CharField(max_length=255, null=True)
    item_id = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'project_management.external_project_request'
        managed = False

class ExternalProjectDetails(models.Model):
    project_id = models.CharField(max_length=255, primary_key=True)
    ext_project_request_id = models.ForeignKey(
        ExternalProjectRequest,
        on_delete=models.CASCADE,
        db_column='ext_project_request_id',
        null=True,
        related_name='project_details'
    )
    project_status = models.CharField(max_length=20, choices=ProjectStatus.choices)
    project_milestone = models.CharField(max_length=20, choices=ProjectMilestone.choices, null=True)
    start_date = models.DateField(null=True)
    estimated_end_date = models.DateField(null=True)
    warranty_coverage_yr = models.IntegerField(null=True)
    warranty_start_date = models.DateField(null=True)
    warranty_end_date = models.DateField(null=True)
    project_issues = models.TextField(null=True)
    warranty_status = models.CharField(max_length=20, choices=WarrantyStatus.choices, null=True)

    class Meta:
        db_table = 'project_management.external_project_details'
        managed = False

class ProjectLabor(models.Model):
    project_labor_id = models.CharField(max_length=255, primary_key=True)
    project_id = models.CharField(max_length=255, null=True)
    job_role_needed = models.CharField(max_length=255, null=True)
    employee_id = models.CharField(max_length=255, null=True)
    intrnl_project_id = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'project_management.project_labor'
        managed = False

class ExternalProjectEquipments(models.Model):
    project_equipment_list_id = models.CharField(max_length=255, primary_key=True)
    project_id = models.CharField(max_length=255, null=True)
    project_equipment_id = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'project_management.external_project_equipments'
        managed = False

class InternalProjectRequest(models.Model):
    project_request_id = models.CharField(max_length=255, primary_key=True)
    project_name = models.CharField(max_length=50)
    request_date = models.DateField()
    employee_id = models.CharField(max_length=255, null=True)
    dept_id = models.CharField(max_length=255, null=True)
    reason_for_request = models.TextField(null=True)
    materials_needed = models.TextField(null=True)
    equipments_needed = models.TextField(null=True)
    project_type = models.CharField(max_length=20, choices=InternalProjectType.choices, null=True)

    class Meta:
        db_table = 'project_management.internal_project_request'
        managed = False

class InternalProjectDetails(models.Model):
    intrnl_project_id = models.CharField(max_length=255, primary_key=True)
    project_request_id = models.CharField(max_length=255, null=True)
    intrnl_project_status = models.CharField(max_length=20, choices=InternalProjectStatus.choices)
    approval_id = models.CharField(max_length=255, null=True)
    start_date = models.DateField(null=True)
    estimated_end_date = models.DateField(null=True)
    project_issues = models.TextField(null=True)

    class Meta:
        db_table = 'project_management.internal_project_details'
        managed = False

class ProjectCosts(models.Model):
    project_resources_id = models.CharField(max_length=255, primary_key=True)
    project_id = models.CharField(max_length=255, null=True)
    bom_id = models.CharField(max_length=255, null=True)
    budget_approvals_id = models.CharField(max_length=255, null=True)
    intrnl_project_id = models.CharField(max_length=255, null=True)
    outside_labor_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    utility_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    outsourced_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    overall_project_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = 'project_management.project_costs'
        managed = False

class ProjectTasks(models.Model):
    task_id = models.CharField(max_length=255, primary_key=True)
    project_id = models.CharField(max_length=255, null=True)
    task_description = models.TextField(null=True)
    task_status = models.CharField(max_length=20, choices=TaskStatus.choices)
    task_deadline = models.DateField()
    project_labor_id = models.CharField(max_length=255, null=True)
    intrnl_project_id = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'project_management.project_tasks'
        managed = False