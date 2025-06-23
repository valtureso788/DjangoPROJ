from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Count, Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Statistic
from projects.models import Project
from tasks.models import Task
from django.utils import timezone
import datetime


class StatisticsView(LoginRequiredMixin, ListView):
    model = Statistic
    template_name = 'stats/statistics.html'
    context_object_name = 'statistics'
    paginate_by = 10
    
    def get_queryset(self):
        # Обновляем статистику перед отображением
        Statistic.update_daily_stats()
        return Statistic.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем статистику за последние 7 дней
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=6)
        
        # Статистика по проектам
        context['total_projects'] = Project.objects.count()
        context['user_projects'] = Project.objects.filter(owner=self.request.user).count()
        
        # Статистика по задачам
        context['total_tasks'] = Task.objects.count()
        context['user_tasks'] = Task.objects.filter(assigned_to=self.request.user).count()
        context['completed_tasks'] = Task.objects.filter(status='completed').count()
        context['user_completed_tasks'] = Task.objects.filter(
            assigned_to=self.request.user, 
            status='completed'
        ).count()
        
        # Статистика по приоритетам задач
        priority_stats = Task.objects.values('priority').annotate(count=Count('id'))
        context['priority_stats'] = {item['priority']: item['count'] for item in priority_stats}
        
        # Статистика по статусам задач
        status_stats = Task.objects.values('status').annotate(count=Count('id'))
        context['status_stats'] = {item['status']: item['count'] for item in status_stats}
        
        # Данные для графиков
        context['dates'] = [
            (start_date + datetime.timedelta(days=i)).strftime('%d.%m') 
            for i in range(7)
        ]
        
        # Получаем данные по дням
        daily_stats = Statistic.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # Подготавливаем данные для графиков
        tasks_created = [0] * 7
        tasks_completed = [0] * 7
        
        for stat in daily_stats:
            day_index = (stat.date - start_date).days
            if 0 <= day_index < 7:
                tasks_created[day_index] = stat.tasks_created
                tasks_completed[day_index] = stat.tasks_completed
        
        context['tasks_created_data'] = tasks_created
        context['tasks_completed_data'] = tasks_completed
        
        return context


@login_required
def dashboard(request):
    """Дашборд с основной статистикой"""
    # Обновляем статистику
    Statistic.update_daily_stats()
    
    # Получаем статистику за последние 30 дней
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=29)
    
    # Статистика по проектам пользователя
    user_projects = Project.objects.filter(owner=request.user)
    total_user_projects = user_projects.count()
    
    # Статистика по задачам пользователя
    user_tasks = Task.objects.filter(assigned_to=request.user)
    total_user_tasks = user_tasks.count()
    completed_user_tasks = user_tasks.filter(status='completed').count()
    overdue_user_tasks = user_tasks.filter(
        due_date__lt=timezone.now().date(),
        status__in=['new', 'in_progress', 'on_hold']
    ).count()
    
    # Процент выполнения
    completion_rate = 0
    if total_user_tasks > 0:
        completion_rate = int((completed_user_tasks / total_user_tasks) * 100)
    
    # Статистика по приоритетам задач пользователя
    priority_stats = user_tasks.values('priority').annotate(count=Count('id'))
    priority_data = {item['priority']: item['count'] for item in priority_stats}
    
    # Статистика по статусам задач пользователя
    status_stats = user_tasks.values('status').annotate(count=Count('id'))
    status_data = {item['status']: item['count'] for item in status_stats}
    
    context = {
        'total_user_projects': total_user_projects,
        'total_user_tasks': total_user_tasks,
        'completed_user_tasks': completed_user_tasks,
        'overdue_user_tasks': overdue_user_tasks,
        'completion_rate': completion_rate,
        'priority_data': priority_data,
        'status_data': status_data,
    }
    
    return render(request, 'stats/dashboard.html', context)
