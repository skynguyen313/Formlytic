from unicodedata import name
from django.urls import path
from .views import (
        RegisterView, 
        VerifyUserEmail,
        LoginUserView,
        ForgotPasswordView,
        ForgotPasswordResetConfirmView,  
        PasswordResetRequestView,
        PasswordResetConfirmView,
        LogoutApiView)

from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginUserView.as_view(), name='login_user'),
    path('forgot-password/', ForgotPasswordView.as_view(),name='forgot_password'),
    path('forgot-password-reset-confirm/', ForgotPasswordResetConfirmView.as_view(), name='forgot-password_reset_confirm'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', LogoutApiView.as_view(), name='logout')
    ]