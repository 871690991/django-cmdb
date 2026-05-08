import json
import logging
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from core.permission import check_permission
from core.models import Idc_info, devgroup_name, Appdomain_info, App_info, Server_info, Vm_info

logger = logging.getLogger(__name__)


@login_required(login_url='/login/')
@check_permission
def idc(request):
    return render(request, 'cmdb/idc.html')


@login_required(login_url='/login/')
def idc_info(request):
    dic = {
        "code": 0,
        "msg": "",
        "count": 0,
        "data": []
    }
    search = request.GET.get("idcName", "").strip()

    if search:
        idc_obj = Idc_info.objects.filter(name=search)
        data = [{
            "idcName": i.name,
            "idcNum": i.num,
            "idcAddress": i.address
        } for i in idc_obj]
        dic['data'] = data
        dic['count'] = idc_obj.count()
        return HttpResponse(json.dumps(dic))

    idc_obj = Idc_info.objects.all()
    data = [{
        "idcName": i.name,
        "idcNum": i.num,
        "idcAddress": i.address
    } for i in idc_obj]
    dic['data'] = data
    dic['count'] = idc_obj.count()
    return HttpResponse(json.dumps(dic))


@login_required(login_url='/login/')
@check_permission
def idcadd(request):
    if request.method == "POST":
        idcname = request.POST.get('idcname', '').strip()
        idcnum = request.POST.get('idcnum', '').strip()
        idcaddress = request.POST.get('idcaddress', '').strip()

        try:
            idc_obj = Idc_info.objects.create(name=idcname, num=idcnum, address=idcaddress)
            if idc_obj:
                return HttpResponse(json.dumps({'msg': '添加成功', 'status': 1}))
            else:
                return HttpResponse(json.dumps({'msg': 'err', 'status': 0}))
        except Exception as e:
            logger.error(f"添加机房失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))

    return render(request, 'cmdb/idcadd.html')


@login_required(login_url='/login/')
@check_permission
def idcedit(request):
    if request.method == "POST":
        idcname = request.POST.get('idcname', '').strip()
        idcnum = request.POST.get('idcnum', '').strip()
        idcaddress = request.POST.get('idcaddress', '').strip()

        try:
            idc_obj = Idc_info.objects.get(name=idcname)
            idc_obj.num = idcnum
            idc_obj.address = idcaddress
            idc_obj.save()
            return HttpResponse(json.dumps({'msg': '修改成功', 'status': 1}))
        except Idc_info.DoesNotExist:
            return HttpResponse(json.dumps({'msg': '机房不存在', 'status': 0}))
        except Exception as e:
            logger.error(f"修改机房失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))

    return render(request, 'cmdb/idcedit.html')


@login_required(login_url='/login/')
@check_permission
def idcdel(request):
    if request.method == "POST":
        idcname = request.POST.get('idcname', '').strip()
        idclist = request.POST.get('idclist', '').strip()

        try:
            deleted_count = 0
            if idclist:
                name_list = [x.strip() for x in idclist.strip('[]').replace('"', '').split(',') if x.strip()]
                for name in name_list:
                    try:
                        idc_obj = Idc_info.objects.get(name=name)
                        idc_obj.delete()
                        deleted_count += 1
                    except Idc_info.DoesNotExist:
                        continue

            if idcname:
                idc_obj = Idc_info.objects.get(name=idcname)
                idc_obj.delete()
                deleted_count += 1

            return HttpResponse(json.dumps({'msg': f'删除成功({deleted_count})', 'status': 1}))
        except Idc_info.DoesNotExist:
            return HttpResponse(json.dumps({'msg': '机房不存在', 'status': 0}))
        except Exception as e:
            logger.error(f"删除机房失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))


def get_groups(request):
    name = request.GET.get("name", "").strip()
    if not name:
        return HttpResponse(json.dumps({"error": "name required"}))

    try:
        obj = devgroup_name.objects.get(name=name)
        return HttpResponse(json.dumps({"id": obj.id}))
    except devgroup_name.DoesNotExist:
        return HttpResponse(json.dumps({"error": "group not found"}), status=404)


def get_appdomain(request):
    name = request.GET.get("name", "").strip()
    if not name:
        return HttpResponse(json.dumps({"error": "name required"}))

    try:
        obj = Appdomain_info.objects.get(enname=name)
        return HttpResponse(json.dumps({"id": obj.id}))
    except Appdomain_info.DoesNotExist:
        return HttpResponse(json.dumps({"error": "appdomain not found"}), status=404)


@login_required(login_url='/login/')
@check_permission
def appdomain(request):
    return render(request, 'cmdb/appdomain.html')


@login_required(login_url='/login/')
def appdomain_info(request):
    dic = {
        "code": 0,
        "msg": "",
        "count": 0,
        "data": []
    }
    search = request.GET.get("enname", "").strip()
    current_page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)

    try:
        limit = int(limit)
        current_page = int(current_page)
    except (ValueError, TypeError):
        limit = 10
        current_page = 1

    if search:
        idc_obj = Appdomain_info.objects.filter(enname__contains=search)
        data = [{
            "enname": i.enname,
            "cnname": i.cnname,
            "group": str(i.group),
            "manager": i.manager
        } for i in idc_obj]
        dic['data'] = data
        dic['count'] = idc_obj.count()
        return HttpResponse(json.dumps(dic))

    aobj = Appdomain_info.objects.all()
    data = [{
        "enname": i.enname,
        "cnname": i.cnname,
        "group": str(i.group),
        "manager": i.manager
    } for i in aobj]

    paginator = Paginator(data, limit)
    dic['data'] = list(paginator.get_page(current_page).object_list)
    dic['count'] = aobj.count()
    return HttpResponse(json.dumps(dic))


@login_required(login_url='/login/')
@check_permission
def appdomainadd(request):
    if request.method == "POST":
        enname = request.POST.get('enname', '').strip()
        cnname = request.POST.get('cnname', '').strip()
        group_id = request.POST.get('group')
        manager = request.POST.get('manager', '').strip()

        try:
            get_group = devgroup_name.objects.get(id=int(group_id))
            obj = Appdomain_info.objects.create(
                enname=enname, cnname=cnname,
                group=get_group, manager=manager
            )
            if obj:
                return HttpResponse(json.dumps({'msg': '添加成功', 'status': 1}))
            else:
                return HttpResponse(json.dumps({'msg': 'err', 'status': 0}))
        except (ValueError, devgroup_name.DoesNotExist):
            return HttpResponse(json.dumps({'msg': '数据无效', 'status': 0}))
        except Exception as e:
            logger.error(f"添加业务线失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))

    data = list(devgroup_name.objects.all())
    return render(request, 'cmdb/appdomainadd.html', {'group': data})


@login_required(login_url='/login/')
@check_permission
def appdomaindel(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        dlist = request.POST.get('dlist', '').strip()

        try:
            deleted_count = 0
            if dlist:
                name_list = [x.strip() for x in dlist.strip('[]').replace('"', '').split(',') if x.strip()]
                for n in name_list:
                    try:
                        idc_obj = Appdomain_info.objects.get(enname=n)
                        idc_obj.delete()
                        deleted_count += 1
                    except Appdomain_info.DoesNotExist:
                        continue

            if name:
                idc_obj = Appdomain_info.objects.get(enname=name)
                idc_obj.delete()
                deleted_count += 1

            return HttpResponse(json.dumps({'msg': f'删除成功({deleted_count})', 'status': 1}))
        except Appdomain_info.DoesNotExist:
            return HttpResponse(json.dumps({'msg': '业务线不存在', 'status': 0}))
        except Exception as e:
            logger.error(f"删除业务线失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))


@login_required(login_url='/login/')
@check_permission
def appdomainedit(request):
    if request.method == "POST":
        enname = request.POST.get('enname', '').strip()
        cnname = request.POST.get('cnname', '').strip()
        group_id = request.POST.get('group')
        manager = request.POST.get('manager', '').strip()

        try:
            get_group = devgroup_name.objects.get(id=int(group_id))
            idc_obj = Appdomain_info.objects.get(enname=enname)
            idc_obj.cnname = cnname
            idc_obj.group = get_group
            idc_obj.manager = manager
            idc_obj.save()
            return HttpResponse(json.dumps({'msg': '修改成功', 'status': 1}))
        except (ValueError, Appdomain_info.DoesNotExist, devgroup_name.DoesNotExist):
            return HttpResponse(json.dumps({'msg': '数据无效', 'status': 0}))
        except Exception as e:
            logger.error(f"修改业务线失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))

    data = list(devgroup_name.objects.all())
    return render(request, 'cmdb/appdomainedit.html', {'group': data})


@login_required(login_url='/login/')
def app_infodata(request):
    dic = {
        "code": 1,
        "msg": "",
        "count": 0,
        "data": []
    }
    search = request.GET.get("enname", "").strip()
    current_page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)

    try:
        limit = int(limit)
        current_page = int(current_page)
    except (ValueError, TypeError):
        limit = 10
        current_page = 1

    if search:
        idc_obj = App_info.objects.filter(enname__contains=search)
        data = [{
            "enname": i.enname,
            "cnname": i.cnname,
            "appdomain_info": str(i.appdomain_info),
            "manager": i.manager
        } for i in idc_obj]
        dic['data'] = data
        dic['count'] = idc_obj.count()
        dic['code'] = 0
        return HttpResponse(json.dumps(dic))

    aobj = App_info.objects.all()
    data = [{
        "enname": i.enname,
        "cnname": i.cnname,
        "appdomain_info": str(i.appdomain_info),
        "manager": i.manager
    } for i in aobj]

    paginator = Paginator(data, limit)
    dic['data'] = list(paginator.get_page(current_page).object_list)
    dic['count'] = aobj.count()
    dic['code'] = 0

    return HttpResponse(json.dumps(dic))


@check_permission
def app_info(request):
    return render(request, 'cmdb/appinfo.html')


@login_required(login_url='/login/')
@check_permission
def app_infoadd(request):
    if request.method == "POST":
        enname = request.POST.get('enname', '').strip()
        cnname = request.POST.get('cnname', '').strip()
        appdomain_info_id = request.POST.get('appdomain_info')
        manager = request.POST.get('manager', '').strip()

        try:
            get_group = Appdomain_info.objects.get(id=int(appdomain_info_id))
            obj = App_info.objects.create(
                enname=enname, cnname=cnname,
                appdomain_info=get_group, manager=manager
            )
            if obj:
                return HttpResponse(json.dumps({'msg': '添加成功', 'status': 1}))
            else:
                return HttpResponse(json.dumps({'msg': 'err', 'status': 0}))
        except (ValueError, Appdomain_info.DoesNotExist):
            return HttpResponse(json.dumps({'msg': '数据无效', 'status': 0}))
        except Exception as e:
            logger.error(f"添加应用失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))

    data = list(Appdomain_info.objects.all())
    return render(request, 'cmdb/appinfoadd.html', {'group': data})


@login_required(login_url='/login/')
@check_permission
def appinfodel(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        dlist = request.POST.get('dlist', '').strip()

        try:
            deleted_count = 0
            if dlist:
                name_list = [x.strip() for x in dlist.strip('[]').replace('"', '').split(',') if x.strip()]
                for n in name_list:
                    try:
                        idc_obj = App_info.objects.get(enname=n)
                        idc_obj.delete()
                        deleted_count += 1
                    except App_info.DoesNotExist:
                        continue

            if name:
                idc_obj = App_info.objects.get(enname=name)
                idc_obj.delete()
                deleted_count += 1

            return HttpResponse(json.dumps({'msg': f'删除成功({deleted_count})', 'status': 1}))
        except App_info.DoesNotExist:
            return HttpResponse(json.dumps({'msg': '应用不存在', 'status': 0}))
        except Exception as e:
            logger.error(f"删除应用失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))


@login_required(login_url='/login/')
@check_permission
def appinfoedit(request):
    if request.method == "POST":
        enname = request.POST.get('enname', '').strip()
        cnname = request.POST.get('cnname', '').strip()
        appdomain_info_id = request.POST.get('appdomain_info')
        manager = request.POST.get('manager', '').strip()

        try:
            get_group = Appdomain_info.objects.get(id=int(appdomain_info_id))
            idc_obj = App_info.objects.get(enname=enname)
            idc_obj.cnname = cnname
            idc_obj.appdomain_info = get_group
            idc_obj.manager = manager
            idc_obj.save()
            return HttpResponse(json.dumps({'msg': '修改成功', 'status': 1}))
        except (ValueError, App_info.DoesNotExist, Appdomain_info.DoesNotExist):
            return HttpResponse(json.dumps({'msg': '数据无效', 'status': 0}))
        except Exception as e:
            logger.error(f"修改应用失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))

    data = list(Appdomain_info.objects.all())
    return render(request, 'cmdb/appinfoedit.html', {'group': data})


def appname_infodata(request):
    data = []
    appname = request.GET.get("appname", "").strip()

    if not appname:
        return render(request, 'cmdb/appnameinfo.html', {"serverinfo": []})

    try:
        getappnameid = App_info.objects.get(enname=appname)
        get_serverinfo = Server_info.objects.filter(app_info=getappnameid.id)

        for s in get_serverinfo:
            data.append({
                "env": s.env.name,
                "ip": s.ip,
                "status": s.status.name,
                "type": "物理机"
            })

        get_vminfo = Vm_info.objects.filter(app_info=getappnameid.id)
        for v in get_vminfo:
            data.append({
                "env": v.env.name,
                "ip": v.ip,
                "status": v.status.name,
                "type": "虚拟机"
            })
    except App_info.DoesNotExist:
        logger.warning(f"应用不存在: {appname}")
    except Exception as e:
        logger.error(f"获取应用信息失败: {e}")

    return render(request, 'cmdb/appnameinfo.html', {"serverinfo": data})
