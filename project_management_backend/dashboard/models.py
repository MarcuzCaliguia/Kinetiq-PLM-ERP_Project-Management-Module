from django.db import models
from django.utils import timezone
from django.db import connection


class ExternalProjectWarranty(models.Model):
    warranty_start_date = models.DateField()
    warranty_end_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'external_project_warranty'
        
class ExternalProjectRequest(models.Model):
    ext_project_request_id = models.CharField(primary_key=True, max_length=255)
    ext_project_name = models.CharField(max_length=50)
    
    class Meta:
        managed = False
        db_table = 'external_project_request'


class ExternalProjectDetails(models.Model):
    project_id = models.CharField(primary_key=True, max_length=255)
    ext_project_request = models.ForeignKey(ExternalProjectRequest, models.DO_NOTHING, blank=True, null=True)
    project_status = models.TextField()
    
    class Meta:
        managed = False
        db_table = 'external_project_details'


class ExternalProjectTracking(models.Model):
    project_tracking_id = models.CharField(primary_key=True, max_length=255)
    project = models.ForeignKey(ExternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    project_milestone = models.TextField()  # This field type is a guess.
    start_date = models.DateField()
    estimated_end_date = models.DateField()
    project_warranty = models.ForeignKey('ExternalProjectWarranty', models.DO_NOTHING, blank=True, null=True)
    project_issue = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'external_project_tracking'

class InternalProjectRequest(models.Model):
    project_request_id = models.CharField(primary_key=True, max_length=255)
    project_name = models.CharField(max_length=50)
    
    class Meta:
        managed = False
        db_table = 'internal_project_request'


class InternalProjectDetails(models.Model):
    intrnl_project_id = models.CharField(primary_key=True, max_length=255)
    project_request = models.ForeignKey(InternalProjectRequest, models.DO_NOTHING, blank=True, null=True)
    intrnl_project_status = models.TextField()
    
    class Meta:
        managed = False
        db_table = 'internal_project_details'


class InternalProjectLabor(models.Model):
    employee_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'internal_project_labor'


class InternalProjectTaskList(models.Model):
    intrnl_task_id = models.CharField(primary_key=True, max_length=255)
    intrnl_project = models.ForeignKey(InternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    intrnl_task_description = models.TextField(blank=True, null=True)
    intrnl_task_status = models.TextField()  # This is an enum field
    intrnl_task_deadline = models.DateField()
    intrnl_project_labor = models.ForeignKey(InternalProjectLabor, models.DO_NOTHING, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'internal_project_task_list'


class InternalProjectTracking(models.Model):
    intrnl_project_tracking_id = models.CharField(primary_key=True, max_length=255)
    intrnl_project = models.ForeignKey(InternalProjectDetails, models.DO_NOTHING, blank=True, null=True)
    intrnl_start_date = models.DateField()
    intrnl_estimated_end_date = models.DateField()
    intrnl_project_issue = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internal_project_tracking'

class DashboardService:
    @staticmethod
    def create_contractual_worker_request(data):
        """Create a new contractual worker request"""
        import logging
        import uuid
        from django.db import connection
        from django.utils import timezone
        
        logger = logging.getLogger(__name__)
        
        try:
            # Generate a unique request ID
            request_id = f"CWR-{uuid.uuid4().hex[:8].upper()}"
            
            # Extract data from the form
            job_title = data.get('job_title', '')
            job_description = data.get('job_description', '')
            required_position = data.get('required_position', '')
            employment_type = data.get('employment_type', '')
            dept_id = data.get('department', '')
            project_id = data.get('project_id', '')
            
            # Map the user-friendly employment type to the actual enum value
            # First, let's check what values are valid in the database
            valid_employment_types = []
            with connection.cursor() as cursor:
                try:
                    # This query gets the enum values for the employment_type column
                    cursor.execute("""
                        SELECT 
                            pg_enum.enumlabel
                        FROM 
                            pg_type 
                        JOIN 
                            pg_enum ON pg_enum.enumtypid = pg_type.oid
                        WHERE 
                            pg_type.typname = 'employment_type'
                        ORDER BY 
                            pg_enum.enumsortorder
                    """)
                    valid_employment_types = [row[0] for row in cursor.fetchall()]
                    logger.info(f"Valid employment types from DB: {valid_employment_types}")
                except Exception as e:
                    # If the query fails (e.g., not PostgreSQL or enum not found),
                    # use some common values as fallback
                    logger.warning(f"Could not retrieve enum values: {str(e)}")
                    valid_employment_types = ['fulltime', 'parttime', 'contractual']
            
            # Map the form value to a valid enum value
            mapped_employment_type = employment_type.lower()
            if mapped_employment_type == 'full-time':
                mapped_employment_type = 'fulltime'
            elif mapped_employment_type == 'part-time':
                mapped_employment_type = 'parttime'
            
            # Check if the mapped value is valid
            if mapped_employment_type not in valid_employment_types:
                # Try to find a close match
                if 'fulltime' in valid_employment_types and mapped_employment_type in ['full-time', 'full_time', 'full time']:
                    mapped_employment_type = 'fulltime'
                elif 'parttime' in valid_employment_types and mapped_employment_type in ['part-time', 'part_time', 'part time']:
                    mapped_employment_type = 'parttime'
                elif 'contractual' in valid_employment_types and mapped_employment_type in ['contract', 'contractual']:
                    mapped_employment_type = 'contractual'
                else:
                    # If no match, use the first valid value as default
                    if valid_employment_types:
                        mapped_employment_type = valid_employment_types[0]
                        logger.warning(f"Using default employment type: {mapped_employment_type}")
                    else:
                        raise ValueError(f"No valid employment type found for: {employment_type}")
            
            logger.info(f"Mapped employment type '{employment_type}' to '{mapped_employment_type}'")
            
            # Insert new request into database
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO contractual_worker_request 
                    (request_id, job_title, job_description, required_position, employment_type, dept_id, intrnl_project_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [
                    request_id, 
                    job_title, 
                    job_description, 
                    required_position, 
                    mapped_employment_type,  # Use the mapped value
                    dept_id if dept_id else None, 
                    project_id if project_id else None
                ])
            
            logger.info(f"Created new contractual worker request with ID: {request_id}")
            return {
                'success': True,
                'request_id': request_id,
                'message': 'Request created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating contractual worker request: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f"Error creating request: {str(e)}"
            }

    @staticmethod
    def create_contractual_worker_request(data):
        """Create a new contractual worker request"""
        import logging
        import uuid
        from django.db import connection
        from django.utils import timezone
        
        logger = logging.getLogger(__name__)
        
        try:
            # Generate a unique request ID
            request_id = f"CWR-{uuid.uuid4().hex[:8].upper()}"
            
            # Extract data from the form
            job_title = data.get('job_title', '')
            job_description = data.get('job_description', '')
            required_position = data.get('required_position', '')
            employment_type = data.get('employment_type', '')
            dept_id = data.get('department', '')
            project_id = data.get('project_id', '')
            
            # Insert new request into database
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO contractual_worker_request 
                    (request_id, job_title, job_description, required_position, employment_type, dept_id, intrnl_project_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [
                    request_id, 
                    job_title, 
                    job_description, 
                    required_position, 
                    employment_type, 
                    dept_id if dept_id else None, 
                    project_id if project_id else None
                ])
            
            logger.info(f"Created new contractual worker request with ID: {request_id}")
            return {
                'success': True,
                'request_id': request_id,
                'message': 'Request created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating contractual worker request: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f"Error creating request: {str(e)}"
            }

    @staticmethod
    def get_departments():
        """Get all departments for dropdown selection"""
        from django.db import connection
        
        departments = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT dept_id, dept_name FROM departments ORDER BY dept_name")
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    departments.append(dict(zip(columns, row)))
        except Exception as e:
            pass
        
        return departments

    @staticmethod
    def get_internal_projects():
        """Get active internal projects for dropdown selection"""
        from django.db import connection
        
        projects = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ipd.intrnl_project_id, 
                        ipr.project_name
                    FROM 
                        internal_project_details ipd
                    JOIN 
                        internal_project_request ipr ON ipd.project_request_id = ipr.project_request_id
                    WHERE 
                        ipd.intrnl_project_status IN ('in progress', 'ongoing', 'In Progress', 'Ongoing', 'active', 'Active')
                    ORDER BY 
                        ipr.project_name
                """)
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    projects.append(dict(zip(columns, row)))
        except Exception as e:
            pass
        
        return projects

    @staticmethod
    def get_task_status_values():
        """Get the actual enum values from the database"""
        with connection.cursor() as cursor:
            # For external tasks
            cursor.execute("SELECT DISTINCT task_status FROM external_project_task_list LIMIT 10")
            external_statuses = [row[0] for row in cursor.fetchall()]
            
            # For internal tasks
            cursor.execute("SELECT DISTINCT intrnl_task_status FROM internal_project_task_list LIMIT 10")
            internal_statuses = [row[0] for row in cursor.fetchall()]
            
            return {
                'external': external_statuses,
                'internal': internal_statuses
            }
    
    @staticmethod
    def get_overdue_tasks():
        """Get all overdue tasks from both internal and external projects using raw SQL"""
        today = timezone.now().date().isoformat()
        
        # Get the task statuses first
        status_values = DashboardService.get_task_status_values()
        
        # Use raw SQL to avoid enum conversion issues
        external_tasks_raw = []
        with connection.cursor() as cursor:
            # Query for external tasks
            cursor.execute("""
                SELECT 
                    t.task_id, 
                    t.task_description, 
                    t.task_deadline,
                    t.task_status,
                    l.employee_id,
                    e.first_name,
                    e.last_name,
                    p.project_id
                FROM 
                    external_project_task_list t
                LEFT JOIN 
                    external_project_labor l ON t.project_labor_id = l.project_labor_id
                LEFT JOIN 
                    employees e ON l.employee_id = e.employee_id
                LEFT JOIN
                    external_project_details p ON t.project_id = p.project_id
                WHERE 
                    t.task_deadline < %s
                ORDER BY
                    t.task_deadline ASC
            """, [today])
            
            columns = [col[0] for col in cursor.description]
            external_tasks_raw = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Process external tasks
        external_overdue = []
        for task in external_tasks_raw:
            # Only include tasks with appropriate status
            if 'task_status' in task and task['task_status'] in status_values['external']:
                # Check if the status indicates the task is not completed
                # You may need to adjust this logic based on your actual enum values
                if task['task_status'] != 'Completed' and task['task_status'] != 'completed':
                    days_overdue = (timezone.now().date() - task['task_deadline']).days
                    category = DashboardService._categorize_overdue_days(days_overdue)
                    
                    employee_name = "N/A"
                    if task.get('first_name') and task.get('last_name'):
                        employee_name = f"{task['first_name']} {task['last_name']}"
                    elif task.get('employee_id'):
                        employee_name = task['employee_id']
                    
                    external_overdue.append({
                        'task_id': task['task_id'],
                        'description': task['task_description'],
                        'deadline': task['task_deadline'],
                        'employee': employee_name,
                        'days_overdue': days_overdue,
                        'category': category,
                        'project_type': 'External',
                        'project_id': task.get('project_id', 'N/A')
                    })
        
        # Query for internal tasks
        internal_tasks_raw = []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    t.intrnl_task_id, 
                    t.intrnl_task_description, 
                    t.intrnl_task_deadline,
                    t.intrnl_task_status,
                    l.employee_id,
                    e.first_name,
                    e.last_name,
                    p.intrnl_project_id
                FROM 
                    internal_project_task_list t
                LEFT JOIN 
                    internal_project_labor l ON t.intrnl_project_labor_id = l.intrnl_project_labor_id
                LEFT JOIN 
                    employees e ON l.employee_id = e.employee_id
                LEFT JOIN
                    internal_project_details p ON t.intrnl_project_id = p.intrnl_project_id
                WHERE 
                    t.intrnl_task_deadline < %s
                ORDER BY
                    t.intrnl_task_deadline ASC
            """, [today])
            
            columns = [col[0] for col in cursor.description]
            internal_tasks_raw = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Process internal tasks
        internal_overdue = []
        for task in internal_tasks_raw:
            # Only include tasks with appropriate status
            if 'intrnl_task_status' in task and task['intrnl_task_status'] in status_values['internal']:
                # Check if the status indicates the task is not completed
                # You may need to adjust this logic based on your actual enum values
                if task['intrnl_task_status'] != 'Completed' and task['intrnl_task_status'] != 'completed':
                    days_overdue = (timezone.now().date() - task['intrnl_task_deadline']).days
                    category = DashboardService._categorize_overdue_days(days_overdue)
                    
                    employee_name = "N/A"
                    if task.get('first_name') and task.get('last_name'):
                        employee_name = f"{task['first_name']} {task['last_name']}"
                    elif task.get('employee_id'):
                        employee_name = task['employee_id']
                    
                    internal_overdue.append({
                        'task_id': task['intrnl_task_id'],
                        'description': task['intrnl_task_description'],
                        'deadline': task['intrnl_task_deadline'],
                        'employee': employee_name,
                        'days_overdue': days_overdue,
                        'category': category,
                        'project_type': 'Internal',
                        'project_id': task.get('intrnl_project_id', 'N/A')
                    })
        
        # Combine and sort by days_overdue (descending)
        all_overdue = external_overdue + internal_overdue
        all_overdue.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return all_overdue
    
    @staticmethod
    def _categorize_overdue_days(days):
        """Categorize overdue days into predefined buckets"""
        if days <= 10:
            return "10 Days"
        elif days <= 15:
            return "15 Days"
        elif days <= 25:
            return "25 Days"
        elif days <= 30:
            return "1 Month"
        elif days <= 60:
            return "2 Months"
        else:
            return "3+ Months"
    
    @staticmethod
    def get_today_tasks():
        """Get tasks that are due today or upcoming using raw SQL"""
        today = timezone.now().date().isoformat()
        
        # Get the task statuses first
        status_values = DashboardService.get_task_status_values()
        
        # Use raw SQL to avoid enum conversion issues
        external_tasks_raw = []
        with connection.cursor() as cursor:
            # Query for external tasks
            cursor.execute("""
                SELECT 
                    t.task_id, 
                    t.task_description, 
                    t.task_status,
                    l.employee_id,
                    e.first_name,
                    e.last_name,
                    p.project_id
                FROM 
                    external_project_task_list t
                LEFT JOIN 
                    external_project_labor l ON t.project_labor_id = l.project_labor_id
                LEFT JOIN 
                    employees e ON l.employee_id = e.employee_id
                LEFT JOIN
                    external_project_details p ON t.project_id = p.project_id
                WHERE 
                    t.task_deadline = %s
                ORDER BY
                    t.task_id ASC
            """, [today])
            
            columns = [col[0] for col in cursor.description]
            external_tasks_raw = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Process external tasks
        external_today = []
        for task in external_tasks_raw:
            # Only include tasks with appropriate status
            if 'task_status' in task and task['task_status'] in status_values['external']:
                # Check if the status indicates the task is not completed
                if task['task_status'] != 'Completed' and task['task_status'] != 'completed':
                    employee_name = "N/A"
                    if task.get('first_name') and task.get('last_name'):
                        employee_name = f"{task['first_name']} {task['last_name']}"
                    elif task.get('employee_id'):
                        employee_name = task['employee_id']
                    
                    external_today.append({
                        'task_id': task['task_id'],
                        'description': task['task_description'],
                        'important': DashboardService._is_task_important(task['task_description']),
                        'notes': '',  # You would need to add a notes field to your model
                        'links': '',  # You would need to add a links field to your model
                        'employee': employee_name,
                        'project_type': 'External',
                        'project_id': task.get('project_id', 'N/A')
                    })
        
        # Query for internal tasks
        internal_tasks_raw = []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    t.intrnl_task_id, 
                    t.intrnl_task_description, 
                    t.intrnl_task_status,
                    l.employee_id,
                    e.first_name,
                    e.last_name,
                    p.intrnl_project_id
                FROM 
                    internal_project_task_list t
                LEFT JOIN 
                    internal_project_labor l ON t.intrnl_project_labor_id = l.intrnl_project_labor_id
                LEFT JOIN 
                    employees e ON l.employee_id = e.employee_id
                LEFT JOIN
                    internal_project_details p ON t.intrnl_project_id = p.intrnl_project_id
                WHERE 
                    t.intrnl_task_deadline = %s
                ORDER BY
                    t.intrnl_task_id ASC
            """, [today])
            
            columns = [col[0] for col in cursor.description]
            internal_tasks_raw = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Process internal tasks
        internal_today = []
        for task in internal_tasks_raw:
            # Only include tasks with appropriate status
            if 'intrnl_task_status' in task and task['intrnl_task_status'] in status_values['internal']:
                # Check if the status indicates the task is not completed
                if task['intrnl_task_status'] != 'Completed' and task['intrnl_task_status'] != 'completed':
                    employee_name = "N/A"
                    if task.get('first_name') and task.get('last_name'):
                        employee_name = f"{task['first_name']} {task['last_name']}"
                    elif task.get('employee_id'):
                        employee_name = task['employee_id']
                    
                    internal_today.append({
                        'task_id': task['intrnl_task_id'],
                        'description': task['intrnl_task_description'],
                        'important': DashboardService._is_task_important(task['intrnl_task_description']),
                        'notes': '',  # You would need to add a notes field to your model
                        'links': '',  # You would need to add a links field to your model
                        'employee': employee_name,
                        'project_type': 'Internal',
                        'project_id': task.get('intrnl_project_id', 'N/A')
                    })
        
        # Combine and sort by importance
        all_today = external_today + internal_today
        all_today.sort(key=lambda x: x['important'], reverse=True)
        
        return all_today
    
    @staticmethod
    def _is_task_important(description):
        """Determine if a task is important based on keywords in the description"""
        important_keywords = ['urgent', 'priority', 'critical', 'important', 'asap', 'deadline']
        if description:
            description_lower = str(description).lower()
            return any(keyword in description_lower for keyword in important_keywords)
        return False
        
    @staticmethod
    def get_project_summary():
        """Get summary of all projects directly from ExternalProjectTracking and InternalProjectTracking models"""
        import logging
        logger = logging.getLogger(__name__)
        
        all_projects = []
        
        try:
            # Get external projects directly from the model
            external_projects = ExternalProjectTracking.objects.all()
            
            for ext_tracking in external_projects:
                try:
                    project_id = "N/A"
                    if ext_tracking.project:
                        project_id = ext_tracking.project.project_id
                    
                    all_projects.append({
                        'tracking_id': ext_tracking.project_tracking_id,
                        'project_id': project_id,
                        'start_date': ext_tracking.start_date,
                        'end_date': ext_tracking.estimated_end_date,
                        'project_type': 'External'
                    })
                except Exception as e:
                    logger.error(f"Error processing external project {ext_tracking.project_tracking_id}: {str(e)}")
            
            # Get internal projects directly from the model
            internal_projects = InternalProjectTracking.objects.all()
            
            for int_tracking in internal_projects:
                try:
                    project_id = "N/A"
                    if int_tracking.intrnl_project:
                        project_id = int_tracking.intrnl_project.intrnl_project_id
                    
                    all_projects.append({
                        'tracking_id': int_tracking.intrnl_project_tracking_id,
                        'project_id': project_id,
                        'start_date': int_tracking.intrnl_start_date,
                        'end_date': int_tracking.intrnl_estimated_end_date,
                        'project_type': 'Internal'
                    })
                except Exception as e:
                    logger.error(f"Error processing internal project {int_tracking.intrnl_project_tracking_id}: {str(e)}")
            
            # Sort by end date
            all_projects.sort(key=lambda x: x['end_date'])
            logger.info(f"Returning {len(all_projects)} projects")
            
        except Exception as e:
            logger.error(f"Error in get_project_summary: {str(e)}", exc_info=True)
            all_projects = []
        
        return all_projects
    @staticmethod
    def _calculate_progress(start_date, end_date, today):
        """Calculate project progress as a percentage"""
        if today <= start_date:
            return 0
        
        if today >= end_date:
            return 100
        
        total_days = (end_date - start_date).days
        if total_days <= 0:
            return 100
            
        days_passed = (today - start_date).days
        progress = (days_passed / total_days) * 100
        
        return min(round(progress), 100)
    
    @staticmethod
    def _determine_project_status(project_status, start_date, end_date, today):
        """Determine project status based on dates and current status"""
        # Convert project_status to string and lowercase for comparison
        project_status_str = str(project_status).lower()
        
        if 'complete' in project_status_str:
            return 'Completed'
        
        if today < start_date:
            return 'Not Started'
        
        if today > end_date:
            return 'Delayed'
        
        # Check if project is at risk (less than 10% of time remaining but less than 90% complete)
        total_days = (end_date - start_date).days
        if total_days > 0:
            days_remaining = (end_date - today).days
            time_remaining_percent = (days_remaining / total_days) * 100
            
            if time_remaining_percent < 10:
                progress = DashboardService._calculate_progress(start_date, end_date, today)
                if progress < 90:
                    return 'At Risk'
        
        return 'Ongoing'