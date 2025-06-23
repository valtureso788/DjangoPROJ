from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

class Profile(models.Model):
    """Модель профиля пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.TextField(max_length=500, blank=True)
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f'Профиль пользователя {self.user.username}'
    
    def save(self, *args, **kwargs):
        """Переопределение метода save для изменения размера изображения"""
        super().save(*args, **kwargs)
        
        # Проверяем существование файла перед обработкой
        if self.avatar and os.path.exists(self.avatar.path):
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception as e:
                # Логирование ошибки, но продолжение работы
                print(f"Ошибка при обработке изображения: {e}")
