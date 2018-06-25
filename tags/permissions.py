from rest_framework import permissions


class TagPermissionOrReadOnly(permissions.IsAdminUser):
    """
    仅允许管理员添加标签，（以后可添加普通用户的权限管理），其他用户只读
    """
    def has_permission(self, request, view):
        return (super(TagPermissionOrReadOnly, self).has_permission(request, view) or
                request.method in permissions.SAFE_METHODS)
