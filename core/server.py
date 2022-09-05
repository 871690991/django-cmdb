

#coding=utf-8
from ast import Num
from email.headerregistry import Address
from logging import exception
from telnetlib import STATUS
from tokenize import group
from django.shortcuts import render,redirect
from core.models import *
from django.http import HttpResponse
import json
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from core.permission import check_permission

@login_required(login_url='/login')
@check_permission
def server(request):

        
    return render(request, 'cmdb/server.html')

@login_required(login_url='/login')
def server_info(request):
    
    dic={
    "code": 1,
    "msg": "",
    "count": 0,
    "data": [

    ]
  }
    search=request.GET.get("ip")
    currentPage = request.GET.get('page')
    limit = request.GET.get('limit')
    if search:
        idc_obj=Server_info.objects.filter(ip__contains=search)
        data=[]
        for i in idc_obj:
            data.append({"ip":i.ip,"managerip":i.managerip,"env":i.env.name,"sn":i.sn,"status":i.status.name})


        idc_obj2=Server_info.objects.filter(sn__contains=search)
        for i2 in idc_obj2:
            data.append({"ip":i2.ip,"managerip":i2.managerip,"env":i2.env.name,"sn":i2.sn,"status":i2.status.name})
        dic['data']=data
        dic['count']=idc_obj.count()+idc_obj2.count()
        dic['code']=0
        return HttpResponse(json.dumps(dic))


    aobj=Server_info.objects.all()
    data=[]
    for i in aobj:
        data.append({"ip":i.ip,"managerip":i.managerip,"env":i.env.name,"sn":i.sn,"status":i.status.name})
    paginator = Paginator(data, limit)
    dic['data']=paginator.get_page(currentPage).object_list
    dic['count']=aobj.count()
    dic['code']=0

    return HttpResponse(json.dumps(dic))

