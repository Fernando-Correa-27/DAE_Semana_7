"""Authorisation tests: native permissions plus ownership rules."""
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from blog.models import Author, Category, Comment, Post, Tag


def make_user(username, group=None, **extra):
    user = User.objects.create_user(username, password="clave-segura-123", **extra)
    if group:
        user.groups.add(Group.objects.get(name=group))
    return user


class BaseAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_groups", verbosity=0)
        cls.author = Author.objects.create(name="Autora")
        cls.published = Post.objects.create(
            title="Publicado", author=cls.author, published=True
        )
        cls.draft = Post.objects.create(
            title="Borrador secreto", author=cls.author, published=False
        )

    def test_anonymous_sees_only_published_posts(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertContains(response, "Publicado")
        self.assertNotContains(response, "Borrador secreto")

    def test_anonymous_cannot_open_a_draft(self):
        response = self.client.get(reverse("blog:post_detail", args=[self.draft.pk]))
        self.assertEqual(response.status_code, 404)

    def test_editor_sees_the_drafts_too(self):
        make_user("editor", group="Editor")
        self.client.login(username="editor", password="clave-segura-123")
        response = self.client.get(reverse("blog:post_list"))
        self.assertContains(response, "Borrador secreto")


class PostPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_groups", verbosity=0)

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("blog:login"), response.url)

    def test_registered_without_permission_is_forbidden(self):
        make_user("lector", group="Usuario registrado")
        self.client.login(username="lector", password="clave-segura-123")
        response = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 403)

    def test_editor_can_open_the_create_form(self):
        make_user("editor", group="Editor")
        self.client.login(username="editor", password="clave-segura-123")
        response = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 200)


class CategoryTagPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_groups", verbosity=0)
        cls.category = Category.objects.create(name="Noticias")
        cls.tag = Tag.objects.create(name="django")

    def test_registered_cannot_manage_categories(self):
        make_user("lector", group="Usuario registrado")
        self.client.login(username="lector", password="clave-segura-123")
        self.assertEqual(self.client.get(reverse("blog:category_create")).status_code, 403)
        self.assertEqual(
            self.client.get(reverse("blog:category_update", args=[Category.objects.first().pk])).status_code,
            403,
        )

    def test_editor_can_create_a_category(self):
        make_user("editor", group="Editor")
        self.client.login(username="editor", password="clave-segura-123")
        response = self.client.post(reverse("blog:category_create"), {"name": "Deportes"})
        self.assertRedirects(response, reverse("blog:category_list"))
        self.assertTrue(Category.objects.filter(name="Deportes").exists())

    def test_editor_can_create_a_tag(self):
        make_user("editor", group="Editor")
        self.client.login(username="editor", password="clave-segura-123")
        response = self.client.post(reverse("blog:tag_create"), {"name": "orm"})
        self.assertRedirects(response, reverse("blog:tag_list"))
        self.assertTrue(Tag.objects.filter(name="orm").exists())


class CommentOwnershipTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_groups", verbosity=0)
        cls.author = Author.objects.create(name="Autora")
        cls.post = Post.objects.create(
            title="Publicado", author=cls.author, published=True
        )

    def setUp(self):
        self.owner = make_user("owner_user")
        self.other = make_user("other_user", group="Usuario registrado")
        self.editor = make_user("editor_user", group="Editor")
        self.comment = Comment.objects.create(
            post=self.post, user=self.owner, author_name="owner_user", text="hola"
        )

    def test_owner_can_open_the_delete_page(self):
        self.client.login(username="owner_user", password="clave-segura-123")
        response = self.client.get(reverse("blog:comment_delete", args=[self.comment.pk]))
        self.assertEqual(response.status_code, 200)

    def test_other_registered_user_is_redirected(self):
        self.client.login(username="other_user", password="clave-segura-123")
        response = self.client.get(reverse("blog:comment_delete", args=[self.comment.pk]))
        self.assertRedirects(
            response, reverse("blog:post_detail", args=[self.post.pk])
        )
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_editor_with_permission_can_delete(self):
        self.client.login(username="editor_user", password="clave-segura-123")
        response = self.client.post(reverse("blog:comment_delete", args=[self.comment.pk]))
        self.assertRedirects(
            response, reverse("blog:post_detail", args=[self.post.pk])
        )
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_anonymous_is_sent_to_login(self):
        response = self.client.get(reverse("blog:comment_delete", args=[self.comment.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("blog:login"), response.url)


class CommentCreateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_groups", verbosity=0)
        cls.user = make_user("comentarista", group="Usuario registrado")
        cls.author = Author.objects.create(name="Autora")
        cls.post = Post.objects.create(
            title="Publicado", author=cls.author, published=True
        )

    def test_registered_user_can_comment(self):
        self.client.login(username="comentarista", password="clave-segura-123")
        response = self.client.post(
            reverse("blog:comment_create", args=[self.post.pk]), {"text": "Buen aporte"}
        )
        self.assertRedirects(response, reverse("blog:post_detail", args=[self.post.pk]))
        comment = Comment.objects.get(post=self.post)
        self.assertEqual(comment.text, "Buen aporte")
        self.assertEqual(comment.user, self.user)

    def test_anonymous_cannot_comment(self):
        response = self.client.post(
            reverse("blog:comment_create", args=[self.post.pk]), {"text": "hola"}
        )
        self.assertRedirects(response, reverse("blog:login"))
        self.assertEqual(Comment.objects.count(), 0)

    def test_blank_comment_is_rejected(self):
        self.client.login(username="comentarista", password="clave-segura-123")
        self.client.post(
            reverse("blog:comment_create", args=[self.post.pk]), {"text": "   "}
        )
        self.assertEqual(Comment.objects.count(), 0)
