from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    DashboardTemplateView,
    ForbiddenTemplateView,
    LoginTemplateView,
    PasswordResetTemplateView,
    ProfileTemplateView,
    RegisterTemplateView,
    SessionsTemplateView,
    VerifyEmailConfirmView,
    VerifyEmailTemplateView,
)


urlpatterns = [
    path("", DashboardTemplateView.as_view(), name="dashboard"),
    path("login/", LoginTemplateView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", RegisterTemplateView.as_view(), name="register"),
    path("password-reset/", PasswordResetTemplateView.as_view(), name="password_reset"),
    path("verify-email/", VerifyEmailTemplateView.as_view(), name="verify_email"),
    path(
        "verify-email/<uidb64>/<token>/",
        VerifyEmailConfirmView.as_view(),
        name="verify_email_confirm",
    ),
    path("profile/", ProfileTemplateView.as_view(), name="profile"),
    path("sessions/", SessionsTemplateView.as_view(), name="sessions"),
    path("forbidden/", ForbiddenTemplateView.as_view(), name="forbidden"),
]
