from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('verify/', views.UserRegistrationVerifyCodeView.as_view(), name='verify_code'),
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('passwordreset/', views.UserResetPasswordView.as_view(), name='user_reset_password'),
    path('passwordreset/done/', views.UserResetPasswordDoneView.as_view(), name='user_reset_password_done'),
    path('passwordreset/confirm/<uidb64>/<token>/', views.UserResetPasswordConfirmView.as_view(),
         name='user_reset_password_confirm'),
    path('passwordreset/complete/', views.UserResetPasswordCompleteView.as_view(),
         name='user_reset_password_complete'),
    path('upload-avatar/', views.UserUploadAvatarView.as_view(), name='upload_avatar'),
]
