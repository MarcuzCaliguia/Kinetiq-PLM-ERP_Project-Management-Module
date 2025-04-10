from django.db import models
from django.utils import timezone

class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request = models.ForeignKey('ExternalProjectRequest', models.DO_NOTHING, blank=True, null=True)
    project_status = models.TextField()

    class Meta:
        managed = False
        db_table = 'external_project_details'


class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50)
    ext_project_description = models.TextField(blank=True, null=True)
    approval_id = models.CharField(max_length=255, blank=True, null=True)
    item_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_request'


class ExternalProjectTracking(models.Model):
    project_tracking_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    project_milestone = models.TextField()
    start_date = models.DateField()
    estimated_end_date = models.DateField()
    project_warranty = models.ForeignKey('ExternalProjectWarranty', models.DO_NOTHING, blank=True, null=True)
    project_issue = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_tracking'


class ExternalProjectWarranty(models.Model):
    project_warranty_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    warranty_coverage_yr = models.IntegerField()
    warranty_start_date = models.DateField()
    warranty_end_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'external_project_warranty'


class InternalProjectDetails(models.Model):
    intrnl_project_id = models.CharField(primary_key=True, max_length=255)
    project_request = models.ForeignKey('InternalProjectRequest', models.DO_NOTHING, blank=True, null=True)
    intrnl_project_status = models.TextField()

    class Meta:
        managed = False
        db_table = 'internal_project_details'


class InternalProjectRequest(models.Model):
    project_request_id = models.CharField(primary_key=True, max_length=255)
    project_name = models.CharField(max_length=50)
    project_description = models.TextField(blank=True, null=True)
    request_date = models.DateField()
    request_valid_date = models.DateField()
    request_starting_date = models.DateField()
    approval_id = models.CharField(max_length=255, blank=True, null=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)
    dept_id = models.CharField(max_length=255, blank=True, null=True)
    project_type = models.TextField()

    class Meta:
        managed = False
        db_table = 'internal_project_request'


