from django.contrib import admin
from django.urls import include, path

from blog import views as blog_views

urlpatterns = [
    path("admin/", admin.site.urls),
    # The home is also exposed with the plain name "front_page" for backwards
    # compatibility with the original lab test (blog/tests/test_front_page.py).
    path("", blog_views.front_page, name="front_page"),
    path("", include("blog.urls", namespace="blog")),
]
