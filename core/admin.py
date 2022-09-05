from django.contrib import admin
from django.contrib.auth.models import Permission

# Register your models here.
from core.models import *
class Idc_infoAdmin(admin.ModelAdmin):
    list_display = ['name','address','num']	# 指定表中的字段进行展示
    # list_editable = ['phone_number','email']
admin.site.register(Idc_info,Idc_infoAdmin)
class devgroup_name_Admin(admin.ModelAdmin):
    list_display = ['name','id']	# 指定表中的字段进行展示

admin.site.register(devgroup_name,devgroup_name_Admin)


class Appdomain_info_Admin(admin.ModelAdmin):
    list_display = ['enname','cnname','group','manager']	


admin.site.register(Appdomain_info,Appdomain_info_Admin)


class App_info_Admin(admin.ModelAdmin):
    list_display = ['enname','cnname','manager','appdomain_info']	

admin.site.register(App_info,App_info_Admin)
class Server_info_Admin(admin.ModelAdmin):
    list_display = ['ip','managerip','status','env',]	


admin.site.register(Server_info,Server_info_Admin)


admin.site.register(Envs,devgroup_name_Admin)
admin.site.register(Server_status,devgroup_name_Admin)

class Vm_info_Admin(admin.ModelAdmin):
    list_display = ['ip','hostname','status','env','hardware_parameters','system','server','app_info','idc']	
admin.site.register(Vm_info,Vm_info_Admin)
admin.site.register(Permission)
admin.site.register(myPermission)

