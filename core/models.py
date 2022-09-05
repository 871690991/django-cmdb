from ipaddress import ip_address
from django.db import models

# Create your models here.
class Idc_info(models.Model):
    name = models.CharField(u"机房名称", max_length=30,null=True,unique=True)
    address = models.CharField(u"机房地址", max_length=100, null=True)
    num = models.CharField(u"机房编号", max_length=30, null=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '机房管理'
        verbose_name_plural = verbose_name


biz_group_choice = (
(u'大数据部', u'大数据部'),
(u'系统运维部', u'系统运维部'),
(u'会员服务部', u'会员服务部'),

(u'ITBP项目部', u'ITBP项目部'),
(u'电商服务部', u'电商服务部'),
(u'财务服务部', u'财务服务部'),
(u'技术中台部', u'技术中台部'),
(u'业务中台部', u'业务中台部'),


)


class devgroup_name(models.Model):
    name = models.CharField(u"部门", max_length=30, null=True,unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '部门管理'
        verbose_name_plural = verbose_name


class Appdomain_info(models.Model):

    enname = models.CharField(u"产品线英文名", max_length=30,null=True,unique=True)
    cnname = models.CharField(u"产品线中文名", max_length=30,null=True)
    group = models.ForeignKey(to=devgroup_name,on_delete=models.DO_NOTHING)
    manager = models.CharField(u"负责人", max_length=30, null=True)

    def __str__(self):
        return self.enname

    class Meta:
        verbose_name = '产品线管理'
        verbose_name_plural = verbose_name



class App_info(models.Model):
    enname = models.CharField(u"应用英文名", max_length=30,null=True,unique=True)
    cnname = models.CharField(u"应用中文名", max_length=30,null=True)
    manager = models.CharField(u"负责人", max_length=30, null=True)
    appdomain_info = models.ForeignKey(to=Appdomain_info,on_delete=models.DO_NOTHING)
    def __str__(self):
        return self.enname

    class Meta:
        verbose_name = '应用管理'
        verbose_name_plural = verbose_name
class Server_status(models.Model):
    name = models.CharField(u"状态名", max_length=30,null=True,unique=True)

    def __str__(self):
            return self.name

    class Meta:
        verbose_name = '服务器状态管理'
        verbose_name_plural = verbose_name


class Envs(models.Model):
    name = models.CharField(u"环境名", max_length=30,null=True,unique=True)

    def __str__(self):
            return self.name

    class Meta:
        verbose_name = '环境管理'
        verbose_name_plural = verbose_name

class Server_info(models.Model):
    ip = models.CharField(u"业务ip", max_length=30,null=True,unique=True)
    hostname = models.CharField(u"主机名", max_length=100,null=True)
    managerip = models.CharField(u"管理ip", max_length=30, null=True,unique=True)
    status = models.ForeignKey(to=Server_status,on_delete=models.DO_NOTHING)
    env = models.ForeignKey(to=Envs,on_delete=models.DO_NOTHING)
    brand = models.CharField(u"机型", max_length=30, null=True)
    hardware_parameters = models.CharField(u"硬件配置", max_length=30, null=True)
    rittal = models.CharField(u"机柜", max_length=30, null=True)
    u_site = models.CharField(u"U位", max_length=30, null=True)
    sn = models.CharField(u"sn序列号", max_length=30, null=True)
    system = models.CharField(u"操作系统", max_length=30, null=True)
    buy_time = models.DateField(u"购买时间", blank=True, null=True)
    expire_date=models.DateField(u"过保时间", blank=True, null=True)
    app_info = models.ForeignKey(to=App_info,on_delete=models.DO_NOTHING)
    idc = models.ForeignKey(to=Idc_info,on_delete=models.DO_NOTHING)
    def __str__(self):
            return self.ip

    class Meta:
        verbose_name = '物理机管理'
        verbose_name_plural = verbose_name


class Vm_info(models.Model):
    ip = models.CharField(u"ip", max_length=30,null=True,unique=True)
    hostname = models.CharField(u"主机名", max_length=100,null=True)
    env = models.ForeignKey(to=Envs,on_delete=models.DO_NOTHING)
    status = models.ForeignKey(to=Server_status,on_delete=models.DO_NOTHING)
    hardware_parameters = models.CharField(u"硬件配置", max_length=30, null=True)
    system = models.CharField(u"操作系统", max_length=30, null=True)
    server= models.ForeignKey(to=Server_info,on_delete=models.DO_NOTHING)
    app_info = models.ForeignKey(to=App_info,on_delete=models.DO_NOTHING)
    idc = models.ForeignKey(to=Idc_info,on_delete=models.DO_NOTHING)
    def __str__(self):
            return self.ip

    class Meta:
        verbose_name = '虚拟机管理'
        verbose_name_plural = verbose_name



class myPermission(models.Model):
    name = models.CharField("权限名称", max_length=64)
    url = models.CharField('URL名称', max_length=255)
    describe = models.CharField('描述', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '权限表'
        verbose_name_plural = verbose_name
