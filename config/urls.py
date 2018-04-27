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
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import refresh_jwt_token
from rest_auth.registration.views import (
    SocialAccountListView, SocialAccountDisconnectView
)

from notifications_extension.views import NotificationViewSet
from posts.views import PostViewSet
from replies.views import ReplyViewSet
from tags.views import TagViewSet
from users.views import (
    EmailAddressViewSet,
    LoginViewCustom,
    RegisterViewCustom,
    ConfirmEmailView,
    UserViewSets,
    GitHubLogin,
    GitHubConnect
)

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'tags', TagViewSet)
router.register(r'replies', ReplyViewSet)
router.register(r'users', UserViewSets)
router.register(r'users/email', EmailAddressViewSet,base_name='email')
router.register(r'notifications', NotificationViewSet, base_name='notifications')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^rest-auth/login/$', LoginViewCustom.as_view(), name='rest_login'),
    url(r'^rest-auth/registration/$', RegisterViewCustom.as_view(), name='rest_register'),
    url(r'^rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        ConfirmEmailView.as_view(),
        name='account_confirm_email'),
    url(r'^rest-auth/github/login/$', GitHubLogin.as_view(), name='github_login'),
    url(r'^rest-auth/github/connect/$', GitHubConnect.as_view(), name='github_connect'),
    url(r'^rest-auth/socialaccounts/$',
        SocialAccountListView.as_view(),
        name='social_account_list'),
    url(r'^rest-auth/socialaccounts/(?P<pk>\d+)/disconnect/$',
        SocialAccountDisconnectView.as_view(),
        name='social_account_disconnect'),
    url(r'^rest-auth/jwt-refresh/', refresh_jwt_token),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),  # 仅仅用于测试
    url(r'^', include(router.urls)),
    url(r'^docs/', include_docs_urls(title='Django中文社区 API'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
