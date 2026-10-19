"""Views for the Lab Blog.

Public reading (posts, categories, tags) + authenticated participation
(comments, own profile) + editor/admin management (post, category, tag CRUD).

Authorisation is always enforced on the server: permissions via the native
Django system and ownership checks where content belongs to a user.
"""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import (
    CategoryForm,
    CommentForm,
    LoginForm,
    PostForm,
    ProfileForm,
    SignUpForm,
    StaffPostForm,
    TagForm,
)
from .models import Author, Category, Comment, Post, Profile, Tag
from .queries import posts_for_front_page


def author_for_user(user):
    """Return (creating if needed) the Author linked to a login account."""
    author = getattr(user, "author", None)
    if author is None:
        name = user.get_full_name().strip() or user.username
        author = Author.objects.create(name=name, user=user)
        Profile.objects.get_or_create(
            author=author, defaults={"country": "Sin especificar"}
        )
    return author


def front_page(request):
    # Kept intentionally lean: the lab test `test_front_page_runs_two_queries`
    # requires the public home to run exactly two queries.
    return render(
        request,
        "blog/front_page.html",
        {"posts": posts_for_front_page(), "now": timezone.now()},
    )


# --- Authentication -------------------------------------------------------


class BlogLoginView(LoginView):
    template_name = "blog/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Sesion iniciada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contrasena incorrectos.")
        return super().form_invalid(form)


class BlogLogoutView(LogoutView):
    next_page = reverse_lazy("blog:front_page")


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "blog/register.html"
    success_url = reverse_lazy("blog:front_page")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("blog:front_page")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Cuenta creada. Ya tienes la sesion iniciada.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los datos: no se pudo crear la cuenta.")
        return super().form_invalid(form)


# --- Posts ---------------------------------------------------------------


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        qs = (
            Post.objects.select_related("author", "category")
            .prefetch_related("tags")
            .annotate(comment_count=Count("comments"))
            .order_by("-published_at", "-id")
        )
        if not self.request.user.has_perm("blog.change_post"):
            qs = qs.filter(published=True)
        return qs


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        qs = (
            Post.objects.select_related("author__profile", "category")
            .prefetch_related("tags", "comments__user")
        )
        if not self.request.user.has_perm("blog.change_post"):
            qs = qs.filter(published=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("user")
        return context


class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    template_name = "blog/post_form.html"
    permission_required = "blog.add_post"
    success_url = reverse_lazy("blog:post_list")

    def get_form_class(self):
        return StaffPostForm if self.request.user.is_staff else PostForm

    def form_valid(self, form):
        if not self.request.user.is_staff:
            form.instance.author = author_for_user(self.request.user)
        messages.success(self.request, "Articulo creado correctamente.")
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    template_name = "blog/post_form.html"
    permission_required = "blog.change_post"
    success_url = reverse_lazy("blog:post_list")

    def get_form_class(self):
        return StaffPostForm if self.request.user.is_staff else PostForm

    def form_valid(self, form):
        messages.success(self.request, "Articulo actualizado correctamente.")
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    permission_required = "blog.delete_post"
    success_url = reverse_lazy("blog:post_list")

    def form_valid(self, form):
        messages.success(self.request, "Articulo eliminado.")
        return super().form_valid(form)


# --- Comments ------------------------------------------------------------


@require_POST
def comment_create(request, pk):
    post = Post.objects.filter(pk=pk).first()
    if post is None or (not post.published and not request.user.has_perm("blog.change_post")):
        messages.error(request, "No puedes comentar este articulo.")
        return redirect("blog:post_list")
    if not request.user.is_authenticated:
        return redirect("blog:login")

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.author_name = (
            author_for_user(request.user).name
            if getattr(request.user, "author", None)
            else request.user.get_full_name() or request.user.username
        )
        comment.full_clean()
        comment.save()
        messages.success(request, "Comentario publicado.")
    else:
        messages.error(request, "El comentario no puede estar vacio.")
    return redirect("blog:post_detail", pk=post.pk)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "blog/comment_confirm_delete.html"

    def get_queryset(self):
        return Comment.objects.select_related("post")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        comment = self.get_object()
        owns = comment.user_id == request.user.id
        if not (owns or request.user.has_perm("blog.delete_comment")):
            messages.error(request, "No puedes eliminar un comentario ajeno.")
            return redirect("blog:post_detail", pk=comment.post_id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"pk": self.object.post_id})

    def form_valid(self, form):
        messages.success(self.request, "Comentario eliminado.")
        return super().form_valid(form)


# --- Profile -------------------------------------------------------------


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "blog/profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        author = author_for_user(self.request.user)
        profile, _ = Profile.objects.get_or_create(
            author=author, defaults={"country": "Sin especificar"}
        )
        return profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "blog/profile_form.html"
    context_object_name = "profile"
    success_url = reverse_lazy("blog:profile")

    def get_object(self, queryset=None):
        author = author_for_user(self.request.user)
        profile, _ = Profile.objects.get_or_create(
            author=author, defaults={"country": "Sin especificar"}
        )
        return profile

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado.")
        return super().form_valid(form)


# --- Categories and tags -------------------------------------------------


class CategoryListView(ListView):
    model = Category
    template_name = "blog/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.annotate(post_count=Count("posts")).order_by("name")


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "blog/category_form.html"
    permission_required = "blog.add_category"
    success_url = reverse_lazy("blog:category_list")

    def form_valid(self, form):
        messages.success(self.request, "Categoria creada.")
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "blog/category_form.html"
    permission_required = "blog.change_category"
    success_url = reverse_lazy("blog:category_list")

    def form_valid(self, form):
        messages.success(self.request, "Categoria actualizada.")
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = "blog/category_confirm_delete.html"
    permission_required = "blog.delete_category"
    success_url = reverse_lazy("blog:category_list")

    def form_valid(self, form):
        messages.success(self.request, "Categoria eliminada.")
        return super().form_valid(form)


class TagListView(ListView):
    model = Tag
    template_name = "blog/tag_list.html"
    context_object_name = "tags"

    def get_queryset(self):
        return Tag.objects.annotate(post_count=Count("posts")).order_by("name")


class TagCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = "blog/tag_form.html"
    permission_required = "blog.add_tag"
    success_url = reverse_lazy("blog:tag_list")

    def form_valid(self, form):
        messages.success(self.request, "Etiqueta creada.")
        return super().form_valid(form)


class TagUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = "blog/tag_form.html"
    permission_required = "blog.change_tag"
    success_url = reverse_lazy("blog:tag_list")

    def form_valid(self, form):
        messages.success(self.request, "Etiqueta actualizada.")
        return super().form_valid(form)


class TagDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Tag
    template_name = "blog/tag_confirm_delete.html"
    permission_required = "blog.delete_tag"
    success_url = reverse_lazy("blog:tag_list")

    def form_valid(self, form):
        messages.success(self.request, "Etiqueta eliminada.")
        return super().form_valid(form)
