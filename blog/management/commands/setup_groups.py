"""Create (idempotently) the access groups of the Lab Blog.

Run it after migrating:  python manage.py setup_groups

Groups and what they can do:
    Visitante            read published content only (no write permissions)
    Usuario registrado   read + comment + edit own profile
    Editor               full CRUD on posts, comments, categories and tags
    Administrador        every permission of the blog app

Nothing here grants is_staff / is_superuser: those are set per user by an
administrator. The command can be run as many times as needed.
"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from blog.models import ArticleTag, Category, Comment, Post, Tag

READ = ("view",)
WRITE = ("add", "change", "delete", "view")

GROUPS = {
    "Visitante": {
        Post: READ,
        Category: READ,
        Tag: READ,
        Comment: READ,
        ArticleTag: READ,
    },
    "Usuario registrado": {
        Post: READ,
        Category: READ,
        Tag: READ,
        Comment: ("add", "view"),
        ArticleTag: READ,
    },
    "Editor": {
        Post: WRITE,
        Category: WRITE,
        Tag: WRITE,
        Comment: WRITE,
        ArticleTag: ("add", "delete", "view"),
    },
    "Administrador": {
        Post: WRITE,
        Category: WRITE,
        Tag: WRITE,
        Comment: WRITE,
        ArticleTag: WRITE,
    },
}


def permissions_for(model, actions):
    model_name = model._meta.model_name
    content_type = ContentType.objects.get_for_model(model)
    codenames = [f"{action}_{model_name}" for action in actions]
    return Permission.objects.filter(content_type=content_type, codename__in=codenames)


class Command(BaseCommand):
    help = "Crea o actualiza los grupos y permisos del Lab Blog."

    def handle(self, *args, **options):
        for name, spec in GROUPS.items():
            group, _ = Group.objects.get_or_create(name=name)
            permissions = Permission.objects.none()
            for model, actions in spec.items():
                permissions = permissions | permissions_for(model, actions)
            group.permissions.set(permissions)
            self.stdout.write(
                self.style.SUCCESS(f"{name}: {group.permissions.count()} permisos")
            )
        self.stdout.write(self.style.SUCCESS("Grupos del Lab Blog listos."))