@login_required(login_url='/login')
@check_permission
def server_infoadd(request):
    if request.method == "POST":

        ip = request.POST.get('ip')
        hostname = request.POST.get('hostname')
        managerip = request.POST.get('managerip')
        status = request.POST.get('status')
        env = request.POST.get('env')
        app_info = request.POST.get('app_info')
        idc = request.POST.get('idc')
        brand = request.POST.get('brand')
        hardware_parameters = request.POST.get('hardware_parameters')
        rittal = request.POST.get('rittal')
        u_site = request.POST.get('u_site')
        sn = request.POST.get('sn')
        buy_time = request.POST.get('buy_time')
        expire_date = request.POST.get('expire_date')
        system = request.POST.get('system')

        try:

            status_name=Server_status.objects.get(id=int(status))
            env_name=Envs.objects.get(id=int(env))

            appname=App_info.objects.get(id=int(app_info))
            idcname=Idc_info.objects.get(id=int(idc))
            obj=Server_info.objects.create(ip=ip,hostname=hostname,managerip=managerip,status=status_name,env=env_name,app_info=appname,idc=idcname,brand=brand,hardware_parameters=hardware_parameters,rittal=rittal,u_site=u_site,sn=sn,buy_time=buy_time,expire_date=expire_date,system=system)
            if obj:
                return HttpResponse(json.dumps({'msg':'添加成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            print(e)
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

    else:
        env=[]
        aobj=Envs.objects.all()
        
        for i in aobj:
            env.append(i)

        status=[]
        obj=Server_status.objects.all()
        for s in obj:
            status.append(s)
        app=[]
        obj1=App_info.objects.all()
        for a in obj1:
            app.append(a)
        idc=[]
        obj2=Idc_info.objects.all()
        for id in obj2:
            idc.append(id)
        return render(request, 'cmdb/serveradd.html',{'env': env,'status':status,'app':app,'idc':idc})

@login_required(login_url='/login')
@check_permission
def server_infodel(request):
    if request.method == "POST":

        ip = request.POST.get('ip')
        dlist = request.POST.get('dlist')
        if dlist:
            for i in eval(dlist):
                
                try:
                    idc_obj=Server_info.objects.get(ip=i)
                    idc_obj.delete()
                except Exception as e:
                    print(e)
                    return HttpResponse(json.dumps({'msg':str(e),'status':0}))
        try:
            idc_obj=Server_info.objects.get(ip=ip)
            idc_obj.delete()
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'删除成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))



def host_info(request):
    


    return render(request, 'cmdb/serverinfo.html')

def serverhost_info(request):
    dic={
    "code": 1,
    "msg": "",
    "data": [

    ]

  }

    ip=request.GET.get("ip")
    obj=Server_info.objects.filter(ip=ip)
    data=[]
    for i in obj:
        data.append({"title":"业务ip","data":i.ip})
        data.append({"title":"主机名","data":i.hostname})
        data.append({"title":"管理ip","data":i.managerip})
        data.append({"title":"状态","data":i.status.name})

        data.append({"title":"环境","data":i.env.name})

        data.append({"title":"机型","data":i.brand})
        data.append({"title":"硬件配置","data":i.hardware_parameters})
        data.append({"title":"机柜","data":i.rittal})
        data.append({"title":"U位","data":i.u_site})
        data.append({"title":"sn序列号","data":i.sn})
        data.append({"title":"购买时间","data":str(i.buy_time)})
        data.append({"title":"过保时间","data":str(i.expire_date)})
        data.append({"title":"应用","data":i.app_info.enname})
        data.append({"title":"机房","data":i.idc.name})
        data.append({"title":"操作系统","data":i.system})

        dic["ip"]=i.ip
        dic["hostname"]=i.hostname
        dic["managerip"]=i.managerip
        dic["status"]=i.status.id
        dic["env"]=i.env.id
        dic["appname"]=i.app_info.id
        dic["idc"]=i.idc.id
        dic["brand"]=i.brand
        dic["hardware_parameters"]=i.hardware_parameters
        dic["rittal"]=i.rittal
        dic["u_site"]=i.u_site
        dic["sn"]=i.sn
        dic["buy_time"]=str(i.buy_time)
        dic["expire_date"]=str(i.expire_date)
        dic["system"]=i.system

    dic['data']=data
    dic['code']=0
    return HttpResponse(json.dumps(dic))

@login_required(login_url='/login')
@check_permission
def server_infoedit(request):
    if request.method == "POST":

        ip = request.POST.get('ip')
        hostname = request.POST.get('hostname')
        managerip = request.POST.get('managerip')
        status = request.POST.get('status')
        env = request.POST.get('env')
        app_info = request.POST.get('app_info')
        idc = request.POST.get('idc')
        brand = request.POST.get('brand')
        hardware_parameters = request.POST.get('hardware_parameters')
        rittal = request.POST.get('rittal')
        u_site = request.POST.get('u_site')
        sn = request.POST.get('sn')
        buy_time = request.POST.get('buy_time')
        expire_date = request.POST.get('expire_date')
        system = request.POST.get('system')

        try:
            status_name=Server_status.objects.get(id=int(status))
            env_name=Envs.objects.get(id=int(env))

            appname=App_info.objects.get(id=int(app_info))
            idcname=Idc_info.objects.get(id=int(idc))
            idc_obj=Server_info.objects.get(ip=ip)
            idc_obj.hostname=hostname
            idc_obj.managerip=managerip
            idc_obj.status=status_name
            idc_obj.env=env_name
            idc_obj.app_info=appname
            idc_obj.idc=idcname

            idc_obj.brand=brand
            idc_obj.hardware_parameters=hardware_parameters
            idc_obj.rittal=rittal
            idc_obj.u_site=u_site
            idc_obj.sn=sn
            idc_obj.system=system

            idc_obj.buy_time=buy_time

            idc_obj.expire_date=expire_date


            idc_obj.save()
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'修改成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

    else:
        env=[]
        aobj=Envs.objects.all()
        for i in aobj:
            env.append(i)

        status=[]
        obj=Server_status.objects.all()
        for s in obj:
            status.append(s)
        app=[]
        obj1=App_info.objects.all()
        for a in obj1:
            app.append(a)
        idc=[]
        obj2=Idc_info.objects.all()
        for id in obj2:
            idc.append(id)
        return render(request, 'cmdb/serveredit.html',{'env': env,'status':status,'app':app,'idc':idc})



@check_permission
def vm(request):
    
        
    return render(request, 'cmdb/vm.html')

@login_required(login_url='/login')
def vm_info(request):
        
    dic={
    "code": 1,
    "msg": "",
    "count": 0,
    "data": [

    ]
  }
    search=request.GET.get("ip")
    currentPage = request.GET.get('page')
    limit = request.GET.get('limit')
    if search:
        idc_obj=Vm_info.objects.filter(ip__contains=search)
        data=[]
        for i in idc_obj:
            data.append({"ip":i.ip,"hostname":i.hostname,"env":i.env.name,"status":i.status.name,"app_info":i.app_info.enname})
        # idc_obj2=Vm_info.objects.filter(server__contains=search)
        # for i2 in idc_obj2:
        #     data.append({"ip":i2.ip,"hostname":i2.hostname,"env":i2.env.name,"status":i2.status.name,"app_info":i2.app_info.enname})
        dic['data']=data
        dic['count']=idc_obj.count()
        dic['code']=0
        return HttpResponse(json.dumps(dic))


    aobj=Vm_info.objects.all()
    data=[]
    for i in aobj:
        data.append({"ip":i.ip,"hostname":i.hostname,"env":i.env.name,"status":i.status.name,"app_info":i.app_info.enname})
    paginator = Paginator(data, limit)
    dic['data']=paginator.get_page(currentPage).object_list
    dic['count']=aobj.count()
    dic['code']=0

    return HttpResponse(json.dumps(dic))



@login_required(login_url='/login')
@check_permission
def vm_infoadd(request):
    if request.method == "POST":

        ip = request.POST.get('ip')
        hostname = request.POST.get('hostname')
        status = request.POST.get('status')
        env = request.POST.get('env')
        app_info = request.POST.get('app_info')
        idc = request.POST.get('idc')
        system = request.POST.get('system')
        hardware_parameters = request.POST.get('hardware_parameters')
        server = request.POST.get('server')

        try:

            status_name=Server_status.objects.get(id=int(status))
            env_name=Envs.objects.get(id=int(env))

            appname=App_info.objects.get(id=int(app_info))
            idcname=Idc_info.objects.get(id=int(idc))

            serverip=Server_info.objects.get(id=int(server))

            obj=Vm_info.objects.create(ip=ip,hostname=hostname,status=status_name,env=env_name,app_info=appname,idc=idcname,hardware_parameters=hardware_parameters,server=serverip,system=system)
            if obj:
                return HttpResponse(json.dumps({'msg':'添加成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            print(e)
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

    else:
        env=[]
        aobj=Envs.objects.all()
        
        for i in aobj:
            env.append(i)

        status=[]
        obj=Server_status.objects.all()
        for s in obj:
            status.append(s)
        app=[]
        obj1=App_info.objects.all()
        for a in obj1:
            app.append(a)
        idc=[]
        obj2=Idc_info.objects.all()
        for id in obj2:
            idc.append(id)

        server=[]
        obj3=Server_info.objects.all()
        for id3 in obj3:
            server.append(id3)        
        return render(request, 'cmdb/vmadd.html',{'env': env,'status':status,'app':app,'idc':idc,'server':server})

@login_required(login_url='/login')
@check_permission
def vm_infodel(request):
    if request.method == "POST":

        ip = request.POST.get('ip')
        dlist = request.POST.get('dlist')
        if dlist:
            for i in eval(dlist):
                
                try:
                    idc_obj=Vm_info.objects.get(ip=i)
                    idc_obj.delete()
                except Exception as e:
                    print(e)
                    return HttpResponse(json.dumps({'msg':str(e),'status':0}))
        try:
            idc_obj=Vm_info.objects.get(ip=ip)
            idc_obj.delete()
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'删除成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

def vmhost_info(request):
    dic={
    "code": 1,
    "msg": "",
    "data": [

    ]

  }

    ip=request.GET.get("ip")
    obj=Vm_info.objects.filter(ip=ip)
    data=[]
    for i in obj:
        data.append({"title":"ip","data":i.ip})
        data.append({"title":"主机名","data":i.hostname})
        data.append({"title":"状态","data":i.status.name})
        data.append({"title":"环境","data":i.env.name})
        data.append({"title":"操作系统","data":i.system})
        data.append({"title":"硬件配置","data":i.hardware_parameters})
        data.append({"title":"物理机","data":i.server.ip})
        data.append({"title":"应用","data":i.app_info.enname})
        data.append({"title":"机房","data":i.idc.name})
        
        dic["ip"]=i.ip
        dic["hostname"]=i.hostname
        dic["status"]=i.status.id
        dic["env"]=i.env.id
        dic["appname"]=i.app_info.id
        dic["idc"]=i.idc.id
        dic["system"]=i.system
        dic["hardware_parameters"]=i.hardware_parameters
        dic["server"]=i.server.id


    dic['data']=data
    dic['code']=0
    return HttpResponse(json.dumps(dic))

@login_required(login_url='/login')
@check_permission
def vm_infoedit(request):
    if request.method == "POST":

        ip = request.POST.get('ip')
        hostname = request.POST.get('hostname')
        status = request.POST.get('status')
        env = request.POST.get('env')
        app_info = request.POST.get('app_info')
        idc = request.POST.get('idc')
        system = request.POST.get('system')
        hardware_parameters = request.POST.get('hardware_parameters')
        server = request.POST.get('server')
        try:
            status_name=Server_status.objects.get(id=int(status))
            env_name=Envs.objects.get(id=int(env))

            appname=App_info.objects.get(id=int(app_info))
            idcname=Idc_info.objects.get(id=int(idc))

            serverip=Server_info.objects.get(id=int(server))

            idc_obj=Vm_info.objects.get(ip=ip)
            idc_obj.hostname=hostname
            idc_obj.server=serverip
            idc_obj.status=status_name
            idc_obj.env=env_name
            idc_obj.app_info=appname
            idc_obj.idc=idcname

            idc_obj.system=system
            idc_obj.hardware_parameters=hardware_parameters



            idc_obj.save()
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'修改成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

    else:
        env=[]
        aobj=Envs.objects.all()
        for i in aobj:
            env.append(i)

        status=[]
        obj=Server_status.objects.all()
        for s in obj:
            status.append(s)
        app=[]
        obj1=App_info.objects.all()
        for a in obj1:
            app.append(a)
        idc=[]
        obj2=Idc_info.objects.all()
        for id in obj2:
            idc.append(id)
        server=[]
        obj3=Server_info.objects.all()
        for id3 in obj3:
            server.append(id3)        
        return render(request, 'cmdb/vmedit.html',{'env': env,'status':status,'app':app,'idc':idc,'server':server})



def getvm_info(request):
    


    return render(request, 'cmdb/vminfo.html')

def vm_list(request):
        
    dic={
    "code": 1,
    "msg": "",
    "count": 0,
    "data": [

    ]
  }
    search=request.GET.get("ip")
    serverip=Server_info.objects.get(ip=search)

    if search:
        idc_obj=Vm_info.objects.filter(server=serverip)
        data=[]
        for i in idc_obj:
            data.append({"ip":i.ip,"hostname":i.hostname,"env":i.env.name,"status":i.status.name,"app_info":i.app_info.enname})
        # idc_obj2=Vm_info.objects.filter(server__contains=search)
        # for i2 in idc_obj2:
        #     data.append({"ip":i2.ip,"hostname":i2.hostname,"env":i2.env.name,"status":i2.status.name,"app_info":i2.app_info.enname})
        dic['data']=data
        dic['count']=idc_obj.count()
        dic['code']=0
        return HttpResponse(json.dumps(dic))


