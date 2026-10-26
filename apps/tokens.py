from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Token becomes invalid immediately after the account is activated."""

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.password}{user.last_login}{timestamp}{user.email}{user.is_active}"

    def check_token(self, user, token):
        if not (user and token):
            return False

        try:
            timestamp, _ = token.split("-")
            timestamp = int(timestamp, 36)
        except (ValueError, TypeError):
            return False

        if not constant_time_compare(
            self._make_token_with_timestamp(user, timestamp, self.secret), token
        ):
            if not any(
                constant_time_compare(
                    self._make_token_with_timestamp(user, timestamp, secret), token
                )
                for secret in self.secret_fallbacks
            ):
                return False

        return self._num_seconds(self._now()) - timestamp <= settings.EMAIL_VERIFICATION_TIMEOUT


email_verification_token_generator = EmailVerificationTokenGenerator()
