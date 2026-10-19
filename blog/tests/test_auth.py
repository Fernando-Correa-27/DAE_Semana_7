"""Authentication flow: registration, login, logout and the own profile."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blog.models import Author, Profile


class SignUpTests(TestCase):
    url = reverse("blog:register")

    def test_registration_creates_user_author_and_profile(self):
        response = self.client.post(
            self.url,
            {
                "username": "nuevo",
                "first_name": "Nuevo",
                "last_name": "Usuario",
                "email": "nuevo@example.com",
                "country": "Peru",
                "password1": "clave-segura-123",
                "password2": "clave-segura-123",
            },
        )
        self.assertRedirects(response, reverse("blog:front_page"))
        user = User.objects.get(username="nuevo")
        self.assertEqual(user.email, "nuevo@example.com")
        self.assertEqual(user.author.name, "Nuevo Usuario")
        self.assertEqual(user.author.profile.country, "Peru")

    def test_registration_logs_the_user_in(self):
        self.client.post(
            self.url,
            {
                "username": "nuevo",
                "email": "nuevo@example.com",
                "password1": "clave-segura-123",
                "password2": "clave-segura-123",
            },
        )
        response = self.client.get(reverse("blog:profile"))
        self.assertEqual(response.status_code, 200)

    def test_registration_cannot_grant_staff_or_superuser(self):
        self.client.post(
            self.url,
            {
                "username": "listillo",
                "email": "x@example.com",
                "password1": "clave-segura-123",
                "password2": "clave-segura-123",
                "is_staff": "on",
                "is_superuser": "on",
            },
        )
        user = User.objects.get(username="nuevo" if False else "listillo")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_duplicated_email_is_rejected(self):
        User.objects.create_user("otro", email="dup@example.com", password="x")
        response = self.client.post(
            self.url,
            {
                "username": "nuevo",
                "email": "dup@example.com",
                "password1": "clave-segura-123",
                "password2": "clave-segura-123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="nuevo").exists())


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", password="clave-segura-123")

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("blog:login"), {"username": "ana", "password": "clave-segura-123"}
        )
        self.assertRedirects(response, reverse("blog:front_page"))

    def test_login_with_wrong_password_keeps_anonymous(self):
        response = self.client.post(
            reverse("blog:login"), {"username": "ana", "password": "nope"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post_and_ends_the_session(self):
        self.client.login(username="ana", password="clave-segura-123")
        self.assertEqual(self.client.get(reverse("blog:logout")).status_code, 405)
        response = self.client.post(reverse("blog:logout"))
        self.assertRedirects(response, reverse("blog:front_page"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", password="clave-segura-123")

    def test_profile_requires_login(self):
        response = self.client.get(reverse("blog:profile"))
        self.assertRedirects(
            response, f"{reverse('blog:login')}?next={reverse('blog:profile')}"
        )

    def test_visiting_profile_creates_author_and_profile_if_missing(self):
        self.client.login(username="ana", password="clave-segura-123")
        self.client.get(reverse("blog:profile"))
        self.assertTrue(Author.objects.filter(user=self.user).exists())
        self.assertTrue(Profile.objects.filter(author__user=self.user).exists())

    def test_profile_edit_updates_name_and_country(self):
        self.client.login(username="ana", password="clave-segura-123")
        response = self.client.post(
            reverse("blog:profile_edit"),
            {"name": "Ana Actualizada", "country": "Chile", "bio": "Hola", "email": "ana@example.com"},
        )
        self.assertRedirects(response, reverse("blog:profile"))
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.author.name, "Ana Actualizada")
        self.assertEqual(user.author.profile.country, "Chile")
        self.assertEqual(user.email, "ana@example.com")
