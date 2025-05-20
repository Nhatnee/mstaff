from django.db import models

class Contract(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên", default="Unknown")
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá bán", default=0.00)
    commission = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Hoa hồng", default=0.00)

    def __str__(self):
        return f"Contract - {self.name}"
