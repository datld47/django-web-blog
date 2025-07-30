from django import forms
from .models import Account_Student,Student


class LoginForm(forms.Form):
    user_name = forms.CharField(max_length=50, label='Tên đăng nhập')
    password = forms.CharField(widget=forms.PasswordInput, max_length=20, label='Mật khẩu')
        
class RegiserForm(forms.ModelForm):
    class Meta:
        model=Student
        fields='__all__'
        #exclude=['post']
        # labels={
        #     'user_name':'Your Name',
        #     'user_email':'Your Email',
        #     'text':'Your comment'
        # }
