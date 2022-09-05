from email.mime import application
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
import json
from django.http import HttpResponseRedirect, JsonResponse,HttpResponsePermanentRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from core.permission import check_permission
from openstack import models
from core.models import App_info,Envs
from keystoneauth1.identity import v3
from keystoneauth1 import session
from django.db.models import Sum, Count,Q
import datetime
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
import _thread
# @login_required(login_url='/login')
# @check_permission

def openstack_auth(cluster_name):
    authdata=models.cloud_cluster.objects.filter(cluster_name=cluster_name)
    for i in authdata:
        # print(i.cluster_name,i.auth_url,i.username,i.password,i.project_name,i.user_domain_name,i.project_domain_name)
        auth = v3.Password(
        auth_url=i.auth_url,
        username=i.username,
        password=i.password,project_name=i.project_name,
        user_domain_name=i.user_domain_name,
        project_domain_name=i.project_domain_name,
        )
        sess=session.Session(auth=auth)

        return sess
def openstack_adminauth(cluster_name):
    authdata=models.cloud_cluster.objects.filter(cluster_name=cluster_name)
    for i in authdata:
        # print(i.cluster_name,i.auth_url,i.username,i.password,i.project_name,i.user_domain_name,i.project_domain_name)
        auth = v3.Password(
        auth_url=i.auth_url,
        username="admin",
        password=i.admin_password,project_name="belle",
        user_domain_name=i.user_domain_name,
        project_domain_name=i.project_domain_name,
        )
        sess=session.Session(auth=auth)

        return sess

def syn_flavor_info(cluster_name):
    print("syn_flavor_info,start")

    from novaclient import client
    sess=openstack_auth(cluster_name)

    nova_obj = client.Client('2', session=sess)
    res = nova_obj.flavors.list(detailed=True)
    for item in res:
        tmp_dic = {
            "cluster_name": "",
            "flavor_name": "",
            "flavor_id": "",
        }
        tmp_dic["cluster_name"] = models.cloud_cluster.objects.get(cluster_name=cluster_name)
        tmp_dic["flavor_name"] = item.name
        tmp_dic["flavor_id"] = item.id
        models.cloud_flavor.objects.filter(flavor_id=item.id).delete()
        models.cloud_flavor.objects.create(**tmp_dic)

    print("syn_flavor_info,done")


def sync_node_info(cluster_name):
    print("sync_node_info,start")

    cluster_obj = models.cloud_cluster.objects.get(cluster_name=cluster_name)
    models.cloud_compute_resource.objects.filter(cluster=cluster_obj).delete()
    sess=openstack_adminauth(cluster_name)
    from novaclient import client

    nova_obj=client.Client('2', session=sess)


    res = nova_obj.hypervisors.list()

    for item in res:
        tmp_dic={}

        tmp_dic["cluster"] = cluster_obj
        tmp_dic["host_ip"] = item.host_ip
        tmp_dic["hypervisor_hostname"] = item.hypervisor_hostname
        tmp_dic["hypervisor_type"] = item.hypervisor_type
        tmp_dic["node_id"] = item.id
        tmp_dic["running_vms"] = item.running_vms
        tmp_dic["state"] = item.state
        tmp_dic["status"] = item.status
        tmp_dic["vcpus"] = item.vcpus
        tmp_dic["vcpus_used"] = item.vcpus_used
        tmp_dic["vcpus_used_percent"] = item.vcpus_used*100/item.vcpus
        tmp_dic["local_gb"] = item.local_gb
        tmp_dic["local_gb_used"] = item.local_gb_used
        tmp_dic["local_gb_used_percent"] = item.local_gb_used * 100/item.local_gb
        tmp_dic["memory_mb"] = item.memory_mb/1024
        tmp_dic["memory_mb_used"] = item.memory_mb_used/1024
        tmp_dic["memory_mb_used_percent"] = item.memory_mb_used * 100/item.memory_mb

        models.cloud_compute_resource.objects.create(**tmp_dic)

    print("sync_node_info,done")


