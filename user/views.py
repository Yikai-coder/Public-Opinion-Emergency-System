from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

import logging
logger = logging.getLogger("user")

# Create your views here.
class LoginView(generic.TemplateView):
    # model = Question
    template_name = 'user/login.html'

    def post(self, request):
        loginUsername = request.POST['loginUsername']
        loginPassword = request.POST['loginPassword']
        def check_login(userName, password):
            # try:
            #     user=User.objects.get(username=userName)
            # except User.DoesNotExist:
            #     return -1, -1
            # if user.check_password(password):
            #     return 0, user.id
            # return -1, -1
            user = authenticate(username=userName, password=password)
            if user is not None:
                # A backend authenticated the credentials
                login(request, user)
                return 0, user.id 
            else:
                return -1, -1
                # No backend authenticated the credentials


        # 验证正确
        status, uid = check_login(loginUsername, loginPassword)
        if status == 0:
            logger.warning("uid:"+str(uid)+" log in.")
            return JsonResponse(data={'code': 1, 'uid':uid})
        else:
            return JsonResponse(data={'code': -1, 'msg': "Incorrect username or password"})


class RegisterView(generic.TemplateView):
    template_name: str = 'user/register.html'

    def post(self, request):
        registerUsername = request.POST['registerUsername']
        registerEmail = request.POST['registerEmail']
        registerPassword = request.POST['registerPassword']

        def check_register(userName, email, password):
            if User.objects.filter(username=userName).exists():
                return 'userName already exists'
            if User.objects.filter(email=email).exists():
                return 'email has been used'
            user = User.objects.create_user(username=userName, email=email, password=password)
            user.save()
            return ''
        
        msg=check_register(registerUsername, registerEmail, registerPassword)
        if msg == '':
            return JsonResponse(data={'code':1})
        else:
            return JsonResponse(data={'code': -1, 'msg': msg})
    

def logout_view(request):
    logout(request=request)
    # logger.warning("")
    return render(request=request, template_name='user/login.html')