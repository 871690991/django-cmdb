from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
import json
from django.http import HttpResponseRedirect, JsonResponse,HttpResponsePermanentRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from core.permission import check_permission


# Create your views here.
from django.contrib.auth.models import User

# def loginauth(request):
#     if request.method=='POST':
#         print("aaa")
#         ret = {"status":0,"msg":"账号密码错误"}
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user=authenticate(username=username,password=password)
#         # return HttpResponse({'res':0})
#         if user is not None:

#             login(request,user)
#             ret['status']=1
#             ret['msg']="登录成功"

#             return HttpResponse(json.dumps(ret))
#         print("nono")
#         return HttpResponse(json.dumps(ret))


#     return render(request, 'login.html')


def login(request):
    if request.session.get('username') is not None:
        print("a1")
        # return HttpResponse(json.dumps({'msg':'','status':1}))

        return HttpResponseRedirect('/index/', {"user": request.user})
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            request.session['username'] = username
            return HttpResponse(json.dumps({'msg':'','status':1}))

            return HttpResponseRedirect('/index/', {"user": request.user})
        else:
            if request.method == "POST":
                return HttpResponse(json.dumps({'msg':'用户名不错存在，或者密码错误！','status':0}))
                # return render(request, 'login.html', {"login_error_info": "用户名不错存在，或者密码错误！"})
            else:
                return render(request, 'login.html')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username):
            msg="用户已存在"
        else:
            User.objects.create_user(username=username,password=password)
            User.save
            msg="注册成功"
        return render(request,'login.html',locals())
    return render(request,'register.html')

@login_required(login_url='/login')
@check_permission
def index(request):
    return render(request, 'index.html', {"user": request.user})




def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login')



@login_required(login_url='/login')
def editpassword(request):

    if request.method == "POST":
        username = request.POST.get('username')
        oldpass = request.POST.get('oldpass')
        newpass = request.POST.get('newpass')
        user=authenticate(username=username, password=oldpass)
        print(username,oldpass,newpass)
        print(user)

        if  user:
            user.set_password(newpass)
            user.save()
            return HttpResponse(json.dumps({'msg':'修改成功','status':1}))

        else:
            return HttpResponse(json.dumps({'msg':'密码错误！','status':0}))

    
    return render(request, 'changepwd.html', {"user": request.user})


def get_navs(request):


    a={
	"contentManagement": [
		
		{
			"title": "应用管理",
			"icon": "&#xe653;",
			"href": "",
			"spread": "true",
			"children": [{
				"title": "业务线信息",
				"icon": "",
				"href": "/cmdb/appdomain/",
				"spread": "true"
			},{
				"title": "应用信息",
				"icon": "",
				"href": "/cmdb/appinfo/",
				"spread": "false"
			},{
				"title": "机房信息",
				"icon": "",
				"href": "/cmdb/idc/",
				"spread": "true"
			},{
				"title": "域名信息",
				"icon": "",
				"href": "/",
				"spread": "true"
			}
		
		]
		},
		
		{
			"title": "资产管理",
			"icon": "&#xe65e;",
			"href": "",
			"spread": "true",
			"children": [{
				"title": "物理机",
				"icon": "",
				"href": "/server/host/",
				"spread": "false"
			},
			{
			"title": "虚拟机",
			"icon": "",
			"href": "/server/vm/",
			"spread": "false"
		}
		
		]
		},
		{
			"title": "私有云管理",
			"icon": "&#xe609;",
			"href": "",
			"spread": "true",
			"children": [{
				"title": "集群看版",
				"icon": "",
				"href": "/cloud/cluster/dashboard/",
				"spread": "false"
			},{
				"title": "主机管理",
				"icon": "",
				"href": "/cloud/vm/index/",
				"spread": "false"
			}
		
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
    return HttpResponse(json.dumps(a))



