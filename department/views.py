from django.shortcuts import render, redirect, get_object_or_404
from .models import Department
from .forms import DepartmentForm
from django.contrib.auth.models import User
from django.contrib import messages
from user.models import Employee, Position  # Import thêm Position
from django.contrib.auth.decorators import login_required


def admin_department(request):
    departments = Department.objects.all()
    return render(request, 'admin/admin_department.html', {'departments': departments})

def admin_add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_department')
    else:
        form = DepartmentForm()
    return render(request, 'admin/admin_add_department.html', {'form': form})

def admin_edit_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('admin_department')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'admin/admin_edit_department.html', {'form': form})

def admin_delete_department(request, dept_id):
    department = get_object_or_404(Department, id=dept_id)
    if request.method == 'POST':
        department.delete()
        messages.success(request, f'Phòng ban "{department.name}" đã được xóa.')
        return redirect('admin_department')
    return redirect('admin_department')  # Fallback nếu không phải POST

@login_required
def admin_assign_head(request, dept_id):
    department = get_object_or_404(Department, id=dept_id)
    
    if request.method == 'POST':
        head_id = request.POST.get('head')
        # Đảm bảo Position "Nhân viên" (ID=1) và "Trưởng phòng" (ID=2) tồn tại
        Position.objects.get_or_create(id=1, defaults={'name': 'Nhân viên'})
        Position.objects.get_or_create(id=2, defaults={'name': 'Trưởng phòng'})

        # Lấy nhân viên hiện tại đang là trưởng phòng (nếu có)
        current_head = department.head
        if current_head:
            current_employee = Employee.objects.get(user=current_head)
            # Đặt lại position thành "Nhân viên" (ID=1) cho trưởng phòng cũ
            default_position = Position.objects.get(id=1)
            current_employee.position = default_position
            current_employee.save()

        if head_id:
            employee = get_object_or_404(Employee, user__id=head_id, department=department)
            # Cập nhật position thành "Trưởng phòng" (ID=2)
            head_position = Position.objects.get(id=2)
            employee.position = head_position
            employee.save()
            # Gán trưởng phòng mới cho phòng ban
            department.head = employee.user
            department.save()
            messages.success(request, f'Đã cấp quyền trưởng phòng cho {employee.user.username}.')
        else:
            # Xóa quyền trưởng phòng
            department.head = None
            department.save()
            messages.success(request, 'Đã xóa quyền trưởng phòng.')
        return redirect('admin_department')
    
    employees = department.employees.all()
    return render(request, 'admin/assign_head.html', {
        'department': department,
        'employees': employees,
    })

