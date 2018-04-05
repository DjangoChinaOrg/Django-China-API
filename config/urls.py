from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import refresh_jwt_token

from posts.views import PostViewSet
from tags.views import TagViewSet
from replies.api.views import ReplyViewSet
from users.views import UserViewSets
from users.views import ConfirmEmailView

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'tags', TagViewSet)
router.register(r'replies', ReplyViewSet)
router.register(r'users', UserViewSets)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        ConfirmEmailView.as_view(),
        name='account_confirm_email'),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^rest-auth/jwt-refresh/', refresh_jwt_token),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),  # 仅仅用于测试
    url(r'^', include(router.urls)),
]
