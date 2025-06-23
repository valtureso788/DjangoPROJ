from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Task
from projects.models import Project


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10
    
    def get_queryset(self):
        # Показываем только задачи, назначенные текущему пользователю или созданные им
        user = self.request.user
        return Task.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Task.STATUS_CHOICES
        context['priority_choices'] = Task.PRIORITY_CHOICES
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'project', 'assigned_to', 'status', 'priority', 'due_date']
    success_url = reverse_lazy('task-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ограничиваем выбор проектов только теми, которые принадлежат пользователю
        form.fields['project'].queryset = Project.objects.filter(owner=self.request.user)
        return form


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'project', 'assigned_to', 'status', 'priority', 'due_date']
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def test_func(self):
        task = self.get_object()
        return self.request.user == task.created_by or self.request.user == task.assigned_to
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ограничиваем выбор проектов только теми, которые принадлежат пользователю
        form.fields['project'].queryset = Project.objects.filter(owner=self.request.user)
        return form


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task-list')
    
    def test_func(self):
        task = self.get_object()
        return self.request.user == task.created_by


@login_required
def task_complete(request, pk):
    """Быстрое завершение задачи"""
    task = get_object_or_404(Task, pk=pk)
    if request.user == task.assigned_to or request.user == task.created_by:
        task.status = 'completed'
        task.save()
    return redirect('task-list')
