from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    """
    允许普通用户编辑帖子
    管理可以编辑、删除帖子
    """
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS or
                request.user.is_staff or
                request.user == obj.author)
