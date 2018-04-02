import django_filters

from notifications.models import Notification


class NotificationFilter(django_filters.rest_framework.FilterSet):
    unread = django_filters.BooleanFilter()

    class Meta:
        model = Notification
        fields = ['unread']
