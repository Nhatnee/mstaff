from django import forms
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
        }
        labels = {
            'title': 'Tiêu đề',
            'content': 'Nội dung',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError('Tiêu đề phải có ít nhất 3 ký tự.')
        return title