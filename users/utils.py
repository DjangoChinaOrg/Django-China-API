from django.conf import settings
from ipware import get_client_ip


def get_ip_address_from_request(request):
    """
    Return IP address from given request
    NOTICE: for dev purpose, this method will return
    non-routable IP addresses like 127.0.0.1, will return None on production
    """
    ip, is_routable = get_client_ip(request)
    if settings.DEBUG:
        return ip
    else:
        if ip is not None and is_routable:
            return ip
    return None
