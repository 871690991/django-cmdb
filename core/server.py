import json
import logging
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from core.permission import check_permission
from core.models import (
    Server_info, Server_status, Envs, App_info, Idc_info,
    Vm_info
)

logger = logging.getLogger(__name__)


@login_required(login_url='/login/')
@check_permission
def server(request):
    return render(request, 'cmdb/server.html')


@login_required(login_url='/login/')
def server_info(request):
    dic = {
        "code": 1,
        "msg": "",
        "count": 0,
        "data": []
    }
    search = request.GET.get("ip", "").strip()
    current_page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)

    try:
        limit = int(limit)
        current_page = int(current_page)
    except (ValueError, TypeError):
        limit = 10
        current_page = 1

    if search:
        idc_obj = Server_info.objects.filter(ip__contains=search)
        data = [{
            "ip": i.ip,
            "managerip": i.managerip,
            "env": i.env.name,
            "sn": i.sn,
            "status": i.status.name
        } for i in idc_obj]

        idc_obj2 = Server_info.objects.filter(sn__contains=search)
        existing_ips = {item["ip"] for item in data}
        for i2 in idc_obj2:
            if i2.ip not in existing_ips:
                data.append({
                    "ip": i2.ip,
                    "managerip": i2.managerip,
                    "env": i2.env.name,
                    "sn": i2.sn,
                    "status": i2.status.name
                })
                existing_ips.add(i2.ip)

        dic['data'] = data
        dic['count'] = len(data)
        dic['code'] = 0
        return HttpResponse(json.dumps(dic))

    aobj = Server_info.objects.all()
    data = [{
        "ip": i.ip,
        "managerip": i.managerip,
        "env": i.env.name,
        "sn": i.sn,
        "status": i.status.name
    } for i in aobj]

    paginator = Paginator(data, limit)
    dic['data'] = list(paginator.get_page(current_page).object_list)
    dic['count'] = aobj.count()
    dic['code'] = 0

    return HttpResponse(json.dumps(dic))


@login_required(login_url='/login/')
@check_permission
def server_infoadd(request):
    if request.method == "POST":
        ip = request.POST.get('ip', '').strip()
        hostname = request.POST.get('hostname', '').strip()
        managerip = request.POST.get('managerip', '').strip()
        status_id = request.POST.get('status')
        env_id = request.POST.get('env')
        app_info_id = request.POST.get('app_info')
        idc_id = request.POST.get('idc')
        brand = request.POST.get('brand', '').strip()
        hardware_parameters = request.POST.get('hardware_parameters', '').strip()
        rittal = request.POST.get('rittal', '').strip()
        u_site = request.POST.get('u_site', '').strip()
        sn = request.POST.get('sn', '').strip()
        buy_time = request.POST.get('buy_time') or None
        expire_date = request.POST.get('expire_date') or None
        system = request.POST.get('system', '').strip()

        try:
            status_name = Server_status.objects.get(id=int(status_id))
            env_name = Envs.objects.get(id=int(env_id))
            appname = App_info.objects.get(id=int(app_info_id))
            idcname = Idc_info.objects.get(id=int(idc_id))

            obj = Server_info.objects.create(
                ip=ip, hostname=hostname, managerip=managerip,
                status=status_name, env=env_name, app_info=appname, idc=idcname,
                brand=brand, hardware_parameters=hardware_parameters,
                rittal=rittal, u_site=u_site, sn=sn,
                buy_time=buy_time, expire_date=expire_date, system=system
            )
            if obj:
                return HttpResponse(json.dumps({'msg': '添加成功', 'status': 1}))
            else:
                return HttpResponse(json.dumps({'msg': 'err', 'status': 0}))
        except (ValueError, Server_status.DoesNotExist, Envs.DoesNotExist,
                App_info.DoesNotExist, Idc_info.DoesNotExist) as e:
            logger.error(f"添加服务器失败: {e}")
            return HttpResponse(json.dumps({'msg': '数据无效', 'status': 0}))
        except Exception as e:
            logger.error(f"添加服务器失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))

    env = list(Envs.objects.all())
    status = list(Server_status.objects.all())
    app = list(App_info.objects.all())
    idc = list(Idc_info.objects.all())
    return render(request, 'cmdb/serveradd.html',
                  {'env': env, 'status': status, 'app': app, 'idc': idc})


@login_required(login_url='/login/')
@check_permission
def server_infodel(request):
    if request.method == "POST":
        ip = request.POST.get('ip', '').strip()
        dlist = request.POST.get('dlist', '').strip()

        try:
            deleted_count = 0
            if dlist:
                ip_list = [x.strip() for x in dlist.strip('[]').replace('"', '').split(',') if x.strip()]
                for i in ip_list:
                    try:
                        idc_obj = Server_info.objects.get(ip=i)
                        idc_obj.delete()
                        deleted_count += 1
                    except Server_info.DoesNotExist:
                        logger.warning(f"服务器不存在: {i}")
                        continue

            if ip:
                idc_obj = Server_info.objects.get(ip=ip)
                idc_obj.delete()
                deleted_count += 1

            return HttpResponse(json.dumps({'msg': f'删除成功({deleted_count})', 'status': 1}))
        except Server_info.DoesNotExist:
            return HttpResponse(json.dumps({'msg': '服务器不存在', 'status': 0}))
        except Exception as e:
            logger.error(f"删除服务器失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))


def host_info(request):
    return render(request, 'cmdb/serverinfo.html')


def serverhost_info(request):
    dic = {
        "code": 1,
        "msg": "",
        "data": []
    }

    ip = request.GET.get("ip", "").strip()
    if not ip:
        dic['msg'] = 'IP参数缺失'
        return HttpResponse(json.dumps(dic))

    try:
        obj = Server_info.objects.get(ip=ip)
        data = [
            {"title": "业务ip", "data": obj.ip},
            {"title": "主机名", "data": obj.hostname},
            {"title": "管理ip", "data": obj.managerip},
            {"title": "状态", "data": obj.status.name},
            {"title": "环境", "data": obj.env.name},
            {"title": "机型", "data": obj.brand},
            {"title": "硬件配置", "data": obj.hardware_parameters},
            {"title": "机柜", "data": obj.rittal},
            {"title": "U位", "data": obj.u_site},
            {"title": "sn序列号", "data": obj.sn},
            {"title": "购买时间", "data": str(obj.buy_time) if obj.buy_time else ""},
            {"title": "过保时间", "data": str(obj.expire_date) if obj.expire_date else ""},
            {"title": "应用", "data": obj.app_info.enname},
            {"title": "机房", "data": obj.idc.name},
            {"title": "操作系统", "data": obj.system},
        ]

        dic.update({
            "ip": obj.ip,
            "hostname": obj.hostname,
            "managerip": obj.managerip,
            "status": obj.status.id,
            "env": obj.env.id,
            "appname": obj.app_info.id,
            "idc": obj.idc.id,
            "brand": obj.brand,
            "hardware_parameters": obj.hardware_parameters,
            "rittal": obj.rittal,
            "u_site": obj.u_site,
            "sn": obj.sn,
            "buy_time": str(obj.buy_time) if obj.buy_time else "",
            "expire_date": str(obj.expire_date) if obj.expire_date else "",
            "system": obj.system,
        })

        dic['data'] = data
        dic['code'] = 0
    except Server_info.DoesNotExist:
        dic['msg'] = '服务器不存在'
    except Exception as e:
        logger.error(f"获取服务器信息失败: {e}")
        dic['msg'] = str(e)

    return HttpResponse(json.dumps(dic))


@login_required(login_url='/login/')
@check_permission
def server_infoedit(request):
    if request.method == "POST":
        ip = request.POST.get('ip', '').strip()
        hostname = request.POST.get('hostname', '').strip()
        managerip = request.POST.get('managerip', '').strip()
        status_id = request.POST.get('status')
        env_id = request.POST.get('env')
        app_info_id = request.POST.get('app_info')
        idc_id = request.POST.get('idc')
        brand = request.POST.get('brand', '').strip()
        hardware_parameters = request.POST.get('hardware_parameters', '').strip()
        rittal = request.POST.get('rittal', '').strip()
        u_site = request.POST.get('u_site', '').strip()
        sn = request.POST.get('sn', '').strip()
        buy_time = request.POST.get('buy_time') or None
        expire_date = request.POST.get('expire_date') or None
        system = request.POST.get('system', '').strip()

        try:
            status_name = Server_status.objects.get(id=int(status_id))
            env_name = Envs.objects.get(id=int(env_id))
            appname = App_info.objects.get(id=int(app_info_id))
            idcname = Idc_info.objects.get(id=int(idc_id))

            idc_obj = Server_info.objects.get(ip=ip)
            idc_obj.hostname = hostname
            idc_obj.managerip = managerip
            idc_obj.status = status_name
            idc_obj.env = env_name
            idc_obj.app_info = appname
            idc_obj.idc = idcname
            idc_obj.brand = brand
            idc_obj.hardware_parameters = hardware_parameters
            idc_obj.rittal = rittal
            idc_obj.u_site = u_site
            idc_obj.sn = sn
            idc_obj.system = system
            idc_obj.buy_time = buy_time
            idc_obj.expire_date = expire_date
            idc_obj.save()

            return HttpResponse(json.dumps({'msg': '修改成功', 'status': 1}))
        except (ValueError, Server_info.DoesNotExist, Server_status.DoesNotExist,
                Envs.DoesNotExist, App_info.DoesNotExist, Idc_info.DoesNotExist) as e:
            logger.error(f"修改服务器失败: {e}")
            return HttpResponse(json.dumps({'msg': '数据无效', 'status': 0}))
        except Exception as e:
            logger.error(f"修改服务器失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))

    env = list(Envs.objects.all())
    status = list(Server_status.objects.all())
    app = list(App_info.objects.all())
    idc = list(Idc_info.objects.all())
    return render(request, 'cmdb/serveredit.html',
                  {'env': env, 'status': status, 'app': app, 'idc': idc})


@check_permission
def vm(request):
    return render(request, 'cmdb/vm.html')


@login_required(login_url='/login/')
def vm_info(request):
    dic = {
        "code": 1,
        "msg": "",
        "count": 0,
        "data": []
    }
    search = request.GET.get("ip", "").strip()
    current_page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)

    try:
        limit = int(limit)
        current_page = int(current_page)
    except (ValueError, TypeError):
        limit = 10
        current_page = 1

    if search:
        idc_obj = Vm_info.objects.filter(ip__contains=search)
        data = [{
            "ip": i.ip,
            "hostname": i.hostname,
            "env": i.env.name,
            "status": i.status.name,
            "app_info": i.app_info.enname
        } for i in idc_obj]

        dic['data'] = data
        dic['count'] = idc_obj.count()
        dic['code'] = 0
        return HttpResponse(json.dumps(dic))

    aobj = Vm_info.objects.all()
    data = [{
        "ip": i.ip,
        "hostname": i.hostname,
        "env": i.env.name,
        "status": i.status.name,
        "app_info": i.app_info.enname
    } for i in aobj]

    paginator = Paginator(data, limit)
    dic['data'] = list(paginator.get_page(current_page).object_list)
    dic['count'] = aobj.count()
    dic['code'] = 0

    return HttpResponse(json.dumps(dic))


@login_required(login_url='/login/')
@check_permission
def vm_infoadd(request):
    if request.method == "POST":
        ip = request.POST.get('ip', '').strip()
        hostname = request.POST.get('hostname', '').strip()
        status_id = request.POST.get('status')
        env_id = request.POST.get('env')
        app_info_id = request.POST.get('app_info')
        idc_id = request.POST.get('idc')
        system = request.POST.get('system', '').strip()
        hardware_parameters = request.POST.get('hardware_parameters', '').strip()
        server_id = request.POST.get('server')

        try:
            status_name = Server_status.objects.get(id=int(status_id))
            env_name = Envs.objects.get(id=int(env_id))
            appname = App_info.objects.get(id=int(app_info_id))
            idcname = Idc_info.objects.get(id=int(idc_id))
            serverip = Server_info.objects.get(id=int(server_id))

            obj = Vm_info.objects.create(
                ip=ip, hostname=hostname, status=status_name, env=env_name,
                app_info=appname, idc=idcname, hardware_parameters=hardware_parameters,
                server=serverip, system=system
            )
            if obj:
                return HttpResponse(json.dumps({'msg': '添加成功', 'status': 1}))
            else:
                return HttpResponse(json.dumps({'msg': 'err', 'status': 0}))
        except (ValueError, Server_status.DoesNotExist, Envs.DoesNotExist,
                App_info.DoesNotExist, Idc_info.DoesNotExist, Server_info.DoesNotExist) as e:
            logger.error(f"添加虚拟机失败: {e}")
            return HttpResponse(json.dumps({'msg': '数据无效', 'status': 0}))
        except Exception as e:
            logger.error(f"添加虚拟机失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))

    env = list(Envs.objects.all())
    status = list(Server_status.objects.all())
    app = list(App_info.objects.all())
    idc = list(Idc_info.objects.all())
    server = list(Server_info.objects.all())
    return render(request, 'cmdb/vmadd.html',
                  {'env': env, 'status': status, 'app': app, 'idc': idc, 'server': server})


@login_required(login_url='/login/')
@check_permission
def vm_infodel(request):
    if request.method == "POST":
        ip = request.POST.get('ip', '').strip()
        dlist = request.POST.get('dlist', '').strip()

        try:
            deleted_count = 0
            if dlist:
                ip_list = [x.strip() for x in dlist.strip('[]').replace('"', '').split(',') if x.strip()]
                for i in ip_list:
                    try:
                        idc_obj = Vm_info.objects.get(ip=i)
                        idc_obj.delete()
                        deleted_count += 1
                    except Vm_info.DoesNotExist:
                        logger.warning(f"虚拟机不存在: {i}")
                        continue

            if ip:
                idc_obj = Vm_info.objects.get(ip=ip)
                idc_obj.delete()
                deleted_count += 1

            return HttpResponse(json.dumps({'msg': f'删除成功({deleted_count})', 'status': 1}))
        except Vm_info.DoesNotExist:
            return HttpResponse(json.dumps({'msg': '虚拟机不存在', 'status': 0}))
        except Exception as e:
            logger.error(f"删除虚拟机失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))


def vmhost_info(request):
    dic = {
        "code": 1,
        "msg": "",
        "data": []
    }

    ip = request.GET.get("ip", "").strip()
    if not ip:
        dic['msg'] = 'IP参数缺失'
        return HttpResponse(json.dumps(dic))

    try:
        obj = Vm_info.objects.get(ip=ip)
        data = [
            {"title": "ip", "data": obj.ip},
            {"title": "主机名", "data": obj.hostname},
            {"title": "状态", "data": obj.status.name},
            {"title": "环境", "data": obj.env.name},
            {"title": "操作系统", "data": obj.system},
            {"title": "硬件配置", "data": obj.hardware_parameters},
            {"title": "物理机", "data": obj.server.ip},
            {"title": "应用", "data": obj.app_info.enname},
            {"title": "机房", "data": obj.idc.name},
        ]

        dic.update({
            "ip": obj.ip,
            "hostname": obj.hostname,
            "status": obj.status.id,
            "env": obj.env.id,
            "appname": obj.app_info.id,
            "idc": obj.idc.id,
            "system": obj.system,
            "hardware_parameters": obj.hardware_parameters,
            "server": obj.server.id,
        })

        dic['data'] = data
        dic['code'] = 0
    except Vm_info.DoesNotExist:
        dic['msg'] = '虚拟机不存在'
    except Exception as e:
        logger.error(f"获取虚拟机信息失败: {e}")
        dic['msg'] = str(e)

    return HttpResponse(json.dumps(dic))


@login_required(login_url='/login/')
@check_permission
def vm_infoedit(request):
    if request.method == "POST":
        ip = request.POST.get('ip', '').strip()
        hostname = request.POST.get('hostname', '').strip()
        status_id = request.POST.get('status')
        env_id = request.POST.get('env')
        app_info_id = request.POST.get('app_info')
        idc_id = request.POST.get('idc')
        system = request.POST.get('system', '').strip()
        hardware_parameters = request.POST.get('hardware_parameters', '').strip()
        server_id = request.POST.get('server')

        try:
            status_name = Server_status.objects.get(id=int(status_id))
            env_name = Envs.objects.get(id=int(env_id))
            appname = App_info.objects.get(id=int(app_info_id))
            idcname = Idc_info.objects.get(id=int(idc_id))
            serverip = Server_info.objects.get(id=int(server_id))

            idc_obj = Vm_info.objects.get(ip=ip)
            idc_obj.hostname = hostname
            idc_obj.server = serverip
            idc_obj.status = status_name
            idc_obj.env = env_name
            idc_obj.app_info = appname
            idc_obj.idc = idcname
            idc_obj.system = system
            idc_obj.hardware_parameters = hardware_parameters
            idc_obj.save()

            return HttpResponse(json.dumps({'msg': '修改成功', 'status': 1}))
        except (ValueError, Vm_info.DoesNotExist, Server_status.DoesNotExist,
                Envs.DoesNotExist, App_info.DoesNotExist, Idc_info.DoesNotExist,
                Server_info.DoesNotExist) as e:
            logger.error(f"修改虚拟机失败: {e}")
            return HttpResponse(json.dumps({'msg': '数据无效', 'status': 0}))
        except Exception as e:
            logger.error(f"修改虚拟机失败: {e}")
            return HttpResponse(json.dumps({'msg': str(e), 'status': 0}))

    env = list(Envs.objects.all())
    status = list(Server_status.objects.all())
    app = list(App_info.objects.all())
    idc = list(Idc_info.objects.all())
    server = list(Server_info.objects.all())
    return render(request, 'cmdb/vmedit.html',
                  {'env': env, 'status': status, 'app': app, 'idc': idc, 'server': server})


def getvm_info(request):
    return render(request, 'cmdb/vminfo.html')


def vm_list(request):
    dic = {
        "code": 1,
        "msg": "",
        "count": 0,
        "data": []
    }
    search = request.GET.get("ip", "").strip()

    if not search:
        dic['msg'] = 'IP参数缺失'
        return HttpResponse(json.dumps(dic))

    try:
        serverip = Server_info.objects.get(ip=search)
        idc_obj = Vm_info.objects.filter(server=serverip)
        data = [{
            "ip": i.ip,
            "hostname": i.hostname,
            "env": i.env.name,
            "status": i.status.name,
            "app_info": i.app_info.enname
        } for i in idc_obj]

        dic['data'] = data
        dic['count'] = idc_obj.count()
        dic['code'] = 0
    except Server_info.DoesNotExist:
        dic['msg'] = '物理机不存在'
    except Exception as e:
        logger.error(f"获取虚拟机列表失败: {e}")
        dic['msg'] = str(e)

    return HttpResponse(json.dumps(dic))
