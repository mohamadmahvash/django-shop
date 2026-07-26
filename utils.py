from kavenegar import *


def send_otp_code(phone_number, code):

    try:
        api = KavenegarAPI('your api code')
        params = {'sender': '******', 'receptor': phone_number, 'message': f'your code is {code}'}
        response = api.sms_send(params)
        print(response)

    except Exception as e:
        print(e)
