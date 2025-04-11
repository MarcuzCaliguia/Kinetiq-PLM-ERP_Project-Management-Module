from django.test import TestCase
from project_reports.models import ReportMonitoring
from django.db import connection
from datetime import date

class ReportMonitoringModelTests(TestCase):
    def setUp(self):
        # Create a test project in the database
        with connection.cursor() as cursor:
            # Create a test external project
            cursor.execute("""
                INSERT INTO project_management.external_project_details(
                    project_id, ext_project_request_id, project_status
                ) VALUES (%s, %s, %s)
            """, ['TEST-PRJ-001', 'TEST-REQ-001', 'Active'])
            
            # Create a test internal project
            cursor.execute("""
                INSERT INTO project_management.internal_project_details(
                    intrnl_project_id, project_request_id, intrnl_project_status, approval_id
                ) VALUES (%s, %s, %s, %s)
            """, ['TEST-INT-001', 'TEST-REQ-002', 'Active', None])
    
    def tearDown(self):
        # Clean up test data
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM project_management.report_monitoring WHERE project_id = 'TEST-PRJ-001' OR intrnl_project_id = 'TEST-INT-001'")
            cursor.execute("DELETE FROM project_management.external_project_details WHERE project_id = 'TEST-PRJ-001'")
            cursor.execute("DELETE FROM project_management.internal_project_details WHERE intrnl_project_id = 'TEST-INT-001'")
    
    def test_create_report_with_external_project(self):
        """Test creating a report with an external project"""
        report_id = ReportMonitoring.create_report(
            project_id='TEST-PRJ-001',
            intrnl_project_id=None,
            report_type='Information',
            report_title='Test Report',
            received_from='Project Management',
            date_created=date.today(),
            assigned_to='Project Management',
            description='This is a test report'
        )
        
        # Check that the report was created
        self.assertIsNotNone(report_id)
        
        # Retrieve the report and check its values
        report = ReportMonitoring.objects.get(report_monitoring_id=report_id)
        self.assertEqual(report.project_id, 'TEST-PRJ-001')
        self.assertIsNone(report.intrnl_project_id)
        self.assertEqual(report.report_title, 'Test Report')
    
    def test_create_report_with_internal_project(self):
        """Test creating a report with an internal project"""
        report_id = ReportMonitoring.create_report(
            project_id=None,
            intrnl_project_id='TEST-INT-001',
            report_type='Progress Report',
            report_title='Test Internal Report',
            received_from='Project Management',
            date_created=date.today(),
            assigned_to='Project Management',
            description='This is a test internal report'
        )
        
        # Check that the report was created
        self.assertIsNotNone(report_id)
        
        # Retrieve the report and check its values
        report = ReportMonitoring.objects.get(report_monitoring_id=report_id)
        self.assertIsNone(report.project_id)
        self.assertEqual(report.intrnl_project_id, 'TEST-INT-001')
        self.assertEqual(report.report_title, 'Test Internal Report')