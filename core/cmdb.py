#coding=utf-8
from ast import Num
from email.headerregistry import Address
from logging import exception
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
def idc(request):

        
    return render(request, 'cmdb/idc.html')

@login_required(login_url='/login')
def idc_info(request):
    

    dic={
    "code": 0,
    "msg": "",
    "count": 0,
    "data": [

    ]
  }
    search=request.GET.get("idcName")
    if search:
        idc_obj=Idc_info.objects.filter(name=search)
        data=[]
        for i in idc_obj:
            data.append({"idcName":i.name,"idcNum":i.num,"idcAddress":i.address})
        dic['data']=data
        dic['count']=idc_obj.count()
        return HttpResponse(json.dumps(dic))


    idc_obj=Idc_info.objects.all()
    data=[]
    for i in idc_obj:
        data.append({"idcName":i.name,"idcNum":i.num,"idcAddress":i.address})
    dic['data']=data
    dic['count']=idc_obj.count()
    return HttpResponse(json.dumps(dic))


@login_required(login_url='/login')
@check_permission
def idcadd(request):
    if request.method == "POST":

        idcname = request.POST.get('idcname')
        idcnum = request.POST.get('idcnum')
        idcaddress = request.POST.get('idcaddress')
        try:
            idc_obj=Idc_info.objects.create(name=idcname,num=idcnum,address=idcaddress)
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'添加成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

    else:
        return render(request, 'cmdb/idcadd.html')

@login_required(login_url='/login')
@check_permission
def idcedit(request):
    if request.method == "POST":

        idcname = request.POST.get('idcname')
        idcnum = request.POST.get('idcnum')
        idcaddress = request.POST.get('idcaddress')
        try:
            idc_obj=Idc_info.objects.get(name=idcname)
            idc_obj.num=idcnum
            idc_obj.address=idcaddress
            idc_obj.save()
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'修改成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

    else:
        return render(request, 'cmdb/idcedit.html')

@login_required(login_url='/login')
@check_permission
def idcdel(request):
    if request.method == "POST":

        idcname = request.POST.get('idcname')
        idclist = request.POST.get('idclist')
        if idclist:
            for idc in eval(idclist):
                try:
                    idc_obj=Idc_info.objects.get(name=idc)
                    idc_obj.delete()
                except Exception as e:
                    return HttpResponse(json.dumps({'msg':str(e),'status':0}))
        try:
            idc_obj=Idc_info.objects.get(name=idcname)

            idc_obj.delete()
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'删除成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))






def get_groups(request):
    # dic={}
    # aobj=devgroup_name.objects.all()
    # data=[]
    # for i in aobj:
    #     data.append(str(i))

    # dic['data']=data
    # return HttpResponse(json.dumps(dic,ensure_ascii=False))
    name=request.GET.get("name")

    obj=devgroup_name.objects.get(name=name)
    return HttpResponse(json.dumps({"id":obj.id}))

def get_appdomain(request):
    # dic={}
    # aobj=devgroup_name.objects.all()
    # data=[]
    # for i in aobj:
    #     data.append(str(i))

    # dic['data']=data
    # return HttpResponse(json.dumps(dic,ensure_ascii=False))
    name=request.GET.get("name")

    obj=Appdomain_info.objects.get(enname=name)
    return HttpResponse(json.dumps({"id":obj.id}))


@login_required(login_url='/login')
@check_permission
def appdomain(request):
    
        
    return render(request, 'cmdb/appdomain.html')

@login_required(login_url='/login')
def appdomain_info(request):

    dic={
    "code": 0,
    "msg": "",
    "count": 0,
    "data": [

    ]
  }
    search=request.GET.get("enname")
    currentPage = request.GET.get('page')
    limit = request.GET.get('limit')
    if search:
        idc_obj=Appdomain_info.objects.filter(enname__contains=search)
        data=[]
        for i in idc_obj:
            data.append({"enname":i.enname,"cnname":i.cnname,"group":str(i.group),"manager":i.manager})
        dic['data']=data
        dic['count']=idc_obj.count()
        return HttpResponse(json.dumps(dic))


    aobj=Appdomain_info.objects.all()
    data=[]
    for i in aobj:
        data.append({"enname":i.enname,"cnname":i.cnname,"group":str(i.group),"manager":i.manager})
    paginator = Paginator(data, limit)
    dic['data']=paginator.get_page(currentPage).object_list
    dic['count']=aobj.count()
    return HttpResponse(json.dumps(dic))

