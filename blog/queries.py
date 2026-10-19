"""Queries behind the views. Part 2 of the lab happens in this file."""
from blog.models import Post


def posts_for_front_page():
    # The template walks `post.author`, `post.category` and `post.tags` once per
    # post. Without the joins below the number of queries grows with the number
    # of posts (the N+1 problem). select_related covers the FKs and
    # prefetch_related the many-to-many, so the page needs exactly 2 queries.
    return (
        Post.objects.filter(published=True)
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-published_at")
    )