class InternalProjectTracking(models.Model):
    intrnl_project_tracking_id = models.CharField(primary_key=True, max_length=255)
    intrnl_project = models.ForeignKey(InternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    intrnl_start_date = models.DateField()
    intrnl_estimated_end_date = models.DateField()
    intrnl_project_issue = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_tracking'


class ProjectPlanService:
    """Service class for project planning operations"""
    
    @staticmethod
    def get_all_projects():
        """Get all projects with their tracking information"""
        from django.db import connection
        
        projects = []
        
        try:
            # Get external projects without relying on JOINs for names
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        project_tracking_id,
                        project_id,
                        project_milestone,
                        start_date,
                        estimated_end_date,
                        project_warranty_id,
                        project_issue
                    FROM 
                        project_management.external_project_tracking
                """)
                
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    project_dict = dict(zip(columns, row))
                    # Add fields that would normally come from JOINs
                    project_dict['project_name'] = f"External Project {project_dict['project_tracking_id'][-6:]}"
                    project_dict['project_status'] = 'Active'
                    project_dict['project_type'] = 'External'
                    
                    # Get warranty info if available
                    if project_dict.get('project_warranty_id'):
                        try:
                            with connection.cursor() as warranty_cursor:
                                warranty_cursor.execute("""
                                    SELECT warranty_coverage_yr
                                    FROM project_management.external_project_warranty
                                    WHERE project_warranty_id = %s
                                """, [project_dict['project_warranty_id']])
                                
                                warranty_result = warranty_cursor.fetchone()
                                if warranty_result:
                                    project_dict['warranty_coverage_yr'] = warranty_result[0]
                                else:
                                    project_dict['warranty_coverage_yr'] = None
                        except:
                            project_dict['warranty_coverage_yr'] = None
                    else:
                        project_dict['warranty_coverage_yr'] = None
                    
                    projects.append(project_dict)
            
            # Get internal projects without relying on JOINs for names
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        intrnl_project_tracking_id,
                        intrnl_project_id,
                        intrnl_start_date,
                        intrnl_estimated_end_date,
                        intrnl_project_issue
                    FROM 
                        project_management.internal_project_tracking
                """)
                
                for row in cursor.fetchall():
                    project_dict = {
                        'project_tracking_id': row[0],
                        'project_id': row[1],
                        'start_date': row[2],
                        'estimated_end_date': row[3],
                        'project_issue': row[4],
                        'project_name': f"Internal Project {row[0][-6:]}",
                        'project_status': 'Active',
                        'project_milestone': 'N/A',
                        'warranty_coverage_yr': None,
                        'project_type': 'Internal'
                    }
                    
                    projects.append(project_dict)
        
        except Exception as e:
            import traceback
            print(f"Error retrieving projects: {str(e)}")
            print(traceback.format_exc())
            projects = []
            
        return projects

    @staticmethod
    def get_project_requests():
        """Get all project requests for dropdown selection"""
        from django.db import connection
        
        requests = {
            'external': [],
            'internal': []
        }
        
        try:
            # Get external project requests
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ext_project_request_id AS request_id,
                        ext_project_name AS project_name,
                        'External' AS request_type
                    FROM 
                        external_project_request
                    ORDER BY 
                        ext_project_name
                """)
                
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    request_dict = dict(zip(columns, row))
                    requests['external'].append(request_dict)
            
            # Get internal project requests
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        project_request_id AS request_id,
                        project_name,
                        'Internal' AS request_type
                    FROM 
                        internal_project_request
                    ORDER BY 
                        project_name
                """)
                
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    request_dict = dict(zip(columns, row))
                    requests['internal'].append(request_dict)
        
        except Exception as e:
            print(f"Error retrieving project requests: {str(e)}")
            requests = {'external': [], 'internal': []}
            
        return requests
    
    @staticmethod
    def create_project_plan(data):
        """Create a new project plan"""
        import uuid
        from django.db import connection
        
        try:
            project_type = data.get('project_type', 'External')
            project_request_id = data.get('project_request_id')
            project_name = data.get('project_name')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            progress = data.get('progress', 'Not Started')
            project_issue = data.get('project_issue', '')
            
            if project_type == 'External':
                # Create external project plan
                return ProjectPlanService._create_external_project_plan(
                    project_request_id, project_name, start_date, end_date, 
                    progress, project_issue, data.get('warranty_coverage_yr', 1)
                )
            else:
                # Create internal project plan
                return ProjectPlanService._create_internal_project_plan(
                    project_request_id, project_name, start_date, end_date, 
                    progress, project_issue
                )
                
        except Exception as e:
            print(f"Error creating project plan: {str(e)}")
            return {
                'success': False,
                'message': f"Error creating project plan: {str(e)}"
            }
    @staticmethod
    def _create_external_project_plan(project_request_id, project_name, start_date, end_date, progress, project_issue, warranty_coverage_yr):
        """Create an external project plan with warranty"""
        import uuid
        from django.db import connection
        
        # Generate unique IDs
        project_tracking_id = f"PT-{uuid.uuid4().hex[:8].upper()}"
        project_warranty_id = f"PW-{uuid.uuid4().hex[:8].upper()}"
        
        # Get project_id from request_id if available
        project_id = None
        
        if project_request_id:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT project_id 
                    FROM project_management.external_project_details 
                    WHERE ext_project_request_id = %s
                """, [project_request_id])
                
                result = cursor.fetchone()
                if result:
                    project_id = result[0]
        
        # Validate and normalize progress value
        valid_milestones = ['planning', 'awaiting_approval', 'manufacturing', 'deployment', 'installation', 'completed']
        progress = progress.lower().replace(' ', '_')
        if progress not in valid_milestones:
            progress = 'planning'  # Default to planning if invalid
        
        # Insert warranty record
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO project_management.external_project_warranty
                (project_warranty_id, project_id, warranty_coverage_yr, warranty_start_date, warranty_end_date)
                VALUES (%s, %s, %s, %s, %s)
            """, [
                project_warranty_id,
                project_id,
                warranty_coverage_yr,
                start_date,
                end_date
            ])
        
        # Insert tracking record
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO project_management.external_project_tracking
                (project_tracking_id, project_id, project_milestone, start_date, estimated_end_date, project_warranty_id, project_issue)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                project_tracking_id,
                project_id,
                progress,
                start_date,
                end_date,
                project_warranty_id,
                project_issue
            ])
        
        return {
            'success': True,
            'tracking_id': project_tracking_id,
            'warranty_id': project_warranty_id,
            'message': 'External project plan created successfully'
        }

    @staticmethod
    def _update_external_project_plan(tracking_id, warranty_coverage_yr, start_date, end_date, progress, project_issue):
        """Update an external project plan"""
        from django.db import connection
        
        # Get warranty_id
        warranty_id = None
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT project_warranty_id 
                FROM project_management.external_project_tracking 
                WHERE project_tracking_id = %s
            """, [tracking_id])
            
            result = cursor.fetchone()
            if result:
                warranty_id = result[0]
        
        if not warranty_id:
            return {
                'success': False,
                'message': 'Project tracking record not found'
            }
        
        # Validate and normalize progress value
        valid_milestones = ['planning', 'awaiting_approval', 'manufacturing', 'deployment', 'installation', 'completed']
        progress = progress.lower().replace(' ', '_')
        if progress not in valid_milestones:
            progress = 'planning'  # Default to planning if invalid
        
        # Update warranty record
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE project_management.external_project_warranty
                SET warranty_coverage_yr = %s, 
                    warranty_start_date = %s, 
                    warranty_end_date = %s
                WHERE project_warranty_id = %s
            """, [
                warranty_coverage_yr,
                start_date,
                end_date,
                warranty_id
            ])
        
        # Update tracking record
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE project_management.external_project_tracking
                SET project_milestone = %s, 
                    start_date = %s, 
                    estimated_end_date = %s,
                    project_issue = %s
                WHERE project_tracking_id = %s
            """, [
                progress,
                start_date,
                end_date,
                project_issue,
                tracking_id
            ])
        
        return {
            'success': True,
            'message': 'External project plan updated successfully'
        }