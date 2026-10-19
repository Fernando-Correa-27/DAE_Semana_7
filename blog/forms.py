"""Forms for authentication and the blog CRUD.

Everything inherits from Django's own forms so validation, password hashing and
CSRF keep working out of the box. The only customisation is cosmetic (Bootstrap
classes) plus the rule that a public registration can never grant staff or
superuser rights.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Author, Category, Comment, Post, Profile, Tag


class StyledFormMixin:
    """Adds Bootstrap-friendly classes to every widget of a form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")
            if field.required:
                widget.attrs.setdefault("aria-required", "true")


class SignUpForm(StyledFormMixin, UserCreationForm):
    """Public registration. Never exposes is_staff / is_superuser / permissions."""

    first_name = forms.CharField(max_length=150, required=False, label="Nombre")
    last_name = forms.CharField(max_length=150, required=False, label="Apellidos")
    email = forms.EmailField(label="Correo electronico")
    country = forms.CharField(max_length=60, required=False, label="Pais")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
            self._sync_author(user)
        return user

    def _sync_author(self, user):
        name = f"{user.first_name} {user.last_name}".strip() or user.username
        country = self.cleaned_data.get("country", "").strip() or "Sin especificar"
        author, _ = Author.objects.get_or_create(
            user=user, defaults={"name": name}
        )
        Profile.objects.get_or_create(
            author=author, defaults={"country": country}
        )


class LoginForm(StyledFormMixin, AuthenticationForm):
    """Authentication form with the shared styling."""


class PostForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "body", "category", "tags", "published", "published_at")
        widgets = {
            "published_at": forms.DateInput(attrs={"type": "date"}),
            "body": forms.Textarea(attrs={"rows": 10}),
        }


class StaffPostForm(PostForm):
    """Editors and admins may also choose who the article is attributed to."""

    class Meta(PostForm.Meta):
        fields = ("title", "body", "author", "category", "tags", "published", "published_at")


class CommentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {"text": forms.Textarea(attrs={"rows": 3, "placeholder": "Escribe un comentario..."})}
        labels = {"text": ""}

    def clean_text(self):
        text = self.cleaned_data.get("text", "").strip()
        if not text:
            raise forms.ValidationError("El comentario no puede estar vacio.")
        return text


class ProfileForm(StyledFormMixin, forms.ModelForm):
    """Edits the profile plus the linked author name / user email."""

    name = forms.CharField(max_length=100, label="Nombre publico")
    email = forms.EmailField(label="Correo electronico", required=False)

    class Meta:
        model = Profile
        fields = ("country", "bio")
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["name"].initial = self.instance.author.name
            user = self.instance.author.user
            if user is not None:
                self.fields["email"].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.author.name = self.cleaned_data["name"]
        author = self.instance.author
        if commit:
            author.save()
            profile.save()
            user = author.user
            if user is not None:
                user.email = self.cleaned_data["email"]
                user.save(update_fields=["email"])
        return profile


class CategoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)


class TagForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Tag
        fields = ("name",)
