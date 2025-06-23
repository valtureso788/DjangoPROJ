from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Project
from tasks.models import Task


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        # Показываем только проекты, принадлежащие текущему пользователю или где он участвует
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(tasks__assigned_to=user)
        ).distinct()


class ProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context['tasks'] = Task.objects.filter(project=project).order_by('-created_at')
        context['can_edit'] = self.request.user == project.owner
        context['task_statuses'] = {
            'new': Task.objects.filter(project=project, status='new').count(),
            'in_progress': Task.objects.filter(project=project, status='in_progress').count(),
            'completed': Task.objects.filter(project=project, status='completed').count(),
            'on_hold': Task.objects.filter(project=project, status='on_hold').count(),
        }
        return context
    
    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner or project.tasks.filter(assigned_to=self.request.user).exists()


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['name', 'description', 'start_date', 'end_date']
    success_url = reverse_lazy('project-list')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['name', 'description', 'start_date', 'end_date']
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('project-list')
    
    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner


def home(request):
    """Главная страница"""
    if request.user.is_authenticated:
        user_projects = Project.objects.filter(owner=request.user)[:5]
        user_tasks = Task.objects.filter(assigned_to=request.user).order_by('due_date')[:5]
        
        context = {
            'projects': user_projects,
            'tasks': user_tasks,
        }
        return render(request, 'projects/home.html', context)
    else:
        return render(request, 'projects/landing.html')
