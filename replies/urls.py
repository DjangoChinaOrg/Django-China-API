from django.conf.urls import url, include

from . import views

app_name = 'replies'
urlpatterns = [
    url(r'^$', views.ReplyCreateView.as_view(), name='create_reply'),

    # 以下两条 API 仅用于测试
    url(r'^flat-list/$', views.FlatReplyListView.as_view(), name='flat_reply_list'),
    url(r'^tree-list/$', views.TreeReplyListView.as_view(), name='tree_reply_list'),
]
