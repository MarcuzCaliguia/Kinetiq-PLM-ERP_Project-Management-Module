from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from project_reports.models import ReportMonitoring
from django.db import connection
from datetime import date
import json

class ReportAPITests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create a test client
        self.client = APIClient()
        
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
            cursor.execute("DELETE FROM project_management.report_monitoring WHERE report_title = 'API Test Report'")
            cursor.execute("DELETE FROM project_management.external_project_details WHERE project_id = 'TEST-PRJ-001'")
    
    def test_report_list_api(self):
        """Test the report list API endpoint"""
        # Login
        self.client.force_authenticate(user=self.user)
        
        # Get the response
        response = self.client.get('/reports/api/reports/')
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the data contains our test report
        data = response.json()
        self.assertIn('results', data)  # DRF pagination
        
        # Find our test report in the results
        test_report = None
        for report in data['results']:
            if report['report_monitoring_id'] == 'TEST-RPT-001':
                test_report = report
                break
        
        self.assertIsNotNone(test_report)
        self.assertEqual(test_report['report_title'], 'Test Report')
    
    def test_report_detail_api(self):
        """Test the report detail API endpoint"""
        # Login
        self.client.force_authenticate(user=self.user)
        
        # Get the response
        response = self.client.get(f'/reports/api/reports/TEST-RPT-001/')
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check the report data
        data = response.json()
        self.assertEqual(data['report_monitoring_id'], 'TEST-RPT-001')
        self.assertEqual(data['report_title'], 'Test Report')
        self.assertEqual(data['project_id'], 'TEST-PRJ-001')
    
    def test_create_report_api(self):
        """Test creating a report via the API"""
        # Login
        self.client.force_authenticate(user=self.user)
        
        # Prepare the data
        post_data = {
            'project_id': 'TEST-PRJ-001',
            'report_type': 'Progress Report',
            'report_title': 'API Test Report',
            'received_from': 'Project Management',
            'date_created': date.today().strftime('%Y-%m-%d'),
            'assigned_to': 'Project Management',
            'description': 'This is a test report created via API'
        }
        
        # Send the request
        response = self.client.post('/reports/api/reports/', post_data, format='json')
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 201)
        
        # Check the report data
        data = response.json()
        self.assertIn('report_monitoring_id', data)
        self.assertEqual(data['report_title'], 'API Test Report')
        
        # Verify the report was created in the database
        report = ReportMonitoring.objects.get(report_monitoring_id=data['report_monitoring_id'])
        self.assertEqual(report.report_title, 'API Test Report')