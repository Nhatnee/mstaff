from django.contrib.auth.models import User
from django.db import models
from department.models import Department
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator
from contract.models import Contract
from decimal import Decimal

class SalaryHistory(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='salary_histories')
    salary_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)]
    )
    effective_date = models.DateField()  # Ngày áp dụng bậc lương
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - Level {self.salary_level} from {self.effective_date}"

class Position(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    # Định nghĩa các lựa chọn cho trạng thái đào tạo
    TRAINING_STATUS_CHOICES = [
        ('new', 'Chưa đào tạo'),
        ('in_progress', 'Đang đào tạo'),
        ('done', 'Đã đào tạo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    citizen_id = models.CharField(max_length=12, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    salary_level = models.IntegerField(default=1)
    training_status = models.CharField(
        max_length=20,
        choices=TRAINING_STATUS_CHOICES,
        default='new'
    )

    def get_salary(self, salary_level=None):
        salary_base = 2340000
        coefficients = {
            1: 2.34, 2: 2.67, 3: 3.00, 4: 3.33,
            5: 3.66, 6: 3.99, 7: 4.32, 8: 4.65, 9: 4.98
        }
        level = salary_level if salary_level is not None else self.salary_level
        return int(salary_base * coefficients.get(level, 1))

    def get_bhxh(self):
        return Decimal(str(self.get_salary())) * Decimal('0.105')

    def get_total_commission(self, start_date=None, end_date=None):
        # Lấy tất cả hợp đồng của nhân viên trong khoảng thời gian
        contracts = UserContract.objects.filter(employee=self)
        if start_date and end_date:
            contracts = contracts.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            )
        return sum(uc.contract.commission for uc in contracts)

    def get_total_salary(self, start_date=None, end_date=None):
        salary = Decimal(str(self.get_salary()))  # Convert to Decimal
        commission = self.get_total_commission(start_date, end_date)
        bhxh = self.get_bhxh()
        return salary + commission - bhxh

    def __str__(self):
        return self.full_name or self.user.username

class UserContract(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.contract.name}"

class Plan(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='plans')
    kpi = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Giá trị KPI (số nguyên)",
        default=0
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Chờ xử lý'), ('in_progress', 'Đang thực hiện'), ('completed', 'Hoàn thành'), ('ended', 'Kết thúc')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Plan for {self.employee.user.username} ({self.start_date} to {self.end_date})"