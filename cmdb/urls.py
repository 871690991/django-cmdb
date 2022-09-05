"""cmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views,cmdb,server
from openstack import vmapi
from django.urls import path,include,re_path
from django.views.static import serve
from cmdb import settings

#cmdb/add_idc/,cmdb/add_appdomain/,cmdb/add_appinfo/,cmdb/add_appinfo/,server/add_host/,server/add_vm/
urlpatterns = [


    re_path(r'^$', views.index),
    path('admin/', admin.site.urls),
    path("index/", views.index),
    path('login/', views.login),
    path('logout/', views.logout),
    path('editpassword/', views.editpassword),
    path('get_navs/', views.get_navs),

    path('cmdb/idc/', cmdb.idc),
    path('cmdb/add_idc/', cmdb.idcadd),
    path('cmdb/edit_idc/', cmdb.idcedit),
    path('cmdb/del_idc/', cmdb.idcdel),

    path('cmdb/get_groups/',cmdb.get_groups),
    path('cmdb/get_appdomain/',cmdb.get_appdomain),

    path('cmdb/appdomain/',cmdb.appdomain),
    path('cmdb/add_appdomain/',cmdb.appdomainadd),
    path('cmdb/del_appdomain/',cmdb.appdomaindel),
    path('cmdb/edit_appdomain/',cmdb.appdomainedit),
    path('cmdb/appinfo/',cmdb.app_info),
    path('cmdb/appnameinfo/',cmdb.appname_infodata),

    path('cmdb/add_appinfo/', cmdb.app_infoadd),
    path('cmdb/del_appinfo/',cmdb.appinfodel),
    path('cmdb/edit_appinfo/',cmdb.appinfoedit),

    path('api/idc_info/', cmdb.idc_info),

    path('api/appdomain_info/', cmdb.appdomain_info),
    path('api/app_info/', cmdb.app_infodata),
    path('api/server_info/', server.server_info),
    path('api/getserverinfo/',server.serverhost_info),
    path('api/getvminfo/',server.vmhost_info),

    path('register/', views.register),



    path('server/host/',server.server),
    path('server/add_host/',server.server_infoadd),
    path('server/del_host/',server.server_infodel),
    path('server/edit_host/',server.server_infoedit),
    path('server/info/',server.host_info),

    path('server/vm/',server.vm),
    path('server/add_vm/',server.vm_infoadd),
    path('server/del_vm/',server.vm_infodel),
    path('server/edit_vm/',server.vm_infoedit),
    path('server/getvm_info/',server.getvm_info),

    path('api/vm_info/', server.vm_info),
    path('server/find_vmlist/',server.vm_list),

    path('sync_openstack_data/',vmapi.sync_openstack_data),

    path('cloud/cluster/dashboard/', vmapi.cluster_dashboard),
    path('cloud/cluster/member/',vmapi.cluster_member_info),
    path('cloud/vm/index/',vmapi.vm_info),
    path('cloud/vm/add/',vmapi.vm_add),

    path('cloud/api/vmlist/',vmapi.vm_listdata)

    # path('logout/', views.logout),
    # path('captcha/',include('captcha.urls')),
    # path('confirm/',views.user_confirm),
]

# if settings.DEBUG ==False:
#         urlpatterns.append(re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}))