from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from project_reports.models import ReportMonitoring
from django.db import connection
from datetime import date

class ReportViewsTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Add permissions
        permission = Permission.objects.get(codename='add_reportmonitoring')
        self.user.user_permissions.add(permission)
        
        # Create a test client
        self.client = Client()
        
        # Create a test project in the database
        with connection.cursor() as cursor:
            # Create a test external project
            cursor.execute("""
                INSERT INTO project_management.external_project_details(
                    project_id, ext_project_request_id, project_status
                ) VALUES (%s, %s, %s)
            """, ['TEST-PRJ-001', 'TEST-REQ-001', 'Active'])
            
            # Create a test report
            cursor.execute("""
                INSERT INTO project_management.report_monitoring(
                    report_monitoring_id, project_id, report_type, report_title, 
                    received_from, date_created, assigned_to, description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING report_monitoring_id
            """, [
                'TEST-RPT-001', 'TEST-PRJ-001', 'Information', 'Test Report', 
                'Project Management', date.today(), 'Project Management', 'Test description'
            ])
    
    def tearDown(self):
        # Clean up test data
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM project_management.report_monitoring WHERE report_monitoring_id = 'TEST-RPT-001'")
            cursor.execute("DELETE FROM project_management.external_project_details WHERE project_id = 'TEST-PRJ-001'")
    
    def test_report_list_view(self):
        """Test the report list view"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        
        # Get the response
        response = self.client.get(reverse('project_reports:report_list'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the report is in the context
        self.assertIn('reports', response.context)
        self.assertGreaterEqual(len(response.context['reports']), 1)
        
        # Check that our test report is in the list
        report_ids = [report.report_monitoring_id for report in response.context['reports']]
        self.assertIn('TEST-RPT-001', report_ids)
    
    def test_report_detail_view(self):
        """Test the report detail view"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        
        # Get the response
        response = self.client.get(reverse('project_reports:report_detail', args=['TEST-RPT-001']))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the report is in the context
        self.assertIn('report', response.context)
        self.assertEqual(response.context['report'].report_monitoring_id, 'TEST-RPT-001')
        self.assertEqual(response.context['report'].report_title, 'Test Report')
    
    def test_create_report_view(self):
        """Test the create report view"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        
        # Get the form page
        response = self.client.get(reverse('project_reports:report_create'))
        self.assertEqual(response.status_code, 200)
        
        # Submit the form
        post_data = {
            'project_id': 'TEST-PRJ-001',
            'intrnl_project_id': '',
            'report_type': 'Progress Report',
            'report_title': 'New Test Report',
            'received_from': 'Project Management',
            'date_created': date.today().strftime('%Y-%m-%d'),
            'assigned_to': 'Project Management',
            'description': 'This is a new test report'
        }
        
        response = self.client.post(reverse('project_reports:report_create'), post_data, follow=True)
        
        # Check that the report was created and we were redirected to the list
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project_reports/report_list.html')
        
        # Check for success message
        messages = list(response.context['messages'])
        self.assertGreaterEqual(len(messages), 1)
        self.assertIn('created successfully', str(messages[0]))
        
        # Clean up the new report
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM project_management.report_monitoring WHERE report_title = 'New Test Report'")
    
    def test_update_report_view(self):
        """Test the update report view"""
        # Add change permission
        permission = Permission.objects.get(codename='change_reportmonitoring')
        self.user.user_permissions.add(permission)
        
        # Login
        self.client.login(username='testuser', password='testpassword')
        
        # Get the form page
        response = self.client.get(reverse('project_reports:report_update', args=['TEST-RPT-001']))
        self.assertEqual(response.status_code, 200)
        
        # Submit the form with updated data
        post_data = {
            'project_id': 'TEST-PRJ-001',
            'intrnl_project_id': '',
            'report_type': 'Information',
            'report_title': 'Updated Test Report',
            'received_from': 'Project Management',
            'date_created': date.today().strftime('%Y-%m-%d'),
            'assigned_to': 'Project Management',
            'description': 'This is an updated test report'
        }
        
        response = self.client.post(
            reverse('project_reports:report_update', args=['TEST-RPT-001']), 
            post_data, 
            follow=True
        )
        
        # Check that the report was updated and we were redirected to the detail view
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project_reports/report_detail.html')
        
        # Check that the report was actually updated
        updated_report = response.context['report']
        self.assertEqual(updated_report.report_title, 'Updated Test Report')
        self.assertEqual(updated_report.description, 'This is an updated test report')