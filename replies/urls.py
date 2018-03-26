from django.conf.urls import url, include

from . import views

app_name = 'replies'
urlpatterns = [
    url(r'^$', views.ReplyCreationView.as_view(), name='create_reply'),
]
