from django.db import models
from django.db.models import Count, Sum
from django.utils import timezone
import datetime


class Statistic(models.Model):
    """Модель для хранения статистики"""
    date = models.DateField(default=timezone.now, verbose_name="Дата")
    projects_created = models.IntegerField(default=0, verbose_name="Создано проектов")
    tasks_created = models.IntegerField(default=0, verbose_name="Создано задач")
    tasks_completed = models.IntegerField(default=0, verbose_name="Завершено задач")
    active_users = models.IntegerField(default=0, verbose_name="Активных пользователей")
    
    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"
        ordering = ['-date']
    
    def __str__(self):
        return f'Статистика за {self.date}'
    
    @classmethod
    def update_daily_stats(cls):
        """Обновляет ежедневную статистику"""
        today = timezone.now().date()
        from projects.models import Project
        from tasks.models import Task
        from django.contrib.auth.models import User
        
        # Получаем данные за сегодня
        projects_created = Project.objects.filter(created_at__date=today).count()
        tasks_created = Task.objects.filter(created_at__date=today).count()
        tasks_completed = Task.objects.filter(
            status='completed', 
            updated_at__date=today
        ).count()
        active_users = User.objects.filter(
            last_login__date=today
        ).count()
        
        # Создаем или обновляем запись статистики
        stat, created = cls.objects.get_or_create(
            date=today,
            defaults={
                'projects_created': projects_created,
                'tasks_created': tasks_created,
                'tasks_completed': tasks_completed,
                'active_users': active_users
            }
        )
        
        if not created:
            stat.projects_created = projects_created
            stat.tasks_created = tasks_created
            stat.tasks_completed = tasks_completed
            stat.active_users = active_users
            stat.save()
        
        return stat
