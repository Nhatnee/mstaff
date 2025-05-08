from django.contrib.auth.models import User
from django.db import models
from department.models import Department
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator

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
    
    def get_total_commission(self, start_date=None, end_date=None):
        from kpi.models import Contract
        queryset = Contract.objects.filter(employee=self)
        if start_date is not None and end_date is not None:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        total_commission = queryset.aggregate(total_commission=Sum('commission'))['total_commission']
        return int(total_commission or 0)

    def get_total_salary(self, start_date=None, end_date=None):
        return self.get_salary() + self.get_total_commission(start_date, end_date)

    def __str__(self):
        return self.full_name or self.user.username