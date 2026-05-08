from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from core.permission import check_permission
import json
import logging

logger = logging.getLogger(__name__)


def login_view(request):
    if request.session.get('username') is not None:
        return HttpResponseRedirect('/index/')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            return JsonResponse({'msg': '用户名和密码不能为空', 'status': 0})

        user = authenticate(username=username, password=password)
        if user and user.is_active:
            auth_login(request, user)
            request.session['username'] = username
            return JsonResponse({'msg': '登录成功', 'status': 1})
        else:
            return JsonResponse({'msg': '用户名不存在或密码错误', 'status': 0})

    return render(request, 'login.html')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            return render(request, 'register.html', {'error': '用户名和密码不能为空'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': '用户已存在'})

        try:
            User.objects.create_user(username=username, password=password)
            return render(request, 'login.html', {'success': '注册成功，请登录'})
        except Exception as e:
            logger.error(f"注册失败: {e}")
            return render(request, 'register.html', {'error': '注册失败'})

    return render(request, 'register.html')


@login_required(login_url='/login/')
@check_permission
def index(request):
    return render(request, 'index.html', {"user": request.user})


def logout_view(request):
    auth_logout(request)
    return HttpResponseRedirect('/login/')


@login_required(login_url='/login/')
def editpassword(request):
    if request.method == "POST":
        username = request.user.username
        oldpass = request.POST.get('oldpass', '')
        newpass = request.POST.get('newpass', '')

        if not oldpass or not newpass:
            return JsonResponse({'msg': '密码不能为空', 'status': 0})

        user = authenticate(username=username, password=oldpass)
        if user:
            user.set_password(newpass)
            user.save()
            return JsonResponse({'msg': '修改成功', 'status': 1})
        else:
            return JsonResponse({'msg': '原密码错误', 'status': 0})

    return render(request, 'changepwd.html', {"user": request.user})


def get_navs(request):
    navs = {
        "contentManagement": [
            {
                "title": "应用管理",
                "icon": "&#xe653;",
                "href": "",
                "spread": "true",
                "children": [
                    {"title": "业务线信息", "icon": "", "href": "/cmdb/appdomain/", "spread": "true"},
                    {"title": "应用信息", "icon": "", "href": "/cmdb/appinfo/", "spread": "false"},
                    {"title": "机房信息", "icon": "", "href": "/cmdb/idc/", "spread": "true"},
                    {"title": "域名信息", "icon": "", "href": "/", "spread": "true"}
                ]
            },
            {
                "title": "资产管理",
                "icon": "&#xe65e;",
                "href": "",
                "spread": "true",
                "children": [
                    {"title": "物理机", "icon": "", "href": "/server/host/", "spread": "false"},
                    {"title": "虚拟机", "icon": "", "href": "/server/vm/", "spread": "false"}
                ]
            },
            {
                "title": "私有云管理",
                "icon": "&#xe609;",
                "href": "",
                "spread": "true",
                "children": [
                    {"title": "集群看版", "icon": "", "href": "/cloud/cluster/dashboard/", "spread": "false"},
                    {"title": "主机管理", "icon": "", "href": "/cloud/vm/index/", "spread": "false"}
                ]
            },
            {
                "title": "导航",
                "icon": "&#xe7ae;",
                "href": "/",
                "spread": "true",
            }
        ]
    }
    return JsonResponse(navs)
