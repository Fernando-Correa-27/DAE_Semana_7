# Blog Funcional (Lab Blog)

> Transformación del proyecto de laboratorio en un blog funcional, seguro y
> gestionable desde el Admin de Django.

---

## Alcance

Se conservó toda la capa de datos original (`Author`, `Profile`, `Category`,
`Tag`, `Post`, `Comment`) y sobre ella se añadió:

- Autenticación nativa de Django (registro, login, logout).
- Autorización por Grupos/Permisos nativos (RBAC).
- CRUD completo con permisos y control de propiedad.
- Admin personalizado con inlines y autocompletado.
- Plantillas reutilizables en modo oscuro (Bootstrap Icons, CSS propio).

---

## Modelos

| Modelo | Cambio |
|--------|--------|
| `Author` | `user = OneToOneField(AUTH_USER_MODEL, null, SET_NULL)` — negocio desacoplado del login |
| `Comment` | `user = ForeignKey(AUTH_USER_MODEL, null, SET_NULL)` + `clean()` que rechaza texto vacío |
| `ArticleTag` | Modelo intermedio explícito de `Post.tags` con `added_at` y `UniqueConstraint` (`unique_article_tag`) |
| `Post` | `tags = ManyToManyField(through="ArticleTag")`, `Meta.ordering` y `get_absolute_url()` |

### Migración de datos

`blog/migrations/0002_*.py` se escribió a mano porque Django no permite pasar de
una M2M normal a una M2M con `through` mediante `AlterField`. Estrategia:

1. `AlterModelOptions` + `AddField` (`Author.user`, `Comment.user`).
2. `CreateModel ArticleTag` + `AddConstraint`.
3. `RunPython(copy_associations_forward)`: copia `blog_post_tags` → `blog_articletag`.
4. `RemoveField` + `AddField` para reemplazar `Post.tags`.

Se verificó que los **23 pares** originales se conservaron y que la migración es
reversible (`copy_associations_backward`).

---

## Roles (Grupos)

Creados por `python manage.py setup_groups` (idempotente):

| Grupo | Permisos |
|-------|----------|
| Visitante | Solo lectura |
| Usuario registrado | Lectura + comentar + perfil propio |
| Editor | CRUD completo de posts, comentarios, categorías y etiquetas |
| Administrador | Todos los permisos de la app |

Los grupos **no** otorgan `is_staff` / `is_superuser`: eso lo decide un admin.

---

## Vistas y seguridad

- `LoginRequiredMixin` + `PermissionRequiredMixin` en todo el CRUD.
- `comment_create` protegido con `@require_POST`.
- Propiedad: solo el autor de un comentario (o quien tenga `blog.delete_comment`)
  puede borrarlo.
- El perfil solo lo edita su dueño (`author_for_user`).
- Los borradores (`published=False`) solo son visibles para quien tenga
  `blog.change_post`.

---

## Formularios (`blog/forms.py`)

`SignUpForm`, `LoginForm`, `PostForm`, `StaffPostForm`, `CommentForm`,
`ProfileForm`, `CategoryForm`, `TagForm`. Todo hereda de los forms de Django
(validación, hash de contraseña y CSRF incluidos). El registro público **nunca**
expone `is_staff`, `is_superuser` ni permisos.

---

## Plantillas

- `base.html` + `partials/` (`_navbar`, `_messages`, `_field`, `_post_card`,
  `_pagination`, `_footer`).
- Páginas: inicio, lista/detalle/crear/editar/eliminar de posts, comentarios,
  perfil, login, registro, categorías y etiquetas.
- Modo oscuro con acentos pastel, foco visible y contraste ≥ 4.5:1.

---

## Pruebas

66 tests (Django test runner) en `blog/tests/`:

- `test_front_page.py` — contenido y **exactamente 2 consultas**.
- `test_models.py` — relaciones, through, unicidad y validación.
- `test_auth.py` — registro, login, logout y perfil.
- `test_permissions.py` — permisos nativos y propiedad.
- `test_crud.py` — flujos CRUD completos vía HTTP.
- `test_seed.py`, `test_agent.py`, `test_duel.py` — originales.

Ejecutar: `python manage.py test`

---

## Comandos

```bash
python manage.py migrate
python manage.py seed_blog        # datos de ejemplo
python manage.py setup_groups     # grupos y permisos
python manage.py runserver
```

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Pruebas-Automatizadas]]
- [[Management-Commands]]
- [[Observaciones-y-Pendientes]]
