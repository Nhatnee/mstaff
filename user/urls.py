from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # Trang đăng nhập
    path('logout/', views.logout_view, name='logout'),  # Đăng xuất
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Trang admin
    path('admin_user/', views.admin_user, name='admin_user'),  # Quản lý nhân viên
    path('admin_department/', views.admin_department, name='admin_department'),  # Quản lý phòng ban
    path('home/', views.home, name='home'),  # Trang nhân viên
    path('dashboard/employee/<int:user_id>/', views.admin_employee_details, name='admin_employee_details'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('salary/', views.admin_salary, name='salary'),
    path('change-password/', views.change_password, name='change_password'),
    path('salary-history/', views.salary_history, name='salary_history'),
]