from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from projects.models import Project
from tasks.models import Task


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    """Просмотр и редактирование профиля пользователя"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваш профиль был обновлен!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Получаем проекты и задачи пользователя
    user_projects = Project.objects.filter(owner=request.user)
    user_tasks = Task.objects.filter(assigned_to=request.user)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user_projects': user_projects,
        'user_tasks': user_tasks,
        'user_projects_count': user_projects.count(),
        'user_tasks_count': user_tasks.count(),
    }
    
    return render(request, 'users/profile.html', context)
