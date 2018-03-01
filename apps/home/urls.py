from django.conf.urls import url
from . import views

app_name = 'home'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^posts/$', views.PostListView.as_view(), name='posts'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='post'),
    url(r'^support/$', views.SupportView.as_view(), name='support'),
]