from django.urls import path
from . import views

urlpatterns = [
    path('', views.contract_list, name='contract_list'),
    path('add/', views.add_contract, name='add_contract'),
]