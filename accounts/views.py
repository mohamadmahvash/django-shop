from django.shortcuts import render
from django.views import View
from .forms import UserRegistrationForm


class UserRegisterView(View):
    form_class = UserRegistrationForm

    def get(self, request):
        return render(request, 'accounts/register.html', {'form': self.form_class})

    def post(self, request):
        pass
