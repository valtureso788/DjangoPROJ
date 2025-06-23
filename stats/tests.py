from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from stats.models import Statistic
from projects.models import Project
from tasks.models import Task
from django.utils import timezone
from datetime import date, timedelta


class StatisticModelTests(TestCase):
    """Тесты для модели Statistic"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            start_date=timezone.now().date(),
            owner=self.user
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Task Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user
        )
        self.statistic = Statistic.objects.create(
            date=timezone.now().date(),
            projects_created=1,
            tasks_created=1,
            tasks_completed=0,
            active_users=1
        )
        
    def test_statistic_creation(self):
        """Тест создания статистики"""
        self.assertEqual(self.statistic.date, timezone.now().date())
        self.assertEqual(self.statistic.projects_created, 1)
        self.assertEqual(self.statistic.tasks_created, 1)
        self.assertEqual(self.statistic.tasks_completed, 0)
        self.assertEqual(self.statistic.active_users, 1)
        
    def test_statistic_str(self):
        """Тест строкового представления статистики"""
        self.assertEqual(str(self.statistic), f'Статистика за {timezone.now().date()}')
        
    def test_update_daily_stats(self):
        """Тест обновления ежедневной статистики"""
        # Создаем еще один проект и задачу
        Project.objects.create(
            name='Another Project',
            description='Another Description',
            start_date=timezone.now().date(),
            owner=self.user
        )
        task = Task.objects.create(
            title='Another Task',
            description='Another Task Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user
        )
        
        # Завершаем задачу
        task.status = 'completed'
        task.save()
        
        # Обновляем статистику
        updated_stat = Statistic.update_daily_stats()
        
        # Проверяем, что статистика обновилась
        self.assertEqual(updated_stat.projects_created, 2)
        self.assertEqual(updated_stat.tasks_created, 2)
        self.assertEqual(updated_stat.tasks_completed, 1)


class StatisticsViewTests(TestCase):
    """Тесты для представлений статистики"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        self.statistics_url = reverse('statistics')
        self.dashboard_url = reverse('dashboard')
        
    def test_statistics_view_redirect_if_not_logged_in(self):
        """Тест редиректа со страницы статистики, если пользователь не авторизован"""
        self.client.logout()
        response = self.client.get(self.statistics_url)
        self.assertRedirects(response, f'/login/?next={self.statistics_url}')
        
    def test_statistics_view_logged_in(self):
        """Тест доступа к странице статистики для авторизованного пользователя"""
        response = self.client.get(self.statistics_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stats/statistics.html')
        
    def test_dashboard_view_redirect_if_not_logged_in(self):
        """Тест редиректа со страницы дашборда, если пользователь не авторизован"""
        self.client.logout()
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'/login/?next={self.dashboard_url}')
        
    def test_dashboard_view_logged_in(self):
        """Тест доступа к странице дашборда для авторизованного пользователя"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stats/dashboard.html')


class DashboardTest(TestCase):
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
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stats/dashboard.html')
        self.assertContains(response, 'Test Project')
        self.assertContains(response, 'Test Task')

    def test_dashboard_statistics(self):
        # Create more tasks with different statuses
        Task.objects.create(
            title='Completed Task',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            status='completed'
        )
        Task.objects.create(
            title='In Progress Task',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            status='in_progress'
        )

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check if statistics are present in the response
        self.assertContains(response, 'Всего проектов: 1')
        self.assertContains(response, 'Всего задач: 3')
        self.assertContains(response, 'Завершено: 1')
        self.assertContains(response, 'В процессе: 1')
        self.assertContains(response, 'Новые: 1')


class StatisticsTest(TestCase):
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
        self.client.login(username='testuser', password='testpass123')

    def test_project_statistics(self):
        # Create tasks with different priorities
        Task.objects.create(
            title='Urgent Task',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            priority='urgent',
            status='new'
        )
        Task.objects.create(
            title='High Priority Task',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            priority='high',
            status='in_progress'
        )
        Task.objects.create(
            title='Normal Task',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            priority='normal',
            status='completed'
        )

        response = self.client.get(reverse('project-statistics', kwargs={'pk': self.project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stats/project_statistics.html')
        
        # Check if statistics are present in the response
        self.assertContains(response, 'Приоритеты задач')
        self.assertContains(response, 'Статусы задач')
        self.assertContains(response, 'Прогресс проекта')

    def test_user_statistics(self):
        # Create tasks assigned to the user
        Task.objects.create(
            title='User Task 1',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            status='completed'
        )
        Task.objects.create(
            title='User Task 2',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            status='in_progress'
        )

        response = self.client.get(reverse('user-statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stats/user_statistics.html')
        
        # Check if user statistics are present in the response
        self.assertContains(response, 'Мои задачи')
        self.assertContains(response, 'Завершено: 1')
        self.assertContains(response, 'В процессе: 1')


class ChartDataTest(TestCase):
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
        self.client.login(username='testuser', password='testpass123')

    def test_task_status_chart_data(self):
        response = self.client.get(reverse('task-status-chart-data'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Check if the response contains the expected data structure
        data = response.json()
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        self.assertEqual(len(data['datasets']), 1)
        self.assertIn('data', data['datasets'][0])

    def test_project_progress_chart_data(self):
        response = self.client.get(reverse('project-progress-chart-data'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Check if the response contains the expected data structure
        data = response.json()
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        self.assertEqual(len(data['datasets']), 1)
        self.assertIn('data', data['datasets'][0])
