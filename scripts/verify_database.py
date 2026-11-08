import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from blog.models import Author, Profile, Category, Tag, Post, Comment

print('=== DATOS INICIALES ===')
print(f'Autores: {Author.objects.count()}')
print(f'Perfiles: {Profile.objects.count()}')
print(f'Categorias: {Category.objects.count()}')
print(f'Etiquetas: {Tag.objects.count()}')
print(f'Articulos: {Post.objects.count()}')
print(f'Comentarios: {Comment.objects.count()}')
print()

print('=== DETALLE POR AUTOR ===')
for a in Author.objects.prefetch_related('posts').all():
    has_profile = hasattr(a, 'profile')
    print(f'{a.name}: {a.posts.count()} posts, tiene perfil: {has_profile}')
print()

print('=== CATEGORIAS EXISTENTES ===')
for c in Category.objects.all():
    print(f'  pk={c.pk}. {c.name}')
print()

print('=== ETIQUETAS EXISTENTES ===')
for t in Tag.objects.all():
    print(f'  pk={t.pk}. {t.name}')
print()

print('=== POSTS ORDENADOS POR PK (top 5) ===')
for p in Post.objects.order_by('pk')[:5]:
    cat_name = p.category.name if p.category else None
    print(f'  pk={p.pk} | {p.title} | autor={p.author.name} | cat={cat_name} | tags={p.tags.count()} | published_at={p.published_at}')
print()

print('=== POSTS CON CATEGORIA NULA ===')
null_cat = list(Post.objects.filter(category__isnull=True).values_list('pk', 'title', 'author__name'))
if null_cat:
    for pk, title, author in null_cat:
        print(f'  pk={pk} | {title} | autor={author}')
else:
    print('  Ninguno')
print()

print('=== COMENTARIOS DEL PRIMER POST (pk menor) ===')
first_post = Post.objects.order_by('pk').first()
print(f'Primer post pk={first_post.pk}: {first_post.title}')
comments = list(first_post.comments.all())
print(f'Tiene {len(comments)} comentarios:')
for c in comments:
    short_text = c.text.replace('\n', ' ')[:200]
    print(f'  pk={c.pk} | [{c.author_name}] {short_text}')
print()

print('=== TODOS LOS COMENTARIOS (para buscar hostil) ===')
all_comments = list(Comment.objects.order_by('pk').values_list('pk', 'post_id', 'author_name', 'text'))
for pk, post_id, author, text in all_comments:
    clean = text.replace('\n', ' ')
    print(f'  pk={pk} | post={post_id} | {author}: {clean[:120]}')
print()

print('=== RELACIONES VERIFICADAS ===')
# OneToOne: Author <-> Profile
for a in Author.objects.all():
    try:
        prof = a.profile
        print(f'  Author {a.name} -> Profile(country={prof.country})')
    except Profile.DoesNotExist:
        print(f'  Author {a.name} -> NO TIENE profile')
print()

# FK: Post -> Author
print('  Post -> Author (FK, related_name=posts):')
for p in Post.objects.all()[:3]:
    print(f'    {p.title} -> {p.author.name}')
print()

# Optional FK: Post -> Category
print('  Post -> Category (FK null=True, related_name=posts):')
for p in Post.objects.all()[:5]:
    cat = f'{p.category.name}' if p.category else 'NULL'
    print(f'    {p.title} -> {cat}')
print()

# M2M: Post <-> Tag
print('  Post <-> Tag (M2M, related_name=posts):')
for p in Post.objects.all()[:3]:
    tag_names = list(p.tags.values_list('name', flat=True))
    print(f'    {p.title} -> tags={tag_names}')
print()

# FK: Comment -> Post
print('  Comment -> Post (FK, related_name=comments):')
for c in Comment.objects.all()[:5]:
    print(f'    pk={c.pk} -> post.pk={c.post.pk}')
