from kavenegar import KavenegarAPI
from django.contrib.auth.mixins import UserPassesTestMixin

def send_otp_code(phone_number, code):

    try:
        api = KavenegarAPI('your api code')
        params = {'sender': '******', 'receptor': phone_number, 'message': f'your code is {code}'}
        response = api.sms_send(params)
        print(response)

    except Exception as e:
        print(e)

class IsAdminUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin