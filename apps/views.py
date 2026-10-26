from binascii import Error as BinasciiError
import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView

from .forms import LoginForm, RegistrationForm
from .services import send_verification_email
from .tokens import email_verification_token_generator


User = get_user_model()
logger = logging.getLogger(__name__)


class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"


class LoginTemplateView(FormView):
    template_name = "login.html"
    form_class = LoginForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.get_user())
        if not form.cleaned_data["remember_me"]:
            self.request.session.set_expiry(0)
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        # Noto‘g‘ri credential login sessiyasi yaratmaydi va mijozga 401 qaytaradi.
        response = super().form_invalid(form)
        response.status_code = 401
        return response

    def get_success_url(self):
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return reverse("dashboard")


class RegisterTemplateView(FormView):
    template_name = "register.html"
    form_class = RegistrationForm

    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = form.save()
                send_verification_email(user)
        except Exception:
            logger.exception("Email verification message could not be sent")
            form.add_error(None, "Tasdiqlash xatini yuborib bo‘lmadi. Iltimos, qayta urinib ko‘ring.")
            return self.form_invalid(form)

        self.request.session["pending_verification_email"] = user.email
        return redirect("verify_email")


class PasswordResetTemplateView(TemplateView):
    template_name = "password_reset.html"


class VerifyEmailTemplateView(TemplateView):
    template_name = "verify_email.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.request.session.get("pending_verification_email")
        return context


class VerifyEmailConfirmView(View):
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
        except (TypeError, ValueError, OverflowError, BinasciiError):
            user_id = None

        verified = False
        if user_id:
            with transaction.atomic():
                try:
                    user = User.objects.select_for_update().get(pk=user_id)
                except User.DoesNotExist:
                    user = None

                if user and not user.is_active and email_verification_token_generator.check_token(user, token):
                    user.is_active = True
                    user.save(update_fields=["is_active"])
                    verified = True

        if verified:
            request.session.pop("pending_verification_email", None)
            messages.success(request, "Email manzilingiz tasdiqlandi. Endi hisobingizga kiring.")
        else:
            messages.error(request, "Tasdiqlash havolasi yaroqsiz, eskirgan yoki avval ishlatilgan.")

        return redirect("login")


class ProfileTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"


class SessionsTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "sessions.html"


class ForbiddenTemplateView(TemplateView):
    template_name = "403.html"
