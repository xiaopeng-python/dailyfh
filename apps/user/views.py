from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from user.models import User
from django.views.generic import View
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.http import HttpResponse
from django.core.mail import send_mail
import re

# Create your views here.

def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        # 获取客户端传入注册信息
        username = request.POST.get("user_name")
        pwd = request.POST.get("pwd")
        email = request.POST.get("email")
        cpwd = request.POST.get("cpwd")
        allow = request.POST.get("allow")

        # 注册信息校验
        if not all([username, pwd, email]):
            return render(request, 'register', {'errmsg': "数据不完整"})

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register', {'errmsg': "邮箱格式不正确"})

        if allow != 'on':
            return render(request, 'register', {'errmsg': "请同意协议"})

        if pwd != cpwd:
            return render(request, 'register', {'errmsg': "两次输入的密码不一致"})

        # 用户注册
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            return render(request, 'register.html', {"errmsg": "用户已存在"})

        user = User.objects.create_user(username, pwd, email)

        return redirect(reverse('goods:index'))


def register_handle(request):
    # 获取客户端传入注册信息
    username = request.POST.get("user_name")
    pwd = request.POST.get("pwd")
    email = request.POST.get("email")
    cpwd = request.POST.get("cpwd")
    allow = request.POST.get("allow")

    # 注册信息校验
    if not all([username, pwd, email]):
        return render(request, 'register', {'errmsg': "数据不完整"})

    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'register', {'errmsg': "邮箱格式不正确"})

    if allow != 'on':
        return render(request, 'register', {'errmsg': "请同意协议"})

    if pwd != cpwd:
        return render(request, 'register', {'errmsg': "两次输入的密码不一致"})

    # 用户注册
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    if user:
        return  render(request, 'register.html', {"errmsg": "用户已存在"})

    user = User.objects.create_user(username, pwd, email)

    return redirect(reverse('goods:index'))


class RegisterView(View):
    '''注册'''
    def get(self, request):
        return render(request, 'register.html')

    """注册助理"""
    def post(self, request):
        # 获取客户端传入注册信息
        username = request.POST.get("user_name")
        pwd = request.POST.get("pwd")
        email = request.POST.get("email")
        print(email)
        cpwd = request.POST.get("cpwd")
        allow = request.POST.get("allow")

        # 注册信息校验
        if not all([username, pwd, email]):
            return render(request, 'register', {'errmsg': "数据不完整"})

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register', {'errmsg': "邮箱格式不正确"})

        if allow != 'on':
            return render(request, 'register', {'errmsg': "请同意协议"})

        if pwd != cpwd:
            return render(request, 'register', {'errmsg': "两次输入的密码不一致"})

        # 用户注册
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            return render(request, 'register.html', {"errmsg": "用户已存在"})

        user = User.objects.create_user(username, email, pwd)
        user.is_active = 0
        user.save()

        # 发送激活的邮件，包含激活链接：http://x.x.x.x:port/user/active/3
        # 激活链接中需要包含用户的身份信息，并且要把身份信息进行加密

        # 加密用户的身份信息，生产激活token
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode('utf-8')

        # 邮件发送
        subject = "欢迎登录商城"
        message = ""
        sender = settings.EMAIL_FROM
        receiver = [email]
        html_message = '<h1>%s, 欢迎您成为本商城注册会员</h1>请点击下面的链接进行用户激活<br/><a href="http://10.77.2.223:9999/user/active/%s">http://10.77.2.223:9999/user/active/%s</a>'%(username,token,token)
        send_mail(subject, message, sender, receiver, html_message=html_message)


        return redirect(reverse('goods:index'))

class ActiveView(View):
    def get(self, request, token):
        """用户激活"""
        # 进行解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            # 获取用户id
            info = serializer.loads(token)

            # 获取用户信息
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return  redirect(reverse('user:login'))
        except SignatureExpired as sig:
            # 实际项目中应该让其点击发送激活邮件
            return HttpResponse("激活链接过去")




class LoginView(View):
    """登录"""
    def get(self,request):
        return render(request, 'login.html')

