# Arquitectura del Proyecto

> Estructura general de directorios, configuración y flujos de ejecución.

---

## Estructura de directorios

```
├── Semana_7/                   ← Bóveda Obsidian (notas)
├── blog/                       ← App principal
│   ├── agent/                  ← Pasarela segura para LLM
│   ├── duel/                   ← Comparativa humano vs IA
│   ├── management/commands/    ← Comandos custom (seed_blog, duel, agent)
│   ├── templates/blog/         ← Plantillas Jinja/Django
│   ├── tests/                  ← Pruebas automatizadas
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               ← Entidades del dominio
│   ├── queries.py              ← Consultas (N+1 problemático)
│   ├── urls.py                 ← Routing interno
│   ├── views.py                ← Vista principal
│   └── seed_data.py            ← Datos de prueba deterministas
├── config/                     ← Configuración Django
│   ├── settings.py
│   ├── urls.py                 ← Root URLconf
│   └── wsgi.py
├── manage.py                   ← CLI de Django
└── README.md
```

## Configuración principal

- **Settings:** `config/settings.py`
  - Base de datos: SQLite (`db.sqlite3`)
  - DEBUG = True (entorno de desarrollo)
  - Apps instaladas: `django.contrib.admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`, y `blog`
  - Language: `es` (español)
  - Timezone: `America/Bogota`

- **URLs raíz:** `config/urls.py`
  - `/admin/` → Django Admin
  - `/` → Vista `front_page` de `blog`

- **URLs de la app:** `blog/urls.py`
  - `/` → `front_page` (reenvía a raíz)

## Flujos principales

### 1. Renderizado de front_page
`views.front_page()` → `queries.posts_for_front_page()` → `render()` con contexto de posts, tags, autores.
**Nota:** `posts_for_front_page()` tiene un problema N+1 marcado con `TODO`.

### 2. Seed de datos
`python manage.py seed_blog` → Crea datos deterministas con `blog.seed_data.DATA` (3 autores, 3 perfiles, 3 categorías, 3 etiquetas, 2 posts, 3 comentarios).

### 3. Duelo (Duel)
`python manage.py duel` → Ejecuta las 8 preguntas ORM, compara respuestas del estudiante (`team.py`) vs IA (`ai_answers.py`) contra un oráculo (`questions.py`), y reporta diferencias y conteo de consultas SQL.

### 4. Pasarela de agente (Agent)
`python manage.py agent` → Simula un flujo de acciones de LLM (lectura, creación, actualización, borrado) a través de la pasarela de seguridad `registry.py`.
