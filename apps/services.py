from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token_generator


def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token_generator.make_token(user)
    verification_path = reverse(
        "verify_email_confirm", kwargs={"uidb64": uid, "token": token}
    )
    verification_url = f"{settings.PUBLIC_ORIGIN}{verification_path}"
    context = {
        "user": user,
        "verification_url": verification_url,
        "verification_timeout_hours": settings.EMAIL_VERIFICATION_TIMEOUT // 3600,
    }
    text_body = render_to_string("emails/verify_email.txt", context)
    html_body = render_to_string("emails/verify_email.html", context)

    email = EmailMultiAlternatives(
        subject="AuthLab — Email manzilingizni tasdiqlang",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
