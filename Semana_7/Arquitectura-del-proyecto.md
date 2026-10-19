# Arquitectura del Proyecto

> Estructura de directorios, configuración y flujos de ejecución.

---

## Estructura de directorios

```
├── Semana_7/                   ← Bóveda Obsidian (notas)
├── blog/                       ← App principal
│   ├── agent/                  ← Pasarela segura para LLM
│   ├── duel/                   ← Comparativa humano vs IA
│   ├── management/commands/    ← seed_blog, setup_groups, duel, agent
│   ├── migrations/             ← Esquema (0001 inicial, 0002 a través de ArticleTag)
│   ├── templates/blog/         ← Plantillas (base, partials y páginas)
│   ├── static/css/style.css    ← Sistema de diseño (modo oscuro)
│   ├── tests/                  ← Pruebas automatizadas
│   ├── admin.py                ← Admin personalizado con inlines
│   ├── forms.py                ← Formularios (auth, posts, comentarios, perfil)
│   ├── models.py               ← Entidades del dominio
│   ├── queries.py              ← posts_for_front_page() (optimizada)
│   ├── urls.py                 ← Rutas de la app (namespace "blog")
│   ├── views.py                ← Vistas públicas, de auth y CRUD
│   └── seed_data.py            ← Datos de prueba deterministas
├── config/                     ← Configuración Django
│   ├── settings.py
│   ├── urls.py                 ← Root URLconf
│   └── wsgi.py
├── manage.py
├── README.md
├── GUIA-DE-USO.md              ← Guía de uso y ejecución
└── entregable.md               ← Entregable del laboratorio
```

## Configuración principal

- **Settings:** `config/settings.py`
  - Base de datos: SQLite (`db.sqlite3`)
  - `DEBUG = True`, `ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]`
  - Apps: `admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`, `blog`
  - Idioma: `es`; zona horaria: `America/Lima`
  - Auth: `LOGIN_URL="blog:login"`, redirecciones a `blog:front_page`

- **URLs raíz:** `config/urls.py`
  - `/admin/` → Django Admin
  - `/` → `front_page` (también expuesta con el nombre plano `front_page` por compatibilidad con el test original)
  - resto → `include("blog.urls", namespace="blog")`

## Flujos principales

### 1. Renderizado de front_page
`views.front_page()` → `queries.posts_for_front_page()` → `render()`.
`posts_for_front_page()` usa `select_related` + `prefetch_related`: **2 consultas**.

### 2. Seed de datos
`python manage.py seed_blog` → datos deterministas de `blog/seed_data.py`
(4 autores, 4 categorías, 5 etiquetas, 15 artículos, 23 comentarios).

### 3. Duelo
`python manage.py duel [--source ai] [--question qN] [--strict]` → ejecuta las 8
preguntas, compara contra el oráculo y cuenta consultas SQL.

### 4. Pasarela de agente
`python manage.py agent --intent '{...}'` → valida la intención. R0 ejecuta y
marca `untrusted_data`; R2 devuelve un plan con hash que exige aprobación humana.

### 5. Blog funcional
Vistas con permisos nativos (`LoginRequiredMixin`, `PermissionRequiredMixin`) y
control de propiedad; grupos creados por `python manage.py setup_groups`. Detalle
en [[Blog-Funcionalidades]].

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Consultas-ORM-y-Duelo]]
- [[Pasarela-de-Acciones-Agent]]
- [[Management-Commands]]
- [[Pruebas-Automatizadas]]
- [[Blog-Funcionalidades]]
