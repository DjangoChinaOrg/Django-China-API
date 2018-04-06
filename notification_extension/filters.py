import django_filters

from notifications.models import Notification


class NotificationFilter(django_filters.rest_framework.FilterSet):
    unread = django_filters.filters.CharFilter(method='unread_filter')

    def unread_filter(self, queryset, name, value):
        if value == 'true':
            return queryset.filter(unread='True')
        elif value == 'false':
            return queryset.filter(unread='False')
        elif value == 'all':
            return queryset
        else:
            return queryset.none()

    class Meta:
        model = Notification
        fields = ['unread']
