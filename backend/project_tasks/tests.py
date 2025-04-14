from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import InternalProjectTask, ExternalProjectTask

class InternalTaskModelTests(TestCase):
    def setUp(self):

        self.task = InternalProjectTask.objects.create(
            intrnl_task_id="TEST-001",
            intrnl_project_id="PROJ-001",
            intrnl_task_description="Test task",
            intrnl_task_status="pending",
            intrnl_task_deadline=date.today() + timedelta(days=7),
            intrnl_project_labor_id="LABOR-001"
        )
    
    def test_task_creation(self):
        self.assertEqual(self.task.intrnl_task_id, "TEST-001")
        self.assertEqual(self.task.intrnl_task_status, "pending")
    
    def test_task_str_representation(self):
        self.assertEqual(str(self.task), "TEST-001")

class ExternalTaskModelTests(TestCase):
    def setUp(self):
        self.task = ExternalProjectTask.objects.create(
            task_id="EXT-TEST-001",
            project_id="EXT-PROJ-001",
            task_description="External test task",
            task_status="pending",
            task_deadline=date.today() + timedelta(days=7),
            project_labor_id="EXT-LABOR-001"
        )
    
    def test_task_creation(self):
        self.assertEqual(self.task.task_id, "EXT-TEST-001")
        self.assertEqual(self.task.task_status, "pending")
    
    def test_task_str_representation(self):
        self.assertEqual(str(self.task), "EXT-TEST-001")

class TaskListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        InternalProjectTask.objects.create(
            intrnl_task_id="INT-001",
            intrnl_project_id="PROJ-001",
            intrnl_task_description="Internal task 1",
            intrnl_task_status="pending",
            intrnl_task_deadline=date.today() + timedelta(days=7),
            intrnl_project_labor_id="LABOR-001"
        )
        ExternalProjectTask.objects.create(
            task_id="EXT-001",
            project_id="EXT-PROJ-001",
            task_description="External task 1",
            task_status="pending",
            task_deadline=date.today() + timedelta(days=7),
            project_labor_id="EXT-LABOR-001"
        )
    
    def test_task_list_view(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "INT-001")
        self.assertContains(response, "EXT-001")
    
    def test_task_list_filtering(self):
        response = self.client.get(reverse('task_list') + '?type=internal')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "INT-001")
        self.assertNotContains(response, "EXT-001")

class TaskDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.internal_task = InternalProjectTask.objects.create(
            intrnl_task_id="INT-001",
            intrnl_project_id="PROJ-001",
            intrnl_task_description="Internal task 1",
            intrnl_task_status="pending",
            intrnl_task_deadline=date.today() + timedelta(days=7),
            intrnl_project_labor_id="LABOR-001"
        )
        self.external_task = ExternalProjectTask.objects.create(
            task_id="EXT-001",
            project_id="EXT-PROJ-001",
            task_description="External task 1",
            task_status="pending",
            task_deadline=date.today() + timedelta(days=7),
            project_labor_id="EXT-LABOR-001"
        )
    
    def test_internal_task_detail_view(self):
        response = self.client.get(reverse('task_detail', args=['internal', 'INT-001']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "INT-001")
        self.assertContains(response, "Internal task 1")
    
    def test_external_task_detail_view(self):
        response = self.client.get(reverse('task_detail', args=['external', 'EXT-001']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "EXT-001")
        self.assertContains(response, "External task 1")
    
    def test_nonexistent_task_detail_view(self):
        response = self.client.get(reverse('task_detail', args=['internal', 'NONEXISTENT']))
        self.assertEqual(response.status_code, 404)

class APITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.force_authenticate(user=self.user)
        
        self.internal_task = InternalProjectTask.objects.create(
            intrnl_task_id="INT-001",
            intrnl_project_id="PROJ-001",
            intrnl_task_description="Internal task 1",
            intrnl_task_status="pending",
            intrnl_task_deadline=date.today() + timedelta(days=7),
            intrnl_project_labor_id="LABOR-001"
        )
        self.external_task = ExternalProjectTask.objects.create(
            task_id="EXT-001",
            project_id="EXT-PROJ-001",
            task_description="External task 1",
            task_status="pending",
            task_deadline=date.today() + timedelta(days=7),
            project_labor_id="EXT-LABOR-001"
        )
    
    def test_get_internal_tasks(self):
        url = reverse('internalprojecttask-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['intrnl_task_id'], "INT-001")
    
    def test_get_external_tasks(self):
        """Test retrieving external tasks via API"""
        url = reverse('externalprojecttask-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['task_id'], "EXT-001")
    
    def test_create_internal_task(self):
        url = reverse('internalprojecttask-list')
        data = {
            'intrnl_project_id': 'PROJ-002',
            'intrnl_task_description': 'New internal task',
            'intrnl_task_status': 'pending',
            'intrnl_task_deadline': (date.today() + timedelta(days=14)).isoformat(),
            'intrnl_project_labor_id': 'LABOR-002'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InternalProjectTask.objects.count(), 2)
        self.assertEqual(InternalProjectTask.objects.last().intrnl_task_description, 'New internal task')
    
    def test_update_internal_task(self):
        url = reverse('internalprojecttask-detail', args=[self.internal_task.intrnl_task_id])
        data = {
            'intrnl_project_id': 'PROJ-001',
            'intrnl_task_description': 'Updated internal task',
            'intrnl_task_status': 'in_progress',
            'intrnl_task_deadline': self.internal_task.intrnl_task_deadline.isoformat(),
            'intrnl_project_labor_id': 'LABOR-001'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.internal_task.refresh_from_db()
        self.assertEqual(self.internal_task.intrnl_task_description, 'Updated internal task')
        self.assertEqual(self.internal_task.intrnl_task_status, 'in_progress')
    
    def test_delete_internal_task(self):
        url = reverse('internalprojecttask-detail', args=[self.internal_task.intrnl_task_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(InternalProjectTask.objects.count(), 0)
    
    def test_bulk_update_status(self):
        url = reverse('bulk_update_status')
        data = {
            'task_ids': [self.internal_task.intrnl_task_id, self.external_task.task_id],
            'task_types': ['internal', 'external'],
            'status': 'completed'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.internal_task.refresh_from_db()
        self.external_task.refresh_from_db()
        
        self.assertEqual(self.internal_task.intrnl_task_status, 'completed')
        self.assertEqual(self.external_task.task_status, 'completed')