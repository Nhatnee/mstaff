from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Contract
from user.models import Employee
from django.http import HttpResponseForbidden
from .forms import ContractForm
from decimal import Decimal
# Hàm kiểm tra xem user có phải admin không
def is_admin(user):
    return user.is_superuser

# Hàm kiểm tra xem user có phải nhân viên phòng Kinh doanh không
def is_sales_employee(user):
    if not user.is_authenticated:
        return False
    try:
        employee = user.employee
        return employee.department.name.lower() == "kinh doanh"
    except AttributeError:
        return False

# View cho danh sách KPI (chỉ admin được truy cập)
@login_required
@user_passes_test(is_admin, login_url='/login/')
def contract_list(request):
    contracts = Contract.objects.all()
    contracts_with_names = []
    for contract in contracts:
        try:
            employee = Employee.objects.get(id=contract.employee_id)
            contract.employee_name = employee.full_name
        except Employee.DoesNotExist:
            contract.employee_name = "Không có tên"
        contracts_with_names.append(contract)

    return render(request, 'kpi/kpi_list.html', {
        'contracts': contracts_with_names,
    })

# View để thêm hợp đồng (chỉ nhân viên phòng Kinh doanh được truy cập)
@login_required
@user_passes_test(is_sales_employee, login_url='/login/')
def add_contract(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.employee = request.user.employee
            contract.commission = contract.price * Decimal('0.07')  # Chuyển 0.07 thành Decimal
            contract.save()
            messages.success(request, 'Hợp đồng đã được thêm thành công!')
            return redirect('home')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        form = ContractForm()
    return render(request, 'kpi/add_contract.html', {'form': form})