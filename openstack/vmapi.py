import json
import datetime
import logging
import threading
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from openstack import models
from core.models import App_info, Envs

logger = logging.getLogger(__name__)

try:
    from novaclient import client as nova_client
    from neutronclient.v2_0 import client as neutron_client
    from keystoneauth1.identity import v3
    from keystoneauth1 import session
    OPENSTACK_SDK_AVAILABLE = True
except ImportError:
    OPENSTACK_SDK_AVAILABLE = False
    logger.warning("OpenStack SDK not installed, cloud features will be unavailable")


def openstack_auth(cluster_name):
    if not OPENSTACK_SDK_AVAILABLE:
        logger.error("OpenStack SDK not available")
        return None

    try:
        cluster = models.cloud_cluster.objects.get(cluster_name=cluster_name)
    except models.cloud_cluster.DoesNotExist:
        logger.error(f"Cluster not found: {cluster_name}")
        return None

    auth = v3.Password(
        auth_url=cluster.auth_url,
        username=cluster.username,
        password=cluster.password,
        project_name=cluster.project_name,
        user_domain_name=cluster.user_domain_name,
        project_domain_name=cluster.project_domain_name,
    )
    return session.Session(auth=auth)


def openstack_admin_auth(cluster_name):
    if not OPENSTACK_SDK_AVAILABLE:
        logger.error("OpenStack SDK not available")
        return None

    try:
        cluster = models.cloud_cluster.objects.get(cluster_name=cluster_name)
    except models.cloud_cluster.DoesNotExist:
        logger.error(f"Cluster not found: {cluster_name}")
        return None

    auth = v3.Password(
        auth_url=cluster.auth_url,
        username="admin",
        password=cluster.admin_password,
        project_name="belle",
        user_domain_name=cluster.user_domain_name,
        project_domain_name=cluster.project_domain_name,
    )
    return session.Session(auth=auth)


def syn_flavor_info(cluster_name):
    logger.info(f"syn_flavor_info, start for cluster: {cluster_name}")

    if not OPENSTACK_SDK_AVAILABLE:
        logger.error("OpenStack SDK not available")
        return

    sess = openstack_auth(cluster_name)
    if not sess:
        return

    try:
        nova = nova_client.Client('2', session=sess)
        res = nova.flavors.list(detailed=True)
        cluster_obj = models.cloud_cluster.objects.get(cluster_name=cluster_name)

        for item in res:
            models.cloud_flavor.objects.update_or_create(
                flavor_id=item.id,
                defaults={
                    'cluster_name': cluster_obj,
                    'flavor_name': item.name,
                }
            )
    except Exception as e:
        logger.error(f"Failed to sync flavor info: {e}")

    logger.info(f"syn_flavor_info, done for cluster: {cluster_name}")


def sync_node_info(cluster_name):
    logger.info(f"sync_node_info, start for cluster: {cluster_name}")

    if not OPENSTACK_SDK_AVAILABLE:
        logger.error("OpenStack SDK not available")
        return

    try:
        cluster_obj = models.cloud_cluster.objects.get(cluster_name=cluster_name)
    except models.cloud_cluster.DoesNotExist:
        logger.error(f"Cluster not found: {cluster_name}")
        return

    models.cloud_compute_resource.objects.filter(cluster=cluster_obj).delete()
    sess = openstack_admin_auth(cluster_name)
    if not sess:
        return

    try:
        nova = nova_client.Client('2', session=sess)
        res = nova.hypervisors.list()

        for item in res:
            vcpus = item.vcpus or 1
            local_gb = item.local_gb or 1
            memory_mb = item.memory_mb or 1

            vcpus_used_percent = (item.vcpus_used * 100 / vcpus) if vcpus else 0
            local_gb_used_percent = (item.local_gb_used * 100 / local_gb) if local_gb else 0
            memory_mb_used_percent = (item.memory_mb_used * 100 / memory_mb) if memory_mb else 0

            models.cloud_compute_resource.objects.create(
                cluster=cluster_obj,
                host_ip=item.host_ip,
                hypervisor_hostname=item.hypervisor_hostname,
                hypervisor_type=item.hypervisor_type,
                node_id=item.id,
                running_vms=item.running_vms,
                state=item.state,
                status=item.status,
                vcpus=item.vcpus,
                vcpus_used=item.vcpus_used,
                vcpus_used_percent=vcpus_used_percent,
                local_gb=item.local_gb,
                local_gb_used=item.local_gb_used,
                local_gb_used_percent=local_gb_used_percent,
                memory_mb=item.memory_mb / 1024,
                memory_mb_used=item.memory_mb_used / 1024,
                memory_mb_used_percent=memory_mb_used_percent,
            )
    except Exception as e:
        logger.error(f"Failed to sync node info: {e}")

    logger.info(f"sync_node_info, done for cluster: {cluster_name}")