def syn_network_info(cluster_name):
    print("syn_network_info,start")

    cluster_obj = models.cloud_cluster.objects.get(cluster_name=cluster_name)

    sess=openstack_auth(cluster_name)
    from neutronclient.v2_0 import client

    neutron_obj = client.Client(session=sess)
    tmp_dic = {}
    networks_res = neutron_obj.list_networks()
    for networks_item in networks_res["networks"]:
        tmp_dic[networks_item["id"]] = {}
        tmp_dic[networks_item["id"]]["network_id"] = networks_item["id"]
        tmp_dic[networks_item["id"]]["name"] = networks_item["name"]
        tmp_dic[networks_item["id"]]["cluster_name"] = cluster_name
        tmp_dic[networks_item["id"]]["used_num"] = 0
        tmp_dic[networks_item["id"]]["percent"] = 0

    subnets_res = neutron_obj.list_subnets()
    for subnets_item in subnets_res["subnets"]:
        tmp_dic[subnets_item["network_id"]
                ]["subnet"] = subnets_item["cidr"]

        start_ip = int(
            subnets_item["allocation_pools"][0]["start"].split(".")[-1])
        end_ip = int(subnets_item["allocation_pools"]
                        [0]["end"].split(".")[-1])
        total_num = end_ip - start_ip
        tmp_dic[subnets_item["network_id"]]["total_num"] = total_num
        tmp_dic[subnets_item["network_id"]]["free_num"] = total_num

    ports_res = neutron_obj.list_ports()
    for ports_item in ports_res["ports"]:
        tmp_dic[ports_item["network_id"]]["used_num"] += 1

        used_num = tmp_dic[ports_item["network_id"]]["used_num"]
        total_num = tmp_dic[ports_item["network_id"]]["total_num"]
        free_num = total_num - \
            tmp_dic[ports_item["network_id"]]["used_num"]

        tmp_dic[ports_item["network_id"]]["free_num"] = free_num
        percent = used_num * 100 / total_num
        # tmp_dic[ports_item["network_id"]]["percent"] = "{percent}%".format(percent=percent)
        tmp_dic[ports_item["network_id"]]["percent"] = percent

    for record in tmp_dic.values():
        record["cluster_name"] = models.cloud_cluster.objects.get(
            cluster_name=record["cluster_name"])
        record_exist_obj = models.cloud_network.objects.filter(
            network_id=record["network_id"])
        if len(record_exist_obj) != 0:
            record_exist_obj.update(**record)
        else:
            models.cloud_network.objects.create(**record)

    # 清理多余数据
    db_res = models.cloud_network.objects.filter(
        cluster_name=cluster_obj).all()
    for item in db_res:
        if item.network_id not in tmp_dic.keys():
            models.cloud_network.objects.filter(
                network_id=item.network_id).delete()

    print("syn_network_info,done")


# def get_vm_info_by_server_id(cluster_name,server_id):
#     sess=openstack_adminauth(cluster_name)
#     from novaclient import client

#     nova_obj=client.Client('2', session=sess)

#     try:
#         server = nova_obj.servers.get(server_id)

#     except Exception as e:
#         print(e)
#     return server

def syn_vm_info(cluster_name):
    print("syn_vm_info,start")

    sess=openstack_adminauth(cluster_name)
    from novaclient import client
    nova_obj=client.Client('2', session=sess)
    servers = nova_obj.servers.list()
    cluster_obj = models.cloud_cluster.objects.get(cluster_name=cluster_name)
    models.cloud_vm_info.objects.filter(cluster_name=cluster_obj).delete()

    for server_item in servers:
        if server_item.id == "1cb6c269-5349-4760-a534-a4af4612ebcb":
            pass
        tmp_dic={}
        cloud_flavor_res = models.cloud_flavor.objects.filter(flavor_id=server_item.flavor.get("id")).first()
        tmp_dic["cluster_name"] = cluster_obj
        tmp_dic["flavor"] = cloud_flavor_res.flavor_name
        tmp_dic["name"] = server_item.name
        tmp_dic["server_id"] = server_item.id
        tmp_dic["status"] = getattr(server_item, 'OS-EXT-STS:vm_state').upper()


        
        for k in server_item.addresses:
            ipadd=server_item.addresses.get(k)
            for i in ipadd:
                tmp_dic["ip"]=i.get("addr")
        # data=get_vm_info_by_server_id(cluster_name,tmp_dic["server_id"])
        tmp_dic["compute"] = getattr(server_item, "OS-EXT-SRV-ATTR:host")

        raw_time_first = str(server_item.created).split('T')[0]
        raw_time_second = str(server_item.created).split('T')[
            1].split('Z')[0]
        raw_time = raw_time_first + ' ' + raw_time_second
        raw_time_obj = datetime.datetime.strptime(
            raw_time, "%Y-%m-%d %H:%M:%S")
        local_time = raw_time_obj + datetime.timedelta(hours=8)
        tmp_dic["date"] = local_time
        models.cloud_vm_info.objects.create(**tmp_dic)
    print("syn_vm_info,done")


def sync_openstack_data(request):
    cluster_name=request.GET.get("clustername")

    _thread.start_new_thread(syn_network_info,(cluster_name,))
    _thread.start_new_thread(sync_node_info,(cluster_name,))
    _thread.start_new_thread(syn_flavor_info,(cluster_name,))
    _thread.start_new_thread(syn_vm_info,(cluster_name,))
    # syn_network_info(cluster_name)
    # sync_node_info(cluster_name)
    # syn_flavor_info(cluster_name)
    # syn_vm_info(cluster_name)
    return HttpResponse(json.dumps({"status":"syncing"}))


