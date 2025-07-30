from datetime import date
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render,get_object_or_404

from django.views.generic import ListView,DetailView
from django.views import View

from .forms import LoginForm,RegiserForm
from .models import Account_Student

class StartingPageView(View):
    #template_name='tutor_app/index.html'
    def get(self,request):
        return render(request,'tutor_app/index.html')
    
class LoginFormView(View):
    
    def get(self,request):

        context={
            'login_form': LoginForm(),
            'error': False
        }
        return render(request,'tutor_app/login.html',context)
    
    def post(self,request):
        login_form=LoginForm(request.POST)
        if login_form.is_valid():
            user_name = login_form.cleaned_data['user_name']
            password = login_form.cleaned_data['password']
            try:
                account= Account_Student.objects.get(user_name=user_name)
                message_error=[]
                if account:
                    if account.password==password:
                        # Đăng nhập thành công
                        return HttpResponseRedirect(reverse('hello-page'))
                    else:
                        message_error.append("sai mật khẩu")
                else:
                    message_error.append("không tìm thấy tên đăng nhập")
                
                context={
                    'error':True,
                    'message_error':message_error,
                    'login_form':login_form
                }
                return render(request,'tutor_app/login.html',context)
            
            except Exception as error:
                context={
                            'error':True,
                            'login_form': login_form,
                            'message_error':f'Lỗi ngoại lệ:{error}'
                            }
                return render(request,'tutor_app/login.html',context)
        
        else:
            context={
                'error':True,
                'login_form': login_form,
                'message_error':'form không hợp lệ'
            }
            return render(request,'tutor_app/login.html',context)
        

class RegiserFormView(View):
    def get(self,request):
        
        context={
            'register_form': RegiserForm(),
        }
        return render(request,'tutor_app/register.html',context)
    

class HelloView(View):
    def get(self,request):
        return render(request,'tutor_app/hello.html')
