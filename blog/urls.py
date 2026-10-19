from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.front_page, name="front_page"),

    # Posts
    path("articulos/", views.PostListView.as_view(), name="post_list"),
    path("articulos/nuevo/", views.PostCreateView.as_view(), name="post_create"),
    path("articulos/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("articulos/<int:pk>/editar/", views.PostUpdateView.as_view(), name="post_update"),
    path("articulos/<int:pk>/eliminar/", views.PostDeleteView.as_view(), name="post_delete"),
    path("articulos/<int:pk>/comentar/", views.comment_create, name="comment_create"),
    path("comentarios/<int:pk>/eliminar/", views.CommentDeleteView.as_view(), name="comment_delete"),

    # Authentication
    path("entrar/", views.BlogLoginView.as_view(), name="login"),
    path("salir/", views.BlogLogoutView.as_view(), name="logout"),
    path("registro/", views.SignUpView.as_view(), name="register"),

    # Profile
    path("perfil/", views.ProfileDetailView.as_view(), name="profile"),
    path("perfil/editar/", views.ProfileUpdateView.as_view(), name="profile_edit"),

    # Categories
    path("categorias/", views.CategoryListView.as_view(), name="category_list"),
    path("categorias/nueva/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categorias/<int:pk>/editar/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categorias/<int:pk>/eliminar/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # Tags
    path("etiquetas/", views.TagListView.as_view(), name="tag_list"),
    path("etiquetas/nueva/", views.TagCreateView.as_view(), name="tag_create"),
    path("etiquetas/<int:pk>/editar/", views.TagUpdateView.as_view(), name="tag_update"),
    path("etiquetas/<int:pk>/eliminar/", views.TagDeleteView.as_view(), name="tag_delete"),
]
