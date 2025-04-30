from django import forms
from .models import Contract

class ContractForm(forms.ModelForm):
 class Meta:
   model = Contract
   fields = ['contract_id', 'product_id', 'price']  # Added price field
   widgets = {
    'contract_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã hợp đồng'}),
    'product_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID sản phẩm'}),
    'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Giá sản phẩm', 'step': '0.01'}),
}