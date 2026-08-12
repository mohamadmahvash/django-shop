from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User, OtpCode


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number']

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords must match')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text="<a href=\"../password/\"> change password </a>")

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'password', 'last_login','is_superuser']


class UserRegistrationForm(forms.Form):
    email = forms.EmailField(label='Email')
    full_name = forms.CharField(label='Full Name')
    phone_number = forms.CharField(label='Phone Number', max_length=11)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError('This Email already exist')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        user = User.objects.filter(phone_number=phone_number).exists()
        if user:
            raise ValidationError('This Phone Number already exist')
        OtpCode.objects.filter(phone_number=phone_number).delete()
        return phone_number


class UserLoginForm(forms.Form):
    phone_number = forms.CharField(label='Phone Number', max_length=11)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class VerifyCodeForm(forms.Form):
    code = forms.IntegerField(label='Verification Code')