def syn_network_info(cluster_name):
    logger.info(f"syn_network_info, start for cluster: {cluster_name}")

    if not OPENSTACK_SDK_AVAILABLE:
        logger.error("OpenStack SDK not available")
        return

    try:
        cluster_obj = models.cloud_cluster.objects.get(cluster_name=cluster_name)
    except models.cloud_cluster.DoesNotExist:
        logger.error(f"Cluster not found: {cluster_name}")
        return

    sess = openstack_auth(cluster_name)
    if not sess:
        return

    try:
        neutron = neutron_client.Client(session=sess)
        networks_res = neutron.list_networks()

        tmp_dic = {}
        for networks_item in networks_res["networks"]:
            network_id = networks_item["id"]
            tmp_dic[network_id] = {
                "network_id": network_id,
                "name": networks_item["name"],
                "cluster_name": cluster_name,
                "used_num": 0,
                "percent": 0,
            }

        subnets_res = neutron.list_subnets()
        for subnets_item in subnets_res["subnets"]:
            network_id = subnets_item["network_id"]
            if network_id in tmp_dic:
                tmp_dic[network_id]["subnet"] = subnets_item["cidr"]

                allocation_pools = subnets_item.get("allocation_pools", [])
                if allocation_pools:
                    start_ip = int(allocation_pools[0]["start"].split(".")[-1])
                    end_ip = int(allocation_pools[0]["end"].split(".")[-1])
                    total_num = end_ip - start_ip
                    tmp_dic[network_id]["total_num"] = total_num
                    tmp_dic[network_id]["free_num"] = total_num

        ports_res = neutron.list_ports()
        for ports_item in ports_res["ports"]:
            network_id = ports_item["network_id"]
            if network_id in tmp_dic:
                tmp_dic[network_id]["used_num"] += 1
                total_num = tmp_dic[network_id].get("total_num", 1)
                if total_num > 0:
                    tmp_dic[network_id]["free_num"] = total_num - tmp_dic[network_id]["used_num"]
                    tmp_dic[network_id]["percent"] = tmp_dic[network_id]["used_num"] * 100 / total_num

        for record in tmp_dic.values():
            record["cluster_name"] = cluster_obj
            record_exist_obj = models.cloud_network.objects.filter(network_id=record["network_id"])
            if record_exist_obj.exists():
                record_exist_obj.update(**record)
            else:
                models.cloud_network.objects.create(**record)

        db_res = models.cloud_network.objects.filter(cluster_name=cluster_obj).all()
        for item in db_res:
            if item.network_id not in tmp_dic.keys():
                item.delete()

    except Exception as e:
        logger.error(f"Failed to sync network info: {e}")

    logger.info(f"syn_network_info, done for cluster: {cluster_name}")


def syn_vm_info(cluster_name):
    logger.info(f"syn_vm_info, start for cluster: {cluster_name}")

    if not OPENSTACK_SDK_AVAILABLE:
        logger.error("OpenStack SDK not available")
        return

    sess = openstack_admin_auth(cluster_name)
    if not sess:
        return

    try:
        nova = nova_client.Client('2', session=sess)
        servers = nova.servers.list()
        cluster_obj = models.cloud_cluster.objects.get(cluster_name=cluster_name)
        models.cloud_vm_info.objects.filter(cluster_name=cluster_obj).delete()

        for server_item in servers:
            if server_item.id == "1cb6c269-5349-4760-a534-a4af4612ebcb":
                continue

            flavor_res = models.cloud_flavor.objects.filter(flavor_id=server_item.flavor.get("id")).first()
            flavor_name = flavor_res.flavor_name if flavor_res else ""

            vm_ip = ""
            for k in server_item.addresses:
                ipadd = server_item.addresses.get(k, [])
                for i in ipadd:
                    if i.get("addr"):
                        vm_ip = i.get("addr")
                        break
                if vm_ip:
                    break

            try:
                raw_time = str(server_item.created).replace("T", " ").replace("Z", "")
                raw_time_obj = datetime.datetime.strptime(raw_time[:19], "%Y-%m-%d %H:%M:%S")
                local_time = raw_time_obj + datetime.timedelta(hours=8)
            except (ValueError, AttributeError):
                local_time = datetime.datetime.now()

            models.cloud_vm_info.objects.create(
                cluster_name=cluster_obj,
                flavor=flavor_name,
                name=server_item.name,
                server_id=server_item.id,
                status=getattr(server_item, 'OS-EXT-STS:vm_state', 'unknown').upper(),
                ip=vm_ip,
                compute=getattr(server_item, "OS-EXT-SRV-ATTR:host", ""),
                date=local_time,
            )

    except Exception as e:
        logger.error(f"Failed to sync VM info: {e}")

    logger.info(f"syn_vm_info, done for cluster: {cluster_name}")


