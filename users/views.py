from allauth.account.views import ConfirmEmailView as AllAuthConfirmEmailView
from rest_framework_jwt.settings import api_settings


class ConfirmEmailView(AllAuthConfirmEmailView):
    template_name = 'email_confirm.html'

    def post(self, *args, **kwargs):
        response = super(ConfirmEmailView, self).post(*args, **kwargs)
        confirmation = self.get_object()

        # Insert JWT to cookie after a successful activation
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(confirmation.email_address.user)
        token = jwt_encode_handler(payload)
        response.set_cookie('JWT', token)
        return response
