from django.conf import settings
from ipware import get_client_ip


def get_ip_address_from_request(request):
    """
    返回request里的IP地址
    提示：
        为了开发方便，这个函数会返回类似127.0.0.1之类无法在公网被路由的地址，
        在生产环境中，类似地址不会被返回
    """
    ip, is_routable = get_client_ip(request)
    if settings.DEBUG:
        return ip
    else:
        if ip is not None and is_routable:
            return ip
    return None
