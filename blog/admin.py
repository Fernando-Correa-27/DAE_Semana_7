"""Django admin configuration for the Lab Blog.

Each model gets a purpose-built ModelAdmin: useful columns, filters, searches,
related inlines and autocomplete widgets. Relations are edited from the parent
screen (comments and tag links from the post, the profile from the author).
"""
from django.contrib import admin
from django.db.models import Count

from .models import ArticleTag, Author, Category, Comment, Post, Profile, Tag


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


class ArticleTagInline(admin.TabularInline):
    """Manage the tags of a post through the explicit through model."""

    model = ArticleTag
    extra = 1
    autocomplete_fields = ("tag",)
    readonly_fields = ("added_at",)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("author_name", "user", "text", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "country", "post_count")
    search_fields = ("name", "user__username")
    list_select_related = ("user",)
    autocomplete_fields = ("user",)
    inlines = (ProfileInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "profile")
            .annotate(_posts=Count("posts"))
        )

    @admin.display(description="Pais", ordering="profile__country")
    def country(self, obj):
        return getattr(obj.profile, "country", "-") if hasattr(obj, "profile") else "-"

    @admin.display(description="Articulos", ordering="_posts")
    def post_count(self, obj):
        return obj._posts


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("author", "country")
    search_fields = ("author__name", "country")
    list_select_related = ("author",)
    autocomplete_fields = ("author",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "post_count")
    search_fields = ("name",)
    ordering = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_posts=Count("posts"))

    @admin.display(description="Articulos", ordering="_posts")
    def post_count(self, obj):
        return obj._posts


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "post_count")
    search_fields = ("name",)
    ordering = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_posts=Count("posts"))

    @admin.display(description="Articulos", ordering="_posts")
    def post_count(self, obj):
        return obj._posts


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "published", "published_at", "comment_count", "tag_count")
    list_filter = ("published", "category", "author", "tags")
    search_fields = ("title", "body", "author__name")
    list_select_related = ("author", "category")
    ordering = ("-published_at", "-id")
    date_hierarchy = "published_at"
    autocomplete_fields = ("author", "category")
    inlines = (ArticleTagInline, CommentInline)
    fieldsets = (
        ("Contenido", {"fields": ("title", "body")}),
        ("Clasificacion", {"fields": ("author", "category")}),
        ("Publicacion", {"fields": ("published", "published_at")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author", "category")
            .annotate(
                _comments=Count("comments", distinct=True),
                _tags=Count("tags", distinct=True),
            )
        )

    @admin.display(description="Comentarios", ordering="_comments")
    def comment_count(self, obj):
        return obj._comments

    @admin.display(description="Etiquetas", ordering="_tags")
    def tag_count(self, obj):
        return obj._tags


@admin.register(ArticleTag)
class ArticleTagAdmin(admin.ModelAdmin):
    list_display = ("article", "tag", "added_at")
    list_filter = ("tag",)
    search_fields = ("article__title", "tag__name")
    list_select_related = ("article", "tag")
    autocomplete_fields = ("article", "tag")
    date_hierarchy = "added_at"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("short_text", "post", "user", "author_name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text", "author_name", "post__title")
    list_select_related = ("post", "user")
    autocomplete_fields = ("post",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)

    @admin.display(description="Comentario")
    def short_text(self, obj):
        return obj.text[:60]
