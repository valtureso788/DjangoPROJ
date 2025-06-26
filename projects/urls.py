from django.urls import path
from . import views
from .views import FeedbackCreateView, FeedbackListView

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/new/', views.ProjectCreateView.as_view(), name='project-create'),
    path('projects/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project-update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('feedback/', FeedbackCreateView.as_view(), name='feedback-create'),
    path('feedbacks/', FeedbackListView.as_view(), name='feedback-list'),
]
