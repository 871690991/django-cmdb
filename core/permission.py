from django.shortcuts import render
from django.http import JsonResponse
from . import models
from django.urls import resolve
from django.contrib.auth.models import Group
import logging

logger = logging.getLogger(__name__)


def perm_check(request):
    try:
        url_obj = resolve(request.path_info)
        url_name = url_obj.route

        if not url_name:
            return True

        if request.user.is_superuser:
            return True

        user_groups = request.user.groups.all()
        if user_groups.filter(name="admin").exists():
            return True

        get_perms = models.myPermission.objects.filter(url__contains=url_name)
        if not get_perms:
            return False

        for perm in get_perms:
            perm_str = "core." + perm.name
            if request.user.has_perm(perm_str):
                return True

        return False

    except Exception as e:
        logger.error(f"权限检查异常: {e}, path: {request.path_info}")
        return False


def check_permission(func):
    def wrapper(request, *args, **kwargs):
        if perm_check(request):
            return func(request, *args, **kwargs)
        return render(request, '403.html', {'error': '您没有权限访问此页面'})
    return wrapper
