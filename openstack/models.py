from django.db import models
from core.models import Idc_info
# Create your models here.


class cloud_cluster(models.Model):
    '''
    私有云集群
    '''
    cluster_name = models.CharField(u'集群名称', max_length=128, unique=True)
    bk_idc_id = models.ForeignKey(Idc_info, verbose_name=u'机房',on_delete=models.DO_NOTHING)
    auth_url = models.URLField(verbose_name=u'keystone认证地址')
    username = models.CharField(u'用户名', max_length=128)
    password = models.CharField(u'密码', max_length=128)
    project_name = models.CharField(u'项目名称', max_length=128)
    admin_password = models.CharField(u'管理员密码', max_length=128)
    user_domain_name = models.CharField(max_length=128, default="default")
    project_domain_name = models.CharField(max_length=128, default="default")

    def __str__(self):
        return self.cluster_name

    class Meta:
        verbose_name = '集群管理'
        verbose_name_plural = verbose_name


class cloud_compute_resource(models.Model):
    '''
    计算节点资源汇总
    '''
    cluster = models.ForeignKey(cloud_cluster, verbose_name=u'所属集群',on_delete=models.DO_NOTHING)
    host_ip = models.GenericIPAddressField(u'IP地址')
    hypervisor_hostname = models.CharField(u'节点名称', max_length=128)
    hypervisor_type = models.CharField(u'类型', max_length=128)
    node_id = models.CharField(u'计算节点ID', max_length=128)
    running_vms = models.IntegerField(u'虚拟机数量')
    state = models.CharField(u'当前状态', max_length=128)
    status = models.CharField(u'是否启用', max_length=128)
    vcpus = models.IntegerField(u'vcpus数量')
    vcpus_used = models.IntegerField(u'已使用vcpu')
    vcpus_used_percent = models.IntegerField(u'vcpu超配比')
    local_gb = models.IntegerField(u'磁盘')
    local_gb_used = models.IntegerField(u'已使用磁盘')
    local_gb_used_percent = models.IntegerField(u'磁盘使用率')
    memory_mb = models.IntegerField(u'内存')
    memory_mb_used = models.IntegerField(u'已使用内存')
    memory_mb_used_percent = models.IntegerField(u'内存使用率')




class cloud_network(models.Model):
    '''
    私有云网络
    '''
    cluster_name = models.ForeignKey(cloud_cluster,on_delete=models.DO_NOTHING)
    name = models.CharField(u'网络名称', max_length=64)
    network_id = models.CharField(max_length=64, unique=True)
    subnet = models.CharField(u'网段', max_length=64)
    total_num = models.IntegerField(u'IP地址数量')
    used_num = models.IntegerField(u'已使用IP地址数量')
    free_num = models.IntegerField(u'空闲IP地址数量')
    percent = models.IntegerField(u'使用率')

    def __str__(self):
        return "%s-%s" % (self.cluster_name, self.name)





class cloud_flavor(models.Model):
    '''
    私有云实例模版
    '''
    cluster_name = models.ForeignKey(cloud_cluster,on_delete=models.DO_NOTHING)

    flavor_name = models.CharField(u'模版名称', max_length=64)
    flavor_id = models.CharField(u'模版ID', max_length=64, unique=True)

    def __unicode__(self):
        return self.flavor_name

    
class cloud_vm_info(models.Model):
    '''
    私有云实例模版
    '''

    name = models.CharField(u'主机名', max_length=128)
    server_id = models.CharField(u'虚拟机ID', max_length=128, null=True, blank=True)
    flavor = models.CharField(u'类型', max_length=128)
    ip = models.GenericIPAddressField(u'IP地址', null=True, blank=True)
    cluster_name = models.ForeignKey(cloud_cluster, null=True, blank=True,on_delete=models.DO_NOTHING)
    status = models.CharField(u'状态', max_length=32, default='BUILDING')
    compute = models.CharField(u'宿主机', max_length=64, null=True, blank=True)
    date = models.DateField(u"创建时间", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '云主机'
        verbose_name_plural = verbose_name

