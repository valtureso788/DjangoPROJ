from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Project(models.Model):
    """Модель для проектов"""
    name = models.CharField(max_length=200, verbose_name="Название проекта")
    description = models.TextField(verbose_name="Описание проекта")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания", null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects", verbose_name="Владелец")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('project-detail', kwargs={'pk': self.pk})
    
    @property
    def task_count(self):
        """Возвращает количество задач в проекте"""
        return self.tasks.count()
    
    @property
    def completed_task_count(self):
        """Возвращает количество завершенных задач в проекте"""
        return self.tasks.filter(status='completed').count()
    
    @property
    def progress(self):
        """Возвращает прогресс выполнения проекта в процентах"""
        total = self.task_count
        if total == 0:
            return 0
        return int((self.completed_task_count / total) * 100)
