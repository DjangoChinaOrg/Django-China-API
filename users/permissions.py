from rest_framework import permissions


class IsVerified(permissions.BasePermission):
    """
    设置主 email 时必须为已验证的 email
    """

    def has_object_permission(self, request, view, obj):
        if obj.verified:
            return True
        return False


class NotPrimary(permissions.BasePermission):
    """
    不能删除主 email
    """

    def has_object_permission(self, request, view, obj):
        if obj.primary:
            return False
        return True
