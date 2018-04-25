from django.conf import settings
from rest_framework_jwt.serializers import RefreshJSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class JWTMiddleware(object):
    """
    将用户的Session状态和JWT同步的中间件
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not hasattr(request, 'user'):
            return response
        if request.user.is_authenticated():
            if response.status_code != 200:
                return response

            if 'JWT' in request.COOKIES:
                # 刷新JWT
                serializer = RefreshJSONWebTokenSerializer(
                    data={'token': request.COOKIES['JWT']})
                if serializer.is_valid():
                    jwt_and_user = serializer.object
                    if jwt_and_user['user'] == request.user:
                        jwt = jwt_and_user['token']
                    else:
                        jwt = jwt_encode_handler(jwt_payload_handler(request.user))
                else:
                    # 旧JWT无法解析的话，创建新的JWT
                    jwt = jwt_encode_handler(jwt_payload_handler(request.user))
            else:
                # JWT还不在cookie里的话，创建新的JWT
                jwt = jwt_encode_handler(jwt_payload_handler(request.user))

            response.set_cookie(
                'JWT',
                value=jwt,
                max_age=24 * 60 * 60
            )
        else:
            # 用户已经登出，清理掉JWT
            if 'JWT' in request.COOKIES:
                response.delete_cookie('JWT')
        return response
