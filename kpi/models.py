from django.db import models
from user.models import Employee

class Contract(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contracts')
    contract_id = models.CharField(max_length=50)
    product_id = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New commission field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contract {self.contract_id} - {self.employee.user.username}"