from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import Project


class Task(models.Model):
    """Модель для задач"""
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('in_progress', 'В процессе'),
        ('on_hold', 'На паузе'),
        ('completed', 'Завершена'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    )
    
    title = models.CharField(max_length=200, verbose_name="Название задачи")
    description = models.TextField(verbose_name="Описание задачи")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks", verbose_name="Проект")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name="assigned_tasks", verbose_name="Исполнитель")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tasks", 
                                  verbose_name="Создатель")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', 
                               verbose_name="Приоритет")
    due_date = models.DateField(null=True, blank=True, verbose_name="Срок выполнения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-priority', 'due_date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('task-detail', kwargs={'pk': self.pk})
    
    @property
    def is_overdue(self):
        """Проверяет, просрочена ли задача"""
        from django.utils import timezone
        if self.due_date and self.status != 'completed':
            return self.due_date < timezone.now().date()
        return False
