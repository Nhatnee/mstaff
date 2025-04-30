from django.urls import path
from . import views

app_name = 'announcements'  # Namespace để tránh xung đột URL

urlpatterns = [
    path('create/', views.announcement_create, name='announcement_create'),
    path('update/<int:id>/', views.announcement_update, name='announcement_update'),
    path('delete/<int:id>/', views.announcement_delete, name='announcement_delete'),
]