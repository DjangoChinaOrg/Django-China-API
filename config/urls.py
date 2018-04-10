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
from allauth.account.views import email_verification_sent
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import refresh_jwt_token

from posts.views import PostViewSet
from replies.api.views import ReplyViewSet
from tags.views import TagViewSet
from users.views import (
    ConfirmEmailView, EmailAddressViewSet, GitHubLogin, LoginViewCustom, RegisterViewCustom,
    UserViewSets)

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'tags', TagViewSet)
router.register(r'replies', ReplyViewSet)
router.register(r'users', UserViewSets)
router.register(r'users/email', EmailAddressViewSet,base_name='email')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        ConfirmEmailView.as_view(),
        name='account_confirm_email'),
    url(r"^rest-auth/confirm-email/$", email_verification_sent,
        name="account_email_verification_sent"),
    url(r'^rest-auth/registration/$', RegisterViewCustom.as_view(), name='rest_register'),
    url(r'^rest-auth/login/$', LoginViewCustom.as_view(), name='rest_login'),
    url(r'^rest-auth/login/github/$', GitHubLogin.as_view(), name='github_login'),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^rest-auth/jwt-refresh/', refresh_jwt_token),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),  # 仅仅用于测试
    url(r'^', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
