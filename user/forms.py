from django import forms
from .models import Employee
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['full_name','email', 'phone_number', 'citizen_id', 'address', 'education', 'date_of_birth', 'department',]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class ChangePasswordForm(forms.Form):
    user_id = forms.IntegerField(label="ID Người dùng", min_value=1)
    current_password = forms.CharField(label="Mật khẩu hiện tại", widget=forms.PasswordInput)
    new_password = forms.CharField(label="Mật khẩu mới", widget=forms.PasswordInput, min_length=1)
    confirm_password = forms.CharField(label="Xác nhận mật khẩu mới", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        user_id = cleaned_data.get('user_id')
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError("ID người dùng không tồn tại.")

        if not user.check_password(current_password):
            raise ValidationError("Mật khẩu hiện tại không đúng.")

        if new_password != confirm_password:
            raise ValidationError("Mật khẩu mới và xác nhận mật khẩu không khớp.")

        return cleaned_data

class PasswordResetRequestForm(forms.Form):
    user_id = forms.IntegerField(label="ID Nhân viên", min_value=1)

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        if not User.objects.filter(id=user_id).exists():
            raise ValidationError("ID nhân viên không tồn tại.")
        return user_id