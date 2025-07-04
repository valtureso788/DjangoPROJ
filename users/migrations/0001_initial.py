# Generated by Django 5.2.2 on 2025-06-05 08:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(default='default.jpg', upload_to='profile_pics', verbose_name='Аватар')),
                ('bio', models.TextField(blank=True, max_length=500, verbose_name='О себе')),
                ('position', models.CharField(blank=True, max_length=100, verbose_name='Должность')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
    ]