def sync_openstack_data(request):
    cluster_name = request.GET.get("clustername")

    if not cluster_name:
        return HttpResponse(json.dumps({"status": "error", "msg": "cluster name required"}))

    thread = threading.Thread(target=syn_network_info, args=(cluster_name,))
    thread.start()
    thread = threading.Thread(target=sync_node_info, args=(cluster_name,))
    thread.start()
    thread = threading.Thread(target=syn_flavor_info, args=(cluster_name,))
    thread.start()
    thread = threading.Thread(target=syn_vm_info, args=(cluster_name,))
    thread.start()

    return HttpResponse(json.dumps({"status": "syncing"}))


def get_cluster_resources():
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
        vcpus_total = item["vcpus_total"] or 1
        local_gb_total = item["local_gb_total"] or 1
        memory_mb_total = item["memory_mb_total"] or 1

        item["vcpus_used_percent"] = int((item["vcpus_used_total"] or 0) * 100 / vcpus_total)
        item["local_gb_used_percent"] = int((item["local_gb_used_total"] or 0) * 100 / local_gb_total)
        item["memory_mb_used_percent"] = int((item["memory_mb_used_total"] or 0) * 100 / memory_mb_total)

        network_res = models.cloud_network.objects.filter(cluster_name=item["cluster"]).aggregate(
            network_total_num=Sum("total_num"),
            network_used_num=Sum("used_num"),
        )
        item.update(network_res)

        network_total = item["network_total_num"] or 1
        item["network_used_percent"] = int((item["network_used_num"] or 0) * 100 / network_total)

        available_compute_res = models.cloud_compute_resource.objects.exclude(
            Q(vcpus_used_percent__gt=250) |
            Q(local_gb_used_percent__gt=95) |
            Q(memory_mb_used_percent__gt=95)
        ).values("cluster").annotate(
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
                avail_vcpus = avail_item["vcpus_total"] or 0
                avail_memory = avail_item["memory_mb_total"] or 0
                avail_vcpus_used = avail_item["vcpus_used_total"] or 0
                avail_memory_used = avail_item["memory_mb_used_total"] or 0

                item["standard_c4m8_available"] = min(
                    (avail_vcpus * 4 - avail_vcpus_used) / 4,
                    (avail_memory - avail_memory_used) / 8
                )
                if item["standard_c4m8_available"] < 1:
                    item["standard_c4m8_available"] = 0

        db_obj.append(item)

        try:
            clustername = models.cloud_cluster.objects.get(id=item["cluster"])
            item['cluster'] = clustername.cluster_name
        except models.cloud_cluster.DoesNotExist:
            pass

    return db_obj


def cluster_dashboard(request):
    dic = {"obj_info": get_cluster_resources()}
    cluster_obj = models.cloud_cluster.objects.all()
    for i in cluster_obj:
        compute_res = models.cloud_compute_resource.objects.filter(cluster=i).all()
        dic["compute_res"] = compute_res

    return render(request, 'openstack/cluster_dashboard.html', dic)


def cluster_member_info(request):
    compute_name = request.GET.get("node")
    member_res = models.cloud_vm_info.objects.filter(compute=compute_name).all()
    return render(request, 'openstack/cluster_member_info.html', {"member_res": member_res})


def vm_info(request):
    return render(request, 'openstack/vm_info.html')


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return super().default(obj)


def get_clustername(cluster_id):
    try:
        cluster = models.cloud_cluster.objects.get(id=cluster_id)
        return cluster.cluster_name
    except models.cloud_cluster.DoesNotExist:
        return ""


def vm_listdata(request):
    dic = {
        "code": 1,
        "msg": "",
        "count": 0,
        "data": []
    }
    search = request.GET.get("ip")
    current_page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)

    try:
        limit = int(limit)
        current_page = int(current_page)
    except (ValueError, TypeError):
        limit = 10
        current_page = 1

    datalist = []

    if search:
        vm_objs = models.cloud_vm_info.objects.filter(ip__contains=search).values()
        for data in vm_objs:
            data["clustername"] = get_clustername(data.get("cluster_name_id"))
            datalist.append(data)
        dic['data'] = datalist
        dic['count'] = len(datalist)
        dic['code'] = 0
        return HttpResponse(json.dumps(dic, cls=DateEncoder))

    cluster_objs = models.cloud_cluster.objects.all()
    for cluster in cluster_objs:
        vm_objs = models.cloud_vm_info.objects.filter(cluster_name=cluster).values()
        for data in vm_objs:
            data["clustername"] = cluster.cluster_name
            datalist.append(data)

    paginator = Paginator(datalist, limit)
    dic['data'] = list(paginator.get_page(current_page).object_list)
    dic['count'] = len(datalist)
    dic['code'] = 0
    return HttpResponse(json.dumps(dic, cls=DateEncoder))


def vm_add(request):
    clusters = list(models.cloud_cluster.objects.values_list('cluster_name', flat=True))
    flavors = list(models.cloud_flavor.values_list('flavor_name', flat=True))
    appnames = list(App_info.objects.values_list('enname', flat=True))
    envs = list(Envs.objects.values_list('name', flat=True))

    dic = {"envs": envs, "appname": appnames, "flavor": flavors, "cluster": clusters}
    return render(request, 'openstack/vm_add.html', dic)
