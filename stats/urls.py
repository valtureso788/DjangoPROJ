from django.urls import path
from . import views

urlpatterns = [
    path('', views.StatisticsView.as_view(), name='statistics'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
