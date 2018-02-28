from django.contrib import admin
from .models import Post


# 显示文章后台
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_time', 'author']


admin.site.register(Post, PostAdmin)
