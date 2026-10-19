"""Domain models for the Lab Blog.

The lab tables (Author, Profile, Category, Tag, Post, Comment) are kept from the
original exercise. On top of them the blog adds:

* a link between the native ``User`` and its ``Author``/``Profile``;
* an explicit many-to-many through model (``ArticleTag``) with its own data.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Author(models.Model):
    """A writer. It may (or may not) be linked to a login account."""

    name = models.CharField(max_length=100)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="author",
        help_text="Login account of the author, when it has one.",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Profile(models.Model):
    """One-to-one profile of an author."""

    author = models.OneToOneField(Author, on_delete=models.CASCADE, related_name="profile")
    country = models.CharField(max_length=60)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.author} ({self.country})"


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="posts"
    )
    tags = models.ManyToManyField(
        Tag, through="ArticleTag", blank=True, related_name="posts"
    )
    published = models.BooleanField(default=False)
    published_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("-published_at", "-id")

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.pk])

    def __str__(self):
        return self.title


class ArticleTag(models.Model):
    """Explicit through model for ``Post.tags``.

    It carries its own data (``added_at``) and forbids duplicate pairs.
    """

    article = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="tag_links")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="article_links")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-added_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("article", "tag"), name="unique_article_tag"
            )
        ]

    def __str__(self):
        return f"{self.article} -> {self.tag}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="comments",
    )
    author_name = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def clean(self):
        super().clean()
        if not self.text or not self.text.strip():
            raise ValidationError({"text": "El comentario no puede estar vacio."})

    def __str__(self):
        return f"{self.author_name}: {self.text[:40]}"
