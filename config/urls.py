from rest_framework_jwt.views import refresh_jwt_token

from users.views import ConfirmEmailView

"""DjangoChina URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from posts.views import PostViewSet
from tags.views import TagViewSet


router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        ConfirmEmailView.as_view(),
        name='account_confirm_email'),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^rest-auth/jwt-refresh/', refresh_jwt_token),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^replies/', include('replies.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),  # 仅仅用于测试
    url(r'^', include(router.urls)),
]
