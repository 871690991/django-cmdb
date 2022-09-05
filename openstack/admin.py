from django.contrib import admin
from openstack.models import *
# Register your models here.

class cloud_cluster_Admin(admin.ModelAdmin):
    list_display = ['cluster_name']


admin.site.register(cloud_cluster,cloud_cluster_Admin)
admin.site.register(cloud_compute_resource)
admin.site.register(cloud_network)
admin.site.register(cloud_flavor)
admin.site.register(cloud_vm_info)