from django.contrib import admin
from .models import Post,  ProgressBar, Support


# 显示文章后台
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_time', 'author']


class ProgressBarAdmin(admin.ModelAdmin):
    list_display = ['title', 'progress', 'remarks']


class SupportAdmin(admin.ModelAdmin):
    list_display = ['name', 'money', 'date']


admin.site.register(Post, PostAdmin)
admin.site.register(ProgressBar, ProgressBarAdmin)
admin.site.register(Support, SupportAdmin)
