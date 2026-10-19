# Consultas ORM y Duelo

> Comparativa entre las respuestas humanas y las de la IA para ocho preguntas
> sobre el ORM de Django. Base: `blog/duel/`.

---

## Estructura

| Archivo | Propósito |
|---------|-----------|
| `blog/duel/questions.py` | Las 8 preguntas, su respuesta esperada (oráculo en Python puro) y el presupuesto de consultas |
| `blog/duel/runner.py` | Ejecuta cada respuesta, la compara con el oráculo y cuenta las consultas SQL |
| `blog/duel/team.py` | Respuestas del equipo (funciones `q1`..`q8`) |
| `blog/duel/ai_answers.py` | Respuestas de la IA, tal como las escribió |

El oráculo se calcula desde `blog/seed_data.py` con Python puro (sin ORM), así que
la respuesta correcta se conoce de antemano.

---

## Las 8 preguntas y las respuestas del equipo

| q | Pregunta | Respuesta del equipo | 1ª consulta |
|---|----------|----------------------|-------------|
| q1 | Artículos publicados | `Post.objects.filter(published=True)` | 1 |
| q2 | Artículos sin categoría | `Post.objects.filter(category__isnull=True)` | 1 |
| q3 | Publicados entre 2026-03-01 y 2026-05-31 (ambos incluidos) | `filter(published=True, published_at__gte=date(2026,3,1), published_at__lte=date(2026,5,31))` | 1 |
| q4 | Artículos con más de 2 comentarios | `annotate(n_comments=Count("comments")).filter(n_comments__gt=2)` | 1 |
| q5 | Top 3 publicados por comentarios, con `n_comments` y `n_tags` | `annotate(n_comments=Count("comments", distinct=True), n_tags=Count("tags", distinct=True)).order_by("-n_comments")[:3]` | 1 |
| q6 | Artículos de autores de Perú | `Post.objects.filter(author__profile__country="Perú")` | 1 |
| q7 | Comentarios de artículos de «Tecnología» | `Comment.objects.filter(post__category__name="Tecnología")` | 1 |
| q8 | Autores que nunca publicaron | `Author.objects.exclude(posts__published=True).distinct()` | 1 |

---

## Resultado del duelo

### Equipo (`python manage.py duel`)

```
q1 [OK] 1  q2 [OK] 1  q3 [OK] 1  q4 [OK] 1
q5 [OK] 1  q6 [OK] 1  q7 [OK] 1  q8 [OK] 1
8 de 8 correctas y baratas.
```

### IA (`python manage.py duel --source ai`)

| q | Estado | Consultas | Problema |
|---|--------|-----------|----------|
| q1 | OK | 1 | — |
| q2 | OK | 1 | — |
| q3 | wrong | 1 | `published_at__gt` / `__lt` (excluye fronteras) → faltan 2 artículos |
| q4 | costly | 16 | filtra en Python con `post.comments.count()` (N+1) |
| q5 | wrong | 1 | `Count` sin `distinct=True` → números inflados (18/12/8 vs 6/4/3) |
| q6 | error | 0 | `author__country` no existe (`FieldError`; el campo está en `Profile`) |
| q7 | OK | 1 | — |
| q8 | wrong | 1 | `filter(posts__published=False)` incluye autores con borradores |

**Resultado: equipo 8/8 correctas y baratas vs IA 3/8.**

---

## Análisis de los fallos de la IA

| q | Error | Corrección |
|---|-------|------------|
| q3 | Límites exclusivos (`gt`/`lt`) | `gte`/`lte` (el enunciado dice "ambos días incluidos") |
| q4 | Filtrado en Python | `annotate(Count("comments")).filter(...)` en una consulta |
| q5 | `Count` sin `distinct=True` | añadir `distinct=True` para no contar filas duplicadas por los JOINs |
| q6 | `author__country` | `author__profile__country` (el país vive en `Profile`) |
| q8 | `filter(posts__published=False)` | `exclude(posts__published=True).distinct()` |

### SQL que lo justifica (q8)

```
TEAM: SELECT DISTINCT ... FROM blog_author
      WHERE NOT (EXISTS(SELECT 1 FROM blog_post U1
                        WHERE U1.published AND U1.author_id = blog_author.id LIMIT 1))

AI  : SELECT ... FROM blog_author
      INNER JOIN blog_post ON blog_author.id = blog_post.author_id
      WHERE NOT blog_post.published
```

El equipo usa `NOT EXISTS` (autor sin ningún post publicado); la IA usa un `JOIN`
que selecciona autores con algún borrador, no los que nunca publicaron.

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Management-Commands]]
- [[Pruebas-Automatizadas]]
- [[Observaciones-y-Pendientes]]
