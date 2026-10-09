from blog.models import Author, Profile, Category, Tag, Post, Comment

print('=== DATOS INICIALES ===')
print(f'Autores: {Author.objects.count()}')
print(f'Perfiles: {Profile.objects.count()}')
print(f'Categorías: {Category.objects.count()}')
print(f'Etiquetas: {Tag.objects.count()}')
print(f'Artículos: {Post.objects.count()}')
print(f'Comentarios: {Comment.objects.count()}')
print()
print('=== DETALLE POR AUTOR ===')
for a in Author.objects.prefetch_related('posts').all():
    print(f'{a.name}: {a.posts.count()} posts, tiene perfil: {hasattr(a, "profile")}')
print()
print('=== RELACIONES POST (muestras) ===')
for p in Post.objects.select_related('author', 'category').all()[:5]:
    print(f'{p.title} | autor={p.author.name} | cat={p.category.name if p.category else None} | tags={p.tags.count()}')
print()
print('=== COMENTARIOS DEL POST 1 ===')
post1 = Post.objects.get(pk=1)
comments = list(post1.comment_set.all())
for c in comments:
    print(f'  {c.pk}. [{c.author_name}] {c.text[:150]}...')
print()
print('=== POSTS CON CATEGORÍA NULA ===')
for p in Post.objects.filter(category__isnull=True):
    print(f'  {p.title}')
print()
print('=== POST 5 - COMENTARIOS ===')
post5 = Post.objects.get(pk=5)
comments5 = list(post5.comment_set.all())
print(f'Post 5 tiene {len(comments5)} comentarios')
for c in comments5:
    print(f'  {c.pk}. [{c.author_name}] {c.text[:100]}')
print()
print('=== CANTIDAD POR AUTOR DE COMENTARIOS ===')
for a in Author.objects.all():
    cnt = Comment.objects.filter(author_name=a.name).count()
    print(f'  {a.name}: {cnt} comentarios como autor_name')
