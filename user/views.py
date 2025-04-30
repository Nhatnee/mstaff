from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Employee
from .forms import UserProfileForm
from department.models import Department
from django.db.models import Sum
from kpi.models import Contract
from .forms import ChangePasswordForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Employee, SalaryHistory
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from announcements.models import Announcement

@login_required
def admin_user(request):
    if request.method == "POST":
        # Tạo nhân viên mới
        if 'create_user' in request.POST:
            try:
                last_user = User.objects.filter(username__startswith='NV').exclude(is_superuser=True).order_by('-id').first()
                if last_user and last_user.username.startswith('NV'):
                    number_part = last_user.username[2:]
                    new_number = int(number_part) + 1 if number_part.isdigit() else 1
                else:
                    new_number = 1

                nv_id = f"NV{str(new_number).zfill(3)}"
                user = User.objects.create_user(
                    username=nv_id,
                    email=f"{nv_id}@gmail.com",
                    password="123456"
                )
                Employee.objects.create(
                    user=user,
                    salary_level=1
                )
                messages.success(request, f'Đã tạo nhân viên {nv_id} thành công!')
                return redirect('admin_user')
            except Exception as e:
                messages.error(request, f'Có lỗi xảy ra: {str(e)}')

        elif 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                if not user.is_superuser:
                    user.delete()
                    messages.success(request, f'Đã xóa nhân viên {user.username} thành công!')
                else:
                    messages.error(request, 'Không thể xóa tài khoản quản trị viên!')
                return redirect('admin_user')
            except User.DoesNotExist:
                messages.error(request, 'Nhân viên không tồn tại!')
            except Exception as e:
                messages.error(request, f'Có lỗi xảy ra: {str(e)}')

    users = User.objects.all().order_by('id')
    user_profiles = {p.user_id: p for p in Employee.objects.filter(user__in=users)}
    return render(request, 'admin_user.html', {
        'users': users,
        'user_profiles': user_profiles
    })

@login_required
def admin_employee_details(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, created = Employee.objects.get_or_create(user=user)
    departments = Department.objects.all()

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()

        profile.full_name = request.POST.get('full_name', profile.full_name)
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.citizen_id = request.POST.get('citizen_id', profile.citizen_id)
        profile.address = request.POST.get('address', profile.address)
        profile.education = request.POST.get('education', profile.education)
        profile.date_of_birth = request.POST.get('date_of_birth', profile.date_of_birth)

        # Xử lý salary_level
        salary_level = request.POST.get('salary_level', profile.salary_level)
        try:
            salary_level = int(salary_level)
            if salary_level < 1 or salary_level > 9:
                messages.error(request, "Bậc lương phải từ 1 đến 9.")
                return render(request, 'admin_employee_details.html', {
                    'user': user,
                    'profile': profile,
                    'departments': departments,
                })
            if salary_level != profile.salary_level:
                # Lưu vào SalaryHistory trước khi cập nhật
                SalaryHistory.objects.create(
                    employee=profile,
                    salary_level=salary_level,
                    effective_date=datetime.now().date()
                )
            profile.salary_level = salary_level
        except ValueError:
            messages.error(request, "Bậc lương phải là một số nguyên.")
            return render(request, 'admin_employee_details.html', {
                'user': user,
                'profile': profile,
                'departments': departments,
            })

        # Xử lý department
        department_id = request.POST.get('department')
        if department_id:
            try:
                profile.department = Department.objects.get(id=int(department_id))
            except (ValueError, Department.DoesNotExist):
                profile.department = None
        else:
            profile.department = None

        profile.save()
        messages.success(request, "Cập nhật thông tin thành công.")
        return redirect('admin_user')

    return render(request, 'admin_employee_details.html', {
        'user': user,
        'profile': profile,
        'departments': departments,
    })

@login_required
def edit_profile(request):
    profile, created = Employee.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            request.user.username = form.cleaned_data['full_name']
            if form.cleaned_data['email']:
                request.user.email = form.cleaned_data['email']
            request.user.save()

            form.save()
            messages.success(request, "Cập nhật thông tin thành công!")
            return redirect('home')
    else:
        form = UserProfileForm(instance=profile, initial={'email': request.user.email})

    return render(request, 'edit_profile.html', {'form': form})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user.models import Employee
from department.models import Department
from kpi.models import Contract

@login_required
def admin_dashboard(request):
    employees = Employee.objects.select_related('user', 'department')
    employee_count = employees.count()
    department_count = Department.objects.count()
    contract_count = Contract.objects.count()
    total_salary = sum(emp.get_total_salary() for emp in employees)
    announcements = Announcement.objects.all().order_by('-created_at')

    # Lấy danh sách phòng ban và số lượng nhân viên từ bảng Employee
    departments = Department.objects.all()
    department_data = []
    for dept in departments:
        # Đếm số nhân viên trong phòng ban dựa trên department_id
        employee_count_in_dept = Employee.objects.filter(department=dept).count()
        if employee_count_in_dept > 0:  # Chỉ thêm nếu có nhân viên
            department_data.append({
                'name': dept.name,
                'count': employee_count_in_dept
            })

    # Thông báo nếu không có dữ liệu
    no_data_message = None
    if not departments:
        no_data_message = "Chưa có phòng ban nào được tạo."
    elif not department_data:
        no_data_message = "Chưa có nhân viên nào trong các phòng ban."

    context = {
        'employee_count': employee_count,
        'department_count': department_count,
        'contract_count': contract_count,
        'total_salary': total_salary,
        'department_data': department_data,  # Dữ liệu cho biểu đồ cột
        'no_data_message': no_data_message,  # Thông báo nếu không có dữ liệu
        'announcements': announcements,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def home(request):
    employee = getattr(request.user, 'employee', None)
    commission_this_month = 0
    salary_this_month = None
    salary_level = None
    announcements = Announcement.objects.all().order_by('-created_at')
    if employee:
        # Tính lương tháng hiện tại
        salary_this_month = employee.get_salary()
        salary_level = employee.salary_level
        
        # Tính hoa hồng tháng hiện tại
        today = datetime.now().date()
        start_date = datetime(today.year, today.month, 1)
        end_date = (start_date + relativedelta(months=1)) - relativedelta(days=1)
        commission_this_month = employee.get_total_commission(start_date, end_date)
    
    contracts = []
    if employee and employee.department and employee.department.name.lower() == "kinh doanh":
        contracts = Contract.objects.filter(employee=employee).order_by('-created_at')

    return render(request, 'user_home.html', {
        'user': request.user,
        'kpis': contracts,
        'salary_this_month': salary_this_month,
        'commission_this_month': commission_this_month,
        'salary_level': salary_level,
        'announcements': announcements,
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard') if user.is_superuser else redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Sai tài khoản hoặc mật khẩu'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def admin_department(request):
    return render(request, 'admin_department.html')

@login_required
def admin_salary(request):
    employees = Employee.objects.select_related('user', 'department')

    total_salary = 0
    total_bonus = 0
    total_salary_with_bonus = 0

    for emp in employees:
        salary = emp.get_salary()
        bonus = emp.get_total_commission()
        total_salary += salary
        total_bonus += bonus
        total_salary_with_bonus += salary + bonus

    context = {
        'employees': employees,
        'total_salary': total_salary,
        'total_bonus': total_bonus,
        'total_salary_with_bonus': total_salary_with_bonus,
    }
    return render(request, 'admin_salary.html', context)

def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            new_password = form.cleaned_data['new_password']

            # Kiểm tra xem user_id có khớp với người dùng hiện tại
            if user_id != request.user.id:
                messages.error(request, "ID người dùng không khớp với tài khoản của bạn.")
                return redirect('change_password')

            # Cập nhật mật khẩu
            request.user.set_password(new_password)
            request.user.save()

            # Đăng xuất sau khi đổi mật khẩu
            messages.success(request, "Đổi mật khẩu thành công! Vui lòng đăng nhập lại.")
            return redirect('logout')  # Chuyển hướng đến đăng xuất để đăng nhập lại
        else:
            # Hiển thị lỗi form nếu có
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ChangePasswordForm()

    return render(request, 'change_password.html', {'form': form})

@login_required
def salary_history(request):
    employee = getattr(request.user, 'employee', None)
    if not employee:
        messages.error(request, "Không tìm thấy thông tin nhân viên.")
        return redirect('home')

    # Tạo danh sách 6 tháng gần nhất
    today = datetime.now().date()
    months = []
    for i in range(6):
        month_date = today - relativedelta(months=i)
        months.append({
            'year': month_date.year,
            'month': month_date.month,
            'label': month_date.strftime('%B %Y'),
            'start_date': datetime(month_date.year, month_date.month, 1),
            'end_date': (datetime(month_date.year, month_date.month, 1) + relativedelta(months=1)) - relativedelta(days=1)
        })
    months.reverse()

    # Tính thu nhập cho từng tháng
    salary_data = []
    for month in months:
        # Lấy salary_level từ lịch sử hoặc hiện tại
        salary_level = employee.salary_level
        history = employee.salary_histories.filter(
            effective_date__lte=month['start_date']
        ).order_by('-effective_date').first()
        if history:
            salary_level = history.salary_level
        
        salary = employee.get_salary(salary_level)
        commission = employee.get_total_commission(month['start_date'], month['end_date'])
        total = salary + commission
        
        salary_data.append({
            'month': month['label'],
            'salary': salary,
            'commission': commission,
            'total': total
        })

    context = {
        'employee': employee,
        'salary_data': salary_data,
    }
    return render(request, 'salary_history.html', context)