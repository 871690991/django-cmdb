from django.shortcuts import render
from . import models
from django.db.models import Q
from django.urls import resolve   #此方法可以将url地址转换成url的name
from django.contrib.auth.models import Group

def perm_check(request):
    url_obj = resolve(request.path_info)
    url_name = url_obj.route
    perm_name = ''
    #权限必须和urlname配合使得
    if url_name:
        # #获取请求方法，和请求参数
        # url_method, url_args = request.method, request.GET
        # url_args_list = []
        # #将各个参数的值用逗号隔开组成字符串，因为数据库中是这样存的
        # for i in url_args:
        #     url_args_list.append(str(url_args[i]))
        # url_args_list = ','.join(url_args_list)
        #操作数据库

        usergroup=Group.objects.get(user=request.user).name
        if usergroup == "admin":
            return True

        get_perm = models.myPermission.objects.filter(url__contains=url_name)
        if get_perm:
            for i in get_perm:
                perm_name = i.name
                perm_str =  "core."+perm_name
                if request.user.has_perm(perm_str):
                    return True
            else:
                return False
        else:
            return False
    else:
        return False   #没有权限设置，默认不放过


def check_permission(fun):    #定义一个装饰器，在views中应用
    def wapper(request, *args, **kwargs):
        if perm_check(request, *args, **kwargs):  #调用上面的权限验证方法
            return fun(request, *args, **kwargs)
        return render(request, '403.html', locals())
    return wapper