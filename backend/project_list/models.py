from django.db import models


from django.db import models

class ProjectStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    ONGOING = 'ongoing', 'Ongoing'
    COMPLETED = 'completed', 'Completed'

class InternalProjectStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    ONGOING = 'ongoing', 'Ongoing'
    COMPLETED = 'completed', 'Completed'

class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(max_length=255, primary_key=True)
    ext_project_name = models.CharField(max_length=50, null=True)
    ext_project_description = models.TextField(null=True)
    approval_id = models.CharField(max_length=255, null=True)
    item_id = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'external_project_request'
        managed = False

class ExternalProjectDetails(models.Model):
    project_id = models.CharField(max_length=255, primary_key=True)
    ext_project_request_id = models.ForeignKey(
        ExternalProjectRequest,
        on_delete=models.CASCADE,
        db_column='ext_project_request_id',
        null=True
    )
    project_status = models.CharField(max_length=20, choices=ProjectStatus.choices)

    class Meta:
        db_table = 'external_project_details'
        managed = False

class ExternalProjectLabor(models.Model):
    project_labor_id = models.CharField(max_length=255, primary_key=True)
    project_id = models.ForeignKey(
        ExternalProjectDetails,
        on_delete=models.CASCADE,
        db_column='project_id',
        null=True
    )
    job_role_needed = models.CharField(max_length=255, null=True)
    employee_id = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'external_project_labor'
        managed = False

class ExternalProjectEquipments(models.Model):
    project_equipment_list_id = models.CharField(max_length=255, primary_key=True)
    project_id = models.ForeignKey(
        ExternalProjectDetails,
        on_delete=models.CASCADE,
        db_column='project_id',
        null=True
    )
    project_equipment_id = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'external_project_equipments'
        managed = False

class ExternalProjectWarranty(models.Model):
    project_warranty_id = models.CharField(max_length=255, primary_key=True)
    project_id = models.ForeignKey(
        ExternalProjectDetails,
        on_delete=models.CASCADE,
        db_column='project_id',
        null=True
    )
    warranty_coverage_yr = models.IntegerField()
    warranty_start_date = models.DateField()
    warranty_end_date = models.DateField()

    class Meta:
        db_table = 'external_project_warranty'
        managed = False

class InternalProjectRequest(models.Model):
    project_request_id = models.CharField(max_length=255, primary_key=True)
    project_name = models.CharField(max_length=50)
    project_description = models.TextField(null=True)
    request_date = models.DateField()
    target_starting_date = models.DateField()
    employee_id = models.CharField(max_length=255, null=True)
    dept_id = models.CharField(max_length=255, null=True)
    project_budget_request = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    project_budget_description = models.TextField(null=True)

    class Meta:
        db_table = 'internal_project_request'
        managed = False

class InternalProjectDetails(models.Model):
    intrnl_project_id = models.CharField(max_length=255, primary_key=True)
    project_request_id = models.ForeignKey(
        InternalProjectRequest,
        on_delete=models.CASCADE,
        db_column='project_request_id',
        null=True
    )
    intrnl_project_status = models.CharField(max_length=20, choices=InternalProjectStatus.choices)
    approval_id = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'internal_project_details'
        managed = False