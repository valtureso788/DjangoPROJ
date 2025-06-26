from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Project(models.Model):
    """Модель для проектов. Хранит информацию о проекте, его владельце, датах и прогрессе."""
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
        """Возвращает количество задач в проекте."""
        return self.tasks.count()
    
    @property
    def completed_task_count(self):
        """Возвращает количество завершённых задач в проекте."""
        return self.tasks.filter(status='completed').count()
    
    @property
    def progress(self):
        """Вычисляет процент выполнения задач в проекте."""
        total = self.task_count
        if total == 0:
            return 0
        return int((self.completed_task_count / total) * 100)

class Feedback(models.Model):
    """Модель для отзывов пользователей. Позволяет хранить ник, почту, пароль (для неанонимных), текст отзыва и оценку."""
    nickname = models.CharField(max_length=100, verbose_name="Ник")
    email = models.EmailField(verbose_name="Почта", blank=True, null=True)
    password = models.CharField(max_length=128, verbose_name="Пароль", blank=True, null=True)
    text = models.TextField(verbose_name="Отзыв")
    rating = models.PositiveSmallIntegerField(
        verbose_name="Оценка",
        choices=[(i, f"{i} звезда{'ы' if i > 1 else ''}") for i in range(1, 6)],
        help_text="Поставьте оценку от 1 до 5, где 5 — отлично"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        """Строковое представление отзыва: ник и первые 30 символов текста."""
        return f"{self.nickname}: {self.text[:30]}..."
