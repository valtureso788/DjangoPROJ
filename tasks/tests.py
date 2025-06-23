from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import Task
from projects.models import Project
from datetime import date, timedelta
from django.utils import timezone


class TaskModelTests(TestCase):
    """Тесты для модели Task"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            owner=self.user
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            due_date=date.today() + timedelta(days=7),
            priority='high',
            status='new'
        )
        
    def test_task_creation(self):
        """Тест создания задачи"""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'Test Description')
        self.assertEqual(self.task.project, self.project)
        self.assertEqual(self.task.created_by, self.user)
        self.assertEqual(self.task.assigned_to, self.user)
        self.assertTrue(isinstance(self.task, Task))
        self.assertEqual(str(self.task), 'Test Task')
        
    def test_task_status(self):
        """Тест проверки статуса задачи"""
        self.assertEqual(self.task.status, 'new')
        self.task.status = 'completed'
        self.task.save()
        self.assertEqual(self.task.status, 'completed')
        
    def test_task_priority(self):
        """Тест проверки приоритета задачи"""
        self.assertEqual(self.task.priority, 'high')
        self.task.priority = 'urgent'
        self.task.save()
        self.assertEqual(self.task.priority, 'urgent')
        
    def test_task_get_absolute_url(self):
        """Тест получения абсолютного URL задачи"""
        self.assertEqual(self.task.get_absolute_url(), f'/tasks/{self.task.id}/')
        
    def test_task_is_overdue_false(self):
        """Тест проверки, что задача не просрочена"""
        self.assertFalse(self.task.is_overdue)
        
    def test_task_is_overdue_true(self):
        """Тест проверки, что задача просрочена"""
        self.task.due_date = date.today() - timedelta(days=1)
        self.task.save()
        self.assertTrue(self.task.is_overdue)
        
    def test_task_is_not_overdue_when_completed(self):
        """Тест проверки, что завершенная задача не считается просроченной"""
        self.task.due_date = date.today() - timedelta(days=1)
        self.task.status = 'completed'
        self.task.save()
        self.assertFalse(self.task.is_overdue)


class TaskViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            owner=self.user
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            due_date=date.today() + timedelta(days=7),
            priority='high',
            status='new'
        )

    def test_task_list_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_list.html')
        self.assertContains(response, 'Test Task')

    def test_task_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('task-detail', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_detail.html')
        self.assertContains(response, 'Test Task')

    def test_task_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('task-create'), {
            'title': 'New Task',
            'description': 'New Description',
            'project': self.project.id,
            'assigned_to': self.user.id,
            'due_date': date.today() + timedelta(days=7),
            'priority': 'high',
            'status': 'new'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_task_update_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('task-update', kwargs={'pk': self.task.pk}),
            {
                'title': 'Updated Task',
                'description': 'Updated Description',
                'project': self.project.id,
                'assigned_to': self.user.id,
                'due_date': date.today() + timedelta(days=7),
                'priority': 'urgent',
                'status': 'in_progress'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertEqual(self.task.status, 'in_progress')

    def test_task_delete_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('task-delete', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_task_complete_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('task-complete', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    def test_unauthorized_access(self):
        # Test without login
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, 302)

        # Test with different user
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('task-detail', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 403)


class TaskFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            owner=self.user
        )

    def test_task_form_validation(self):
        # Test valid data
        form_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'project': self.project.id,
            'assigned_to': self.user.id,
            'due_date': date.today() + timedelta(days=7),
            'priority': 'high',
            'status': 'new'
        }
        from .forms import TaskForm
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test invalid data (due_date in the past)
        form_data['due_date'] = date.today() - timedelta(days=1)
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)

        # Test missing required field
        form_data.pop('title')
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
