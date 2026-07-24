import random
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

from .forms import UserRegistrationForm, VerifyCodeForm
from .models import OtpCode, User
from utils import send_otp_code


class UserRegisterView(View):
    form_class = UserRegistrationForm

    def get(self, request):
        return render(request, 'accounts/register.html', {'form': self.form_class})

    def post(self, request):
        form = self.form_class = UserRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            random_code = random.randint(1000, 9999)
            send_otp_code(phone_number=cd["phone_number"], code=random_code)
            OtpCode.objects.create(phone_number=cd["phone_number"], code=random_code)
            request.session["user_registration_info"] = {
                "email": cd["email"],
                "full_name": cd["full_name"],
                "phone_number": cd["phone_number"],
                "password": cd["password"],
            }

            messages.success(request, 'we sent you a code', extra_tags="success")
            return redirect("accounts:verify_code")

        return render(request, 'accounts/register.html', {'form': self.form_class})


class UserRegistrationVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        return render(request, 'accounts/verify.html', {'form': self.form_class})

    def post(self, request):
        user_session = request.session["user_registration_info"]
        code_instance = OtpCode.objects.get(phone_number=user_session["phone_number"])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd["code"] == code_instance.code:
                User.objects.create_user(phone_number=user_session["phone_number"], email=user_session["email"]
                                         , full_name=user_session["full_name"], password=user_session["password"])
                code_instance.delete()
                messages.success(request, 'you registered successfully', extra_tags="success")
                return redirect("home:home")
            else:
                messages.error(request, 'wrong code', extra_tags="danger")
                return redirect("accounts:verify_code")

        return render(request, 'accounts/verify.html', {'form': self.form_class})
