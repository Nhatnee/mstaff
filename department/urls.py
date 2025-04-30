from django.urls import path
from . import views

urlpatterns = [
    path('admin/department/', views.admin_department, name='admin_department'),
    path('admin/department/add/', views.admin_add_department, name='admin_add_department'),
    path('admin/department/edit/<int:department_id>/', views.admin_edit_department, name='admin_edit_department'),
    path('admin/department/delete/<int:dept_id>/', views.admin_delete_department, name='admin_delete_department'),
]