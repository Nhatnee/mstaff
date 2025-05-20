from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Employee, SalaryHistory
from .forms import UserProfileForm, ChangePasswordForm
from department.models import Department
from django.db.models import Sum
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from announcements.models import Announcement
from contract.models import Contract  
from django.contrib.auth.models import User
from .models import Employee, Plan
from decimal import Decimal



@login_required
def admin_user(request):
    if not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền truy cập trang này!")
        return redirect('home')

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
                    salary_level=1,
                    training_status='new'  # Đặt trạng thái đào tạo mặc định
                )
                messages.success(request, f'Đã tạo nhân viên {nv_id} thành công!')
                return redirect('admin_user')
            except Exception as e:
                messages.error(request, f'Có lỗi xảy ra: {str(e)}')

        # Xóa nhân viên
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

        # Thay đổi trạng thái đào tạo
        elif 'change_training' in request.POST:
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                if user.is_superuser:
                    messages.error(request, 'Không thể thay đổi trạng thái đào tạo cho quản trị viên!')
                    return redirect('admin_user')
                
                employee = get_object_or_404(Employee, user=user)
                current_status = employee.training_status
                if current_status == 'new':
                    employee.training_status = 'in_progress'
                    messages.success(request, f'Nhân viên {user.username} đã bắt đầu đào tạo!')
                elif current_status == 'in_progress':
                    employee.training_status = 'done'
                    messages.success(request, f'Nhân viên {user.username} đã hoàn thành đào tạo!')
                elif current_status == 'done':
                    messages.info(request, f'Nhân viên {user.username} đã hoàn thành đào tạo, không thể thay đổi thêm!')
                employee.save()
                return redirect('admin_user')
            except User.DoesNotExist:
                messages.error(request, 'Nhân viên không tồn tại!')
            except Employee.DoesNotExist:
                messages.error(request, 'Thông tin nhân viên không tồn tại!')
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

@login_required
def admin_dashboard(request):
    employees = Employee.objects.select_related('user', 'department')
    employee_count = employees.count()
    department_count = Department.objects.count()
    total_salary = sum(emp.get_total_salary() for emp in employees)
    announcements = Announcement.objects.all()
    contract_count = Contract.objects.count()

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
        'total_salary': total_salary,
        'department_data': department_data,  # Dữ liệu cho biểu đồ cột
        'no_data_message': no_data_message,  # Thông báo nếu không có dữ liệu
        'announcements': announcements,
        'contract_count': contract_count,
    }
    return render(request, 'admin_dashboard.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Employee, Contract, UserContract
import logging
import re
from django.db import IntegrityError
from django.utils import timezone

logger = logging.getLogger(__name__)

@login_required
def home(request):
    # Lấy thông tin nhân viên
    employee = getattr(request.user, 'employee', None)
    if not employee:
        logger.error(f"No Employee found for user: {request.user.username}")
        messages.error(request, "Không tìm thấy thông tin nhân viên. Vui lòng liên hệ quản trị viên.")
        return redirect('home')

    # Lấy hợp đồng đã tạo
    created_contracts = UserContract.objects.filter(employee=employee).select_related('contract')
    
    # Tính tổng hoa hồng tháng này
    current_month = timezone.now().month
    current_year = timezone.now().year
    current_date = timezone.now().date()
    commission_this_month = sum(
        uc.contract.commission for uc in created_contracts
        if uc.created_at.month == current_month and uc.created_at.year == current_year
    )
    
    # Lấy kế hoạch hiện hành của nhân viên
    current_plan = Plan.objects.filter(
        employee=employee,
        start_date__year=current_year,
        start_date__month__lte=current_month,
        end_date__year=current_year,
        end_date__month__gte=current_month
    ).first()

    kpi_target = current_plan.kpi if current_plan else 0
    kpi_achieved = commission_this_month
    kpi_percentage = min((kpi_achieved / kpi_target) * 100, 100) if kpi_target > 0 else 0

    # Cập nhật trạng thái của kế hoạch
    if current_plan:
        if kpi_achieved >= kpi_target and current_date <= current_plan.end_date:
            current_plan.status = 'completed'
        elif current_date > current_plan.end_date:
            current_plan.status = 'ended'
        elif current_date < current_plan.start_date:
            current_plan.status = 'pending'
        else:
            current_plan.status = 'in_progress'
        current_plan.save()

    salary_this_month = employee.get_salary() if employee else 0
    bhxh = employee.get_bhxh() if employee else Decimal('0')
    total_salary = Decimal(str(salary_this_month)) + commission_this_month - bhxh if employee else Decimal('0')
    salary_level = employee.salary_level if employee else None
    contracts = Contract.objects.all()
    announcements = Announcement.objects.all().order_by('-created_at')

    # Debug: Kiểm tra dữ liệu
    logger.info(f"Contracts: {list(contracts)}")
    logger.info(f"Created Contracts: {list(created_contracts)}")
    logger.info(f"Commission this month: {commission_this_month}")
    logger.info(f"Current Plan: {current_plan}")
    logger.info(f"KPI Target: {kpi_target}, KPI Achieved: {kpi_achieved}, KPI Percentage: {kpi_percentage}%, Status: {current_plan.status if current_plan else 'No plan'}")

    if request.method == 'POST':
        logger.info(f"POST data: {request.POST}")
        action = request.POST.get('action')
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')

        # Validate customer name and phone
        if not customer_name or not customer_phone:
            messages.error(request, "Vui lòng nhập đầy đủ tên khách hàng và số điện thoại.")
            logger.warning("Missing customer_name or customer_phone")
            return redirect('home')

        # Kiểm tra định dạng số điện thoại
        if not re.match(r'^\+?\d{9,12}$', customer_phone):
            messages.error(request, "Số điện thoại không hợp lệ.")
            logger.warning(f"Invalid phone number: {customer_phone}")
            return redirect('home')

        if action == 'create':
            contract_id = request.POST.get('contract')
            try:
                contract = get_object_or_404(Contract, id=contract_id)
                UserContract.objects.create(
                    employee=employee,
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    contract=contract
                )
                messages.success(request, f"Đã tạo hợp đồng {contract.name} thành công!")
                logger.info(f"Created contract {contract.name} for employee {employee.user.username}")
            except IntegrityError as e:
                messages.error(request, f"Lỗi cơ sở dữ liệu: {str(e)}")
                logger.error(f"IntegrityError creating contract: {str(e)}", exc_info=True)
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra: {str(e)}")
                logger.error(f"Unexpected error creating contract: {str(e)}", exc_info=True)

        elif action == 'edit':
            created_contract_id = request.POST.get('created_contract_id')
            try:
                user_contract = get_object_or_404(UserContract, id=created_contract_id, employee=employee)
                user_contract.customer_name = customer_name
                user_contract.customer_phone = customer_phone
                user_contract.save()
                messages.success(request, f"Đã cập nhật hợp đồng {user_contract.contract.name} thành công!")
                logger.info(f"Updated contract {user_contract.contract.name} for employee {employee.user.username}")
            except IntegrityError as e:
                messages.error(request, f"Lỗi cơ sở dữ liệu: {str(e)}")
                logger.error(f"IntegrityError updating contract: {str(e)}", exc_info=True)
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra: {str(e)}")
                logger.error(f"Unexpected error updating contract: {str(e)}", exc_info=True)

        return redirect('home')

    return render(request, 'user_home.html', {
        'user': request.user,
        'salary_this_month': salary_this_month,
        'bhxh': bhxh,
        'commission_this_month': commission_this_month,
        'total_salary': total_salary,
        'salary_level': salary_level,
        'announcements': announcements,
        'contracts': contracts,
        'created_contracts': created_contracts,
        'kpi_target': kpi_target,
        'kpi_achieved': kpi_achieved,
        'kpi_percentage': kpi_percentage,
        'current_plan': current_plan,
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
    # Lấy tháng và năm từ request hoặc mặc định là tháng hiện tại
    selected_month = int(request.GET.get('month', timezone.now().month))
    selected_year = int(request.GET.get('year', timezone.now().year))

    # Tính ngày bắt đầu và kết thúc của tháng được chọn
    start_date = datetime(selected_year, selected_month, 1)
    if selected_month == 12:
        end_date = datetime(selected_year + 1, 1, 1) - timezone.timedelta(days=1)
    else:
        end_date = datetime(selected_year, selected_month + 1, 1) - timezone.timedelta(days=1)

    # Lấy tất cả nhân viên
    employees = Employee.objects.all()

# Tính lương, BHXH, và hoa hồng cho từng nhân viên trong tháng được chọn
    for employee in employees:
        employee.total_commission = employee.get_total_commission(start_date, end_date)
        employee.bhxh = employee.get_bhxh()
        employee.total_salary = employee.get_total_salary(start_date, end_date)

    # Tính tổng
    total_salary = sum(employee.get_salary() for employee in employees)
    total_bhxh = sum(employee.bhxh for employee in employees)
    total_bonus = sum(employee.total_commission for employee in employees)
    total_salary_with_bonus = sum(employee.total_salary for employee in employees)

    return render(request, 'admin_salary.html', {
        'employees': employees,
        'total_salary': total_salary,
        'total_bhxh': total_bhxh,
        'total_bonus': total_bonus,
        'total_salary_with_bonus': total_salary_with_bonus,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': range(1, 13),
        'years': range(2020, timezone.now().year + 1),
    })

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

    # Lấy tháng hiện tại
    today = timezone.now().date()
    month_date = today
    year = month_date.year
    month = month_date.month
    start_date = datetime(year, month, 1)
    end_date = (start_date + relativedelta(months=1)) - relativedelta(days=1)
    month_label = month_date.strftime('%B %Y')

    # Lấy salary_level từ lịch sử hoặc hiện tại
    salary_level = employee.salary_level
    history = employee.salary_histories.filter(
        effective_date__lte=start_date
    ).order_by('-effective_date').first()
    if history:
        salary_level = history.salary_level

    # Tính lương, BHXH, hoa hồng, tổng thu nhập
    salary = employee.get_salary(salary_level)
    bhxh = employee.get_bhxh()
    commission = employee.get_total_commission(start_date, end_date)
    total = Decimal(str(salary)) + commission - bhxh

    # Tạo salary_data
    salary_data = [{
        'month': month_label,
        'salary': salary,
        'bhxh': bhxh,
        'commission': commission,
        'total': total
    }]

    context = {
        'employee': employee,
        'salary_data': salary_data,
    }
    return render(request, 'salary_history.html', context)

@login_required
def admin_employee_plan(request, user_id):
    # Lấy user bằng filter
    user_queryset = User.objects.filter(id=user_id)
    print(user_id)  # Giữ lại để debug
    # Kiểm tra xem user có tồn tại không
    if not user_queryset.exists():
        messages.error(request, 'Không tìm thấy người dùng!')
        return redirect('admin_user')  # Hoặc một trang lỗi khác
    user = user_queryset.first()  # Lấy user đầu tiên từ QuerySet
    
    # Lấy employee liên kết với user
    employee = get_object_or_404(Employee, user=user)
    plans = employee.plans.all()

    if request.method == 'POST':
        if 'add_plan' in request.POST:
            description = request.POST.get('description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            status = request.POST.get('status')
            # Kiểm tra đầu vào cơ bản
            if description and start_date and end_date and status:
                Plan.objects.create(
                    employee=employee,
                    kpi=description,
                    start_date=start_date,
                    end_date=end_date,
                    status=status
                )
                messages.success(request, 'Thêm kế hoạch thành công!')
            else:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin!')
            return redirect('admin_employee_plan', user_id=user_id)
        elif 'edit_plan' in request.POST:
            plan_id = request.POST.get('plan_id')
            plan = get_object_or_404(Plan, id=plan_id)
            description = request.POST.get('description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            status = request.POST.get('status')
            # Kiểm tra đầu vào
            if description and start_date and end_date and status:
                plan.kpi = description
                plan.start_date = start_date
                plan.end_date = end_date
                plan.status = status
                plan.save()
                messages.success(request, 'Cập nhật kế hoạch thành công!')
            else:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin!')
            return redirect('admin_employee_plan', user_id=user_id)
        elif 'delete_plan' in request.POST:
            plan_id = request.POST.get('plan_id')
            plan = get_object_or_404(Plan, id=plan_id)
            plan.delete()
            messages.success(request, 'Xóa kế hoạch thành công!')
            return redirect('admin_employee_plan', user_id=user_id)

    return render(request, 'admin_employee_plan.html', {
        'employee': employee,
        'plans': plans
    })