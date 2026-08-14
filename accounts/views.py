import random

from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import UserRegistrationForm, VerifyCodeForm, UserLoginForm
from .models import OtpCode, User
from utils import send_otp_code


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})

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

        return render(request, self.template_name, {'form': self.form_class})


class UserRegistrationVerifyCodeView(View):
    form_class = VerifyCodeForm
    template_name = 'accounts/verify.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request):
        user_session = request.session["user_registration_info"]
        code_instance = OtpCode.objects.get(phone_number=user_session["phone_number"])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            expiration_time = code_instance.created_at + timedelta(minutes=2)
            if cd["code"] == code_instance.code and expiration_time > timezone.now():
                User.objects.create_user(phone_number=user_session["phone_number"], email=user_session["email"]
                                         , full_name=user_session["full_name"], password=user_session["password"])
                code_instance.delete()
                messages.success(request, 'you registered successfully', extra_tags="success")
                return redirect("home:home")
            else:
                messages.error(request, 'wrong/expire code', extra_tags="danger")
                return redirect("accounts:verify_code")

        return render(request, self.template_name, {'form': self.form_class})


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next', None)
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['phone_number'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'you are login successfully', extra_tags='success')
                if self.next:
                    return redirect(self.next)
                return redirect("home:home")
            else:
                messages.warning(request, 'phone number/password is wrong', extra_tags='warning')

        return render(request, self.template_name, {'form': self.form_class})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'you are logged out', extra_tags='success')
        return redirect("home:home")
