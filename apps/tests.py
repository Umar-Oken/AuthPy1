from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import User


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegistrationVerificationTests(TestCase):
    registration_data = {
        "first_name": "Jasurbek",
        "last_name": "Bekmirzayev",
        "email": "student@example.com",
        "password1": "Tr!9qL5vP8mz",
        "password2": "Tr!9qL5vP8mz",
        "terms": "on",
    }

    def test_registration_sends_verification_email_and_link_is_single_use(self):
        response = self.client.post(reverse("register"), self.registration_data)

        self.assertRedirects(response, reverse("verify_email"))
        user = User.objects.get(email="student@example.com")
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Verify Email", mail.outbox[0].alternatives[0].content)

        verification_url = next(
            line for line in mail.outbox[0].body.splitlines() if line.startswith("http")
        )
        first_use = self.client.get(verification_url)
        self.assertRedirects(first_use, reverse("login"))
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        second_use = self.client.get(verification_url)
        self.assertRedirects(second_use, reverse("login"))
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_settings(
        ALLOWED_HOSTS=["attacker.example"],
        PUBLIC_ORIGIN="https://auth.example.com",
    )
    def test_verification_link_uses_configured_origin_not_request_host(self):
        self.client.post(
            reverse("register"),
            self.registration_data,
            HTTP_HOST="attacker.example",
        )

        verification_url = next(
            line for line in mail.outbox[0].body.splitlines() if line.startswith("http")
        )
        self.assertTrue(verification_url.startswith("https://auth.example.com/"))

    def test_registration_rejects_an_existing_email_ignoring_case(self):
        User.objects.create_user(
            email="student@example.com",
            password="Tr!9qL5vP8mz",
        )
        duplicate_data = {**self.registration_data, "email": "Student@Example.com"}

        response = self.client.post(reverse("register"), duplicate_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "allaqachon mavjud")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="jasurbek@example.com",
            password="Tr!9qL5vP8mz",
            first_name="Jasurbek",
            last_name="Bekmirzayev",
            is_active=True,
        )

    def test_invalid_credentials_return_401_without_creating_a_session(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.user.email, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertContains(response, "Email yoki parol noto‘g‘ri.", status_code=401)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_valid_credentials_create_session_and_show_authenticated_user_name(self):
        response = self.client.post(
            reverse("login"),
            {"email": "JASURBEK@EXAMPLE.COM", "password": "Tr!9qL5vP8mz"},
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(str(self.user.pk), self.client.session["_auth_user_id"])

        dashboard = self.client.get(reverse("dashboard"))
        self.assertContains(dashboard, "Jasurbek Bekmirzayev")
        self.assertContains(dashboard, "Salom, Jasurbek!")

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")


class UserAdminTests(TestCase):
    def test_superuser_can_see_registered_users_in_admin(self):
        User.objects.create_user(
            email="student@example.com",
            password="Tr!9qL5vP8mz",
            first_name="Student",
            last_name="User",
        )
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="Tr!9qL5vP8mz",
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin:apps_user_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "student@example.com")
