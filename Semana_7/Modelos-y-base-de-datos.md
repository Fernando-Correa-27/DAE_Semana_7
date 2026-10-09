# Modelos y Base de Datos

> Definiciones ORM, relaciones y migraciones.

---

## Entidades (Models)

### Author (`blog.Author`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `AutoField` | PK |
| `name` | `CharField(150)` | Requerido |
| `email` | `EmailField(250)` | Requerido, único |
| `created_at` | `DateTimeField` | Auto-now-add (creación) |
| `updated_at` | `DateTimeField` | Auto-now (actualización) |

**Representación:** `"{name} <{email}>"`

---

### Profile (`blog.Profile`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `AutoField` | PK |
| `user` | `OneToOne(Author)` | PK + FK único, on_delete=CASCADE |
| `bio` | `TextField` | Opcional |
| `avatar` | `ImageField(upload_to="avatars/")` | Opcional |

**Relación:** Uno-a-uno con `Author`.

---

### Category (`blog.Category`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `AutoField` | PK |
| `name` | `CharField(100)` | Requerido, único |

---

### Tag (`blog.Tag`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `AutoField` | PK |
| `name` | `CharField(50)` | Requerido, único |

---

### Post (`blog.Post`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `AutoField` | PK |
| `title` | `CharField(200)` | Requerido |
| `slug` | `SlugField(max_length=200)` | Requerido, único, populated from title |
| `content` | `TextField` | Requerido |
| `author` | `ForeignKey(Author)` | on_delete=CASCADE, related_name='posts' |
| `category` | `ForeignKey(Category)` | on_delete=SET_NULL, null=true, blank=true |
| `tags` | `ManyToMany(Tag)` | Symmetrical, related_name='posts' |
| `published_at` | `DateTimeField` | null, blank (opcional) |
| `created_at` | `DateTimeField` | Auto-now-add |
| `updated_at` | `DateTimeField` | Auto-now |

**Relación:** Autor (1:N), Categoría (1:N), Tags (M:N).
**Admin list display:** title, author, category, published_at, created_at.
**Search fields:** title, content.
**Filter fields:** author, category, published_at, created_at.

---

### Comment (`blog.Comment`)
| Campo | Tipo | Características |
|-------|------|-----------------|
| `id` | `AutoField` | PK |
| `post` | `ForeignKey(Post)` | on_delete=CASCADE, related_name='comments' |
| `content` | `TextField` | Requerido |
| `created_at` | `DateTimeField` | Auto-now-add |

**Relación:** Post (1:N).

---

## Relación entre entidades

```
Author 1──1 Profile
Author 1──N Post
Author N──M Tag  (vía Post.tags)
Category 1──N Post
Post 1──N Comment
```

## Datos de prueba (seed_data.py)

| Entidad | Cantidad | Notas |
|---------|----------|-------|
| Authors | 3 | "Ada Lovelace", "Grace Hopper", "Alan Turing" |
| Profiles | 3 | Uno por autor |
| Categories | 3 | "Tecnología", "Ciencia", "Educación" |
| Tags | 3 | "Python", "IA", "Educación" |
| Posts | 2 | Con autores, categorías y etiquetas asignados |
| Comments | 3 | Asignados a posts existentes |

**Total con seed:** 17 entidades (3+3+3+3+2+3).

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Consultas-ORM-y-Duelo]]
- [[Management-Commands]]
- [[Pruebas-Automatizadas]]
- [[Observaciones-y-Pendientes]]
