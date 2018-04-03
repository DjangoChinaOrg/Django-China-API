import django_filters

from notifications.models import Notification


class NotificationFilter(django_filters.rest_framework.FilterSet):
    unread = django_filters.NullBooleanField(name='unread')

    class Meta:
        model = Notification
        fields = ['unread']