@login_required(login_url='/login')
@check_permission
def appdomainadd(request):
    if request.method == "POST":

        enname = request.POST.get('enname')
        cnname = request.POST.get('cnname')
        group = request.POST.get('group')
        manager = request.POST.get('manager')

        try:
            get_group=devgroup_name.objects.get(id=int(group))
            obj=Appdomain_info.objects.create(enname=enname,cnname=cnname,group=get_group,manager=manager)
            if obj:
                return HttpResponse(json.dumps({'msg':'添加成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

    else:
        data=[]
        aobj=devgroup_name.objects.all()
        for i in aobj:
            data.append(i)
        return render(request, 'cmdb/appdomainadd.html',{'group': data})
@login_required(login_url='/login')
@check_permission
def appdomaindel(request):
    if request.method == "POST":

        name = request.POST.get('name')
        dlist = request.POST.get('dlist')
        if dlist:
            for i in eval(dlist):
                
                try:
                    idc_obj=Appdomain_info.objects.get(enname=i)
                    idc_obj.delete()
                except Exception as e:
                    return HttpResponse(json.dumps({'msg':str(e),'status':0}))
        try:
            idc_obj=Appdomain_info.objects.get(enname=name)
            idc_obj.delete()
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'删除成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

@login_required(login_url='/login')
@check_permission
def appdomainedit(request):
    if request.method == "POST":

        enname = request.POST.get('enname')
        cnname = request.POST.get('cnname')
        group = request.POST.get('group')
        manager = request.POST.get('manager')
        try:
            get_group=devgroup_name.objects.get(id=int(group))

            idc_obj=Appdomain_info.objects.get(enname=enname)
            idc_obj.cnname=cnname
            idc_obj.group=get_group
            idc_obj.manager=manager
            idc_obj.save()
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'修改成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

    else:
        data=[]
        aobj=devgroup_name.objects.all()
        for i in aobj:
            data.append(i)
        return render(request, 'cmdb/appdomainedit.html',{'group': data})







def app_infodata(request):
    
    dic={
    "code": 1,
    "msg": "",
    "count": 0,
    "data": [

    ]
  }
    search=request.GET.get("enname")
    currentPage = request.GET.get('page')
    limit = request.GET.get('limit')
    if search:
        idc_obj=App_info.objects.filter(enname__contains=search)
        data=[]
        for i in idc_obj:
            data.append({"enname":i.enname,"cnname":i.cnname,"appdomain_info":str(i.appdomain_info),"manager":i.manager})
        dic['data']=data
        dic['count']=idc_obj.count()
        dic['code']=0
        return HttpResponse(json.dumps(dic))


    aobj=App_info.objects.all()
    data=[]
    for i in aobj:
        data.append({"enname":i.enname,"cnname":i.cnname,"appdomain_info":str(i.appdomain_info),"manager":i.manager})
    paginator = Paginator(data, limit)
    dic['data']=paginator.get_page(currentPage).object_list
    dic['count']=aobj.count()
    dic['code']=0

    return HttpResponse(json.dumps(dic))
@check_permission
def app_info(request):
    
        
    return render(request, 'cmdb/appinfo.html')

@login_required(login_url='/login')
@check_permission
def app_infoadd(request):
    if request.method == "POST":

        enname = request.POST.get('enname')
        cnname = request.POST.get('cnname')
        appdomain_info = request.POST.get('appdomain_info')
        manager = request.POST.get('manager')

        try:
            get_group=Appdomain_info.objects.get(id=int(appdomain_info))
            obj=App_info.objects.create(enname=enname,cnname=cnname,appdomain_info=get_group,manager=manager)
            if obj:
                return HttpResponse(json.dumps({'msg':'添加成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

    else:
        data=[]
        aobj=Appdomain_info.objects.all()
        
        for i in aobj:
            data.append(i)
        return render(request, 'cmdb/appinfoadd.html',{'group': data})
@login_required(login_url='/login')
@check_permission
def appinfodel(request):
    if request.method == "POST":

        name = request.POST.get('name')
        dlist = request.POST.get('dlist')
        if dlist:
            for i in eval(dlist):
                
                try:
                    idc_obj=App_info.objects.get(enname=i)
                    idc_obj.delete()
                except Exception as e:
                    return HttpResponse(json.dumps({'msg':str(e),'status':0}))
        try:
            idc_obj=App_info.objects.get(enname=name)
            idc_obj.delete()
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'删除成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

@login_required(login_url='/login')
@check_permission
def appinfoedit(request):
    if request.method == "POST":

        enname = request.POST.get('enname')
        cnname = request.POST.get('cnname')
        appdomain_info = request.POST.get('appdomain_info')
        manager = request.POST.get('manager')
        try:
            get_group=Appdomain_info.objects.get(id=int(appdomain_info))
            idc_obj=App_info.objects.get(enname=enname)
            idc_obj.cnname=cnname
            idc_obj.appdomain_info=get_group
            idc_obj.manager=manager
            idc_obj.save()
            if idc_obj:
                return HttpResponse(json.dumps({'msg':'修改成功','status':1}))
            else:
                return HttpResponse(json.dumps({'msg':'err','status':0}))
        except Exception as e:
            return HttpResponse(json.dumps({'msg':str(e),'status':0}))

    else:
        data=[]
        aobj=Appdomain_info.objects.all()
        for i in aobj:
            data.append(i)
        return render(request, 'cmdb/appinfoedit.html',{'group': data})



def appname_infodata(request):
    

    data=[]
    appname=request.GET.get("appname")
    getappnameid=App_info.objects.get(enname=appname)
    get_serverinfo=Server_info.objects.filter(app_info=getappnameid.id)
    for s in get_serverinfo:
        dic={}
        dic["env"]=s.env.name
        dic["ip"]=s.ip
        dic["status"]=s.status.name
        dic["type"]="物理机"
        data.append(dic)


    get_vminfo=Vm_info.objects.filter(app_info=getappnameid.id)
    for v in get_vminfo:
        dic={}
        dic["env"]=v.env.name
        dic["ip"]=v.ip
        dic["status"]=v.status.name
        dic["type"]="虚拟机"
        data.append(dic)



  #appnameinfo.html
    return render(request, 'cmdb/appnameinfo.html',{"serverinfo":data})

