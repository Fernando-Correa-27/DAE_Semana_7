import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from blog.models import Post, Comment

print(f'Post count: {Post.objects.count()}')
print(f'Comment count: {Comment.objects.count()}')
print(f'Post PKs: {list(Post.objects.values_list("pk", flat=True))}')
print(f'Comment PKs: {list(Comment.objects.values_list("pk", flat=True))}')
