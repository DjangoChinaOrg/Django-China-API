from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    """
    允许普通用户编辑自己的帖子，但不允许更改hidden, pinned, highlighted字段
    管理员可以编辑所有帖子
    """
    def has_object_permission(self, request, view, obj):
        no_forbidden_changes = True
        if request.data.get('hidden') is not None or \
                        request.data.get('pinned') is not None or \
                        request.data.get('highlighted') is not None:
            no_forbidden_changes = False
        return (request.method in permissions.SAFE_METHODS or
                request.user.is_staff or
                request.user == obj.author and
                no_forbidden_changes)
