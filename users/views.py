from allauth.account.views import ConfirmEmailView as AllAuthConfirmEmailView
from rest_framework_jwt.settings import api_settings


class ConfirmEmailView(AllAuthConfirmEmailView):
    """
    用户点击Email里的激活链接后跳转的视图
    """
    template_name = 'email_confirm.html'

    def post(self, *args, **kwargs):
        response = super(ConfirmEmailView, self).post(*args, **kwargs)
        confirmation = self.get_object()

        # 成功激活用户以后生成新的JWT并放到Cookie里
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(confirmation.email_address.user)
        token = jwt_encode_handler(payload)
        response.set_cookie('JWT', token)
        return response
