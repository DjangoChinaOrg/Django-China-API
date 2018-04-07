from django.utils import timezone
from rest_framework import permissions

from ..models import Record


class OncePerDay(permissions.BasePermission):
    """
    一天内（0:00：00-23:59:59）用户只能签到一次
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            # 获取用户最近一次签到记录
            # 不存在则说明用户从未签到
            latest_record = request.user.record_set.latest('created_time')
        except Record.DoesNotExist:
            return True

        # 获取当天的开始和结束时间
        today_start = timezone.now().replace(hour=0, minute=0, second=0)
        today_end = timezone.now().replace(hour=23, minute=59, second=59)

        if today_start <= latest_record.created_time <= today_end:
            return False

        return True


class IsCurrentUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