def get_cluster_Resources():


    compute_res = models.cloud_compute_resource.objects.values(
        "cluster"
    ).annotate(
        node_num=Count("cluster"),
        vcpus_total=Sum("vcpus"),
        vcpus_used_total=Sum("vcpus_used"),
        local_gb_total=Sum("local_gb"),
        local_gb_used_total=Sum("local_gb_used"),
        memory_mb_total=Sum("memory_mb"),
        memory_mb_used_total=Sum("memory_mb_used"),
        running_vms_total=Sum("running_vms"),
    )

    db_obj = []
    for item in compute_res:

        item["vcpus_used_percent"] = int(item["vcpus_used_total"] * \
            100/item["vcpus_total"])
        item["local_gb_used_percent"] = int(item["local_gb_used_total"] * \
            100/item["local_gb_total"])
        item["memory_mb_used_percent"] = int(item["memory_mb_used_total"] * \
            100/item["memory_mb_total"])
        network_res = models.cloud_network.objects.filter(cluster_name=item["cluster"]).aggregate(
            network_total_num=Sum("total_num"),
            network_used_num=Sum("used_num"),
        )
        item.update(network_res)
        item["network_used_percent"] = int(item["network_used_num"] * \
            100/item["network_total_num"])
        available_compute_res = models.cloud_compute_resource.objects.exclude(
            Q(vcpus_used_percent__gt=250) |
            Q(local_gb_used_percent__gt=95) |
            Q(memory_mb_used_percent__gt=95)).values(
            "cluster"
        ).annotate(
            node_num=Count("cluster"),
            vcpus_total=Sum("vcpus"),
            vcpus_used_total=Sum("vcpus_used"),
            local_gb_total=Sum("local_gb"),
            local_gb_used_total=Sum("local_gb_used"),
            memory_mb_total=Sum("memory_mb"),
            memory_mb_used_total=Sum("memory_mb_used"),
            running_vms_total=Sum("running_vms"),
        ).order_by("-node_num")
        item["standard_c4m8_available"] = 0
        for avail_item in available_compute_res:
            if avail_item["cluster"] == item["cluster"]:
                item["standard_c4m8_available"] = min(
                    (avail_item["vcpus_total"] * 4 -
                     avail_item["vcpus_used_total"]) / 4,
                    (avail_item["memory_mb_total"] -
                     avail_item["memory_mb_used_total"]) / 8
                )
                if item["standard_c4m8_available"] < 1:
                    item["standard_c4m8_available"] = 0
        db_obj.append(item)
        clustername= models.cloud_cluster.objects.get(id=item["cluster"])
        item['cluster']=clustername.cluster_name

    # 需要重新分配的虚拟机资源
    return db_obj






def cluster_dashboard(request):
    dic={"obj_info":get_cluster_Resources()}
    cluster_obj = models.cloud_cluster.objects.all()
    for i in cluster_obj:
        compute_res = models.cloud_compute_resource.objects.filter(cluster=i).all()
        dic["compute_res"]=compute_res

    
    return render(request, 'openstack/cluster_dashboard.html',dic)





def cluster_member_info(request):
    '''
    计算节点运行的虚拟机信息
    :param request:
    :param cluster_name:
    :return:
    '''
    compute_name=request.GET.get("node")
    member_res = models.cloud_vm_info.objects.filter(
        compute=compute_name).all()
    return render(request, 'openstack/cluster_member_info.html', {
        "member_res": member_res,
    })


def vm_info(request):
    
    return render(request, 'openstack/vm_info.html')
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)




def get_clustername(id):
    idc_obj=models.cloud_cluster.objects.filter(id=id)
    for i in idc_obj:
        return(i.cluster_name)


def vm_listdata(request):

        
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
    datalist=[]
    if search:
        idc_obj=list(models.cloud_vm_info.objects.filter(ip__contains=search).values())




        for data in idc_obj:
            data["clustername"]=get_clustername(data.get("cluster_name_id"))
            datalist.append(data)
        dic['data']=datalist
        dic['count']=len(datalist)
        dic['code']=0
        return HttpResponse(json.dumps(dic,cls=DateEncoder))



    cluster_obj = models.cloud_cluster.objects.all()
    for i in cluster_obj:
        compute_res = models.cloud_vm_info.objects.filter(cluster_name=i).values()
        for data in compute_res:
            data["clustername"]=get_clustername(data.get("cluster_name_id"))
            datalist.append(data)
    paginator = Paginator(datalist, limit)
    dic['data']=paginator.get_page(currentPage).object_list
    dic['count']=len(datalist)
    dic['code']=0
    return HttpResponse(json.dumps(dic,cls=DateEncoder))



def vm_info(request):
    
    return render(request, 'openstack/vm_info.html')


def vm_add(request):
    
    clustername=models.cloud_cluster.objects.all()
    cluster=[]
    for c in clustername:
        cluster.append(c.cluster_name)

    flavor=[]
    f=models.cloud_flavor.objects.all()
    for d in f:
        flavor.append(d.flavor_name)

    appname=[]
    app=App_info.objects.all()
    for a in app:
        appname.append(a.enname)

    envs=[]
    env=Envs.objects.all()
    for e in env:
        envs.append(e.name)


    dic={"envs":envs,"appname":appname,"flavor":flavor,"cluster":cluster}
    return render(request, 'openstack/vm_add.html',dic)