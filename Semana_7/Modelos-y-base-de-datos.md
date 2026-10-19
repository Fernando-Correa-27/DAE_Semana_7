# Modelos y Base de Datos

> Definiciones ORM, relaciones y migraciones. Refleja `blog/models.py` tal como
> quedó tras la transformación en blog funcional.

---

## Entidades (Models)

### Author (`blog.Author`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `BigAutoField` | PK |
| `name` | `CharField(100)` | Requerido |
| `user` | `OneToOneField(AUTH_USER_MODEL)` | `null`, `blank`, `on_delete=SET_NULL`, `related_name="author"` |

**Meta:** `ordering = ("name",)`. El login es opcional: un autor puede existir
sin cuenta y conservarse si la cuenta se borra (`SET_NULL`).

---

### Profile (`blog.Profile`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `BigAutoField` | PK |
| `author` | `OneToOneField(Author)` | `on_delete=CASCADE`, `related_name="profile"` |
| `country` | `CharField(60)` | Requerido |
| `bio` | `TextField` | `blank` |

**Relación:** uno-a-uno con `Author`.

---

### Category (`blog.Category`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `BigAutoField` | PK |
| `name` | `CharField(60)` | Requerido, `unique` |

**Meta:** `ordering = ("name",)`.

---

### Tag (`blog.Tag`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `BigAutoField` | PK |
| `name` | `CharField(40)` | Requerido, `unique` |

**Meta:** `ordering = ("name",)`.

---

### Post (`blog.Post`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `BigAutoField` | PK |
| `title` | `CharField(200)` | Requerido |
| `body` | `TextField` | `blank` |
| `author` | `ForeignKey(Author)` | `on_delete=CASCADE`, `related_name="posts"` |
| `category` | `ForeignKey(Category)` | `null`, `blank`, `on_delete=SET_NULL`, `related_name="posts"` |
| `tags` | `ManyToMany(Tag)` | **through** `ArticleTag`, `blank`, `related_name="posts"` |
| `published` | `BooleanField` | `default=False` |
| `published_at` | `DateField` | `null`, `blank` |

**Meta:** `ordering = ("-published_at", "-id")`.
**`get_absolute_url()`:** `reverse("blog:post_detail", args=[self.pk])`.
**Relación:** autor (N:1), categoría (N:1), etiquetas (M:N vía `ArticleTag`).

---

### ArticleTag (`blog.ArticleTag`) — modelo intermedio explícito
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `BigAutoField` | PK |
| `article` | `ForeignKey(Post)` | `on_delete=CASCADE`, `related_name="tag_links"` |
| `tag` | `ForeignKey(Tag)` | `on_delete=CASCADE`, `related_name="article_links"` |
| `added_at` | `DateTimeField` | `auto_now_add` |

**Meta:** `ordering = ("-added_at",)` y
`UniqueConstraint(fields=("article","tag"), name="unique_article_tag")`.
Aporta datos propios (`added_at`) y prohíbe pares duplicados.

---

### Comment (`blog.Comment`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `BigAutoField` | PK |
| `post` | `ForeignKey(Post)` | `on_delete=CASCADE`, `related_name="comments"` |
| `user` | `ForeignKey(AUTH_USER_MODEL)` | `null`, `blank`, `on_delete=SET_NULL`, `related_name="comments"` |
| `author_name` | `CharField(100)` | Requerido (nombre mostrado) |
| `text` | `TextField` | Requerido |
| `created_at` | `DateTimeField` | `auto_now_add` |

**Meta:** `ordering = ("created_at",)`.
**`clean()`:** rechaza `text` vacío o solo espacios (`ValidationError`).

---

## Relaciones entre entidades

```
User     1──1 Author 1──1 Profile
Author   1──N Post
Category 1──N Post
Post     N──N Tag      (a través de ArticleTag)
Post     1──N Comment
User     1──N Comment  (opcional)
```

## Migraciones

- `blog/migrations/0001_initial.py` — esquema original del laboratorio.
- `blog/migrations/0002_alter_author_options_alter_category_options_and_more.py`
  — escrito a mano porque Django no permite pasar de una M2M normal a una con
  `through` mediante `AlterField`. Pasos: `AddField` de `Author.user` y
  `Comment.user`, `CreateModel ArticleTag` + `AddConstraint`, `RunPython`
  (copia `blog_post_tags` → `blog_articletag`), `RemoveField` + `AddField` de
  `Post.tags`. Reversible.

## Datos de prueba (`blog/seed_data.py`)

| Entidad | Cantidad | Notas |
|---------|----------|-------|
| Authors | 4 | Ana Quispe, Beto Salas, Carla Rojas, Diego Pinto |
| Categories | 4 | Tecnología, Cultura, Deportes, Opinión |
| Tags | 5 | django, python, orm, noticias, tutorial |
| Posts | 15 | 11 publicados y 4 borradores |
| Comments | 23 | El 4.º del primer artículo es hostil (prompt injection) |

> `seed_data.py` calcula las respuestas del oráculo en Python puro (sin ORM), lo
> que permite saber de antemano la respuesta correcta de cada pregunta.

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Arquitectura-del-proyecto]]
- [[Consultas-ORM-y-Duelo]]
- [[Management-Commands]]
- [[Pruebas-Automatizadas]]
- [[Observaciones-y-Pendientes]]
- [[Blog-Funcionalidades]]
