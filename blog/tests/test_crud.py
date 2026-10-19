"""CRUD flows exercised through the HTTP layer, as an Editor would use them."""
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from blog.models import Author, Category, Comment, Post, Tag


class PostCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_groups", verbosity=0)
        cls.category = Category.objects.create(name="Noticias")

    def setUp(self):
        self.editor = User.objects.create_user("editor", password="clave-segura-123")
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.client.login(username="editor", password="clave-segura-123")

    def test_editor_creates_a_post_and_becomes_its_author(self):
        response = self.client.post(
            reverse("blog:post_create"),
            {
                "title": "Nuevo articulo",
                "body": "Contenido",
                "category": self.category.pk,
                "published": "on",
            },
        )
        self.assertRedirects(response, reverse("blog:post_list"))
        post = Post.objects.get(title="Nuevo articulo")
        self.assertEqual(post.author.user, self.editor)
        self.assertTrue(post.published)

    def test_editor_updates_a_post(self):
        author = Author.objects.create(name="Autora")
        post = Post.objects.create(title="Viejo", author=author)
        response = self.client.post(
            reverse("blog:post_update", args=[post.pk]),
            {
                "title": "Renombrado",
                "body": "x",
                "category": self.category.pk,
                "published": "on",
            },
        )
        self.assertRedirects(response, reverse("blog:post_list"))
        post.refresh_from_db()
        self.assertEqual(post.title, "Renombrado")

    def test_editor_deletes_a_post(self):
        author = Author.objects.create(name="Autora")
        post = Post.objects.create(title="Adios", author=author)
        response = self.client.post(reverse("blog:post_delete", args=[post.pk]))
        self.assertRedirects(response, reverse("blog:post_list"))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())


class CategoryTagCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_groups", verbosity=0)

    def setUp(self):
        self.editor = User.objects.create_user("editor", password="clave-segura-123")
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.client.login(username="editor", password="clave-segura-123")

    def test_category_lifecycle(self):
        self.client.post(reverse("blog:category_create"), {"name": "Deportes"})
        category = Category.objects.get(name="Deportes")
        self.client.post(
            reverse("blog:category_update", args=[category.pk]),
            {"name": "Deportes y mas"},
        )
        category.refresh_from_db()
        self.assertEqual(category.name, "Deportes y mas")
        self.client.post(reverse("blog:category_delete", args=[category.pk]))
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())

    def test_tag_lifecycle(self):
        self.client.post(reverse("blog:tag_create"), {"name": "orm"})
        tag = Tag.objects.get(name="orm")
        self.client.post(reverse("blog:tag_update", args=[tag.pk]), {"name": "django-orm"})
        tag.refresh_from_db()
        self.assertEqual(tag.name, "django-orm")
        self.client.post(reverse("blog:tag_delete", args=[tag.pk]))
        self.assertFalse(Tag.objects.filter(pk=tag.pk).exists())


class PostDetailTemplateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_groups", verbosity=0)
        cls.author = Author.objects.create(name="Autora")
        cls.post = Post.objects.create(
            title="Titulo visible", body="Cuerpo", author=cls.author, published=True
        )
        cls.tag = Tag.objects.create(name="python")
        cls.post.tags.add(cls.tag)
        Comment.objects.create(
            post=cls.post, author_name="Lectora", text="Muy bueno"
        )

    def test_detail_shows_body_tags_and_comments(self):
        response = self.client.get(reverse("blog:post_detail", args=[self.post.pk]))
        self.assertContains(response, "Titulo visible")
        self.assertContains(response, "Cuerpo")
        self.assertContains(response, "python")
        self.assertContains(response, "Muy bueno")

    def test_detail_hides_the_comment_form_from_anonymous(self):
        response = self.client.get(reverse("blog:post_detail", args=[self.post.pk]))
        self.assertNotContains(response, "Publicar comentario")
