from django.urls import path
from . import views

urlpatterns = [
    path('contracts/', views.contract_list, name='contract_list'),
    path('contracts/add/', views.contract_add, name='contract_add'),
    path('contracts/edit/<int:pk>/', views.contract_edit, name='contract_edit'),
    path('contracts/delete/<int:pk>/', views.contract_delete, name='contract_delete'),
    path('contracts/detail/<int:pk>/', views.contract_detail, name='contract_detail'),  # New URL
]