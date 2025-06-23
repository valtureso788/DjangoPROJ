from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from projects.models import Project
from tasks.models import Task
from datetime import date, timedelta


class ProjectModelTests(TestCase):
    """Тесты для модели Project"""
    
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
        
    def test_project_creation(self):
        """Тест создания проекта"""
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.description, 'Test Description')
        self.assertEqual(self.project.start_date, date.today())
        self.assertEqual(self.project.end_date, date.today() + timedelta(days=30))
        self.assertEqual(self.project.owner, self.user)
        self.assertTrue(isinstance(self.project, Project))
        
    def test_project_str(self):
        """Тест строкового представления проекта"""
        self.assertEqual(str(self.project), 'Test Project')
        
    def test_project_get_absolute_url(self):
        """Тест получения абсолютного URL проекта"""
        self.assertEqual(self.project.get_absolute_url(), f'/projects/{self.project.id}/')
        
    def test_project_task_count(self):
        """Тест подсчета задач в проекте"""
        Task.objects.create(
            title='Task 1',
            description='Task Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user
        )
        Task.objects.create(
            title='Task 2',
            description='Task Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user
        )
        self.assertEqual(self.project.task_count, 2)
        
    def test_project_completed_task_count(self):
        """Тест подсчета завершенных задач в проекте"""
        Task.objects.create(
            title='Task 1',
            description='Task Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            status='completed'
        )
        Task.objects.create(
            title='Task 2',
            description='Task Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user
        )
        self.assertEqual(self.project.completed_task_count, 1)
        
    def test_project_progress(self):
        """Тест расчета прогресса проекта"""
        self.assertEqual(self.project.progress, 0)
        self.assertEqual(self.project.task_count, 0)
        self.assertEqual(self.project.completed_task_count, 0)


class ProjectViewTest(TestCase):
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

    def test_project_list_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_list.html')
        self.assertContains(response, 'Test Project')

    def test_project_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('project-detail', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_detail.html')
        self.assertContains(response, 'Test Project')

    def test_project_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('project-create'), {
            'name': 'New Project',
            'description': 'New Description',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30)
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Project.objects.filter(name='New Project').exists())

    def test_project_update_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('project-update', kwargs={'pk': self.project.pk}),
            {
                'name': 'Updated Project',
                'description': 'Updated Description',
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=30)
            }
        )
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project')

    def test_project_delete_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('project-delete', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_unauthorized_access(self):
        # Test without login
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test with different user
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('project-detail', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden


class ProjectFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_project_form_validation(self):
        # Test valid data
        form_data = {
            'name': 'Test Project',
            'description': 'Test Description',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30)
        }
        from .forms import ProjectForm
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test invalid data (end_date before start_date)
        form_data['end_date'] = date.today() - timedelta(days=1)
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)

        # Test missing required field
        form_data.pop('name')
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
