# Management Commands

> Comandos personalizados de Django: `seed_blog`, `setup_groups`, `duel` y `agent`.

---

## `seed_blog` (`blog/management/commands/seed_blog.py`)

**Propósito:** poblar la base de datos con datos deterministas para el laboratorio.

**Origen de datos:** `blog/seed_data.py` (`AUTHORS`, `CATEGORIES`, `TAGS`, `POSTS`).

**Datos creados:**

| Entidad | Cantidad |
|---------|----------|
| Authors | 4 |
| Profiles | 4 |
| Categories | 4 |
| Tags | 5 |
| Posts | 15 (11 publicados, 4 borradores) |
| Comments | 23 |

**Implementación:** en una transacción, borra en orden de dependencias
(`ArticleTag`, `Comment`, `Post`, `Profile`, `Author`, `Category`, `Tag`) y luego
crea los datos. Las etiquetas se enlazan con `ArticleTag.objects.create(...)`.

**Salida:** `Listo: 4 autores, 15 artículos, 23 comentarios.`

> El comando borra los datos del blog pero **no reinicia el autoincremento** de
> SQLite: los IDs cambian en cada ejecución.

---

## `setup_groups` (`blog/management/commands/setup_groups.py`)

**Propósito:** crear (idempotentemente) los grupos y permisos del blog.

| Grupo | Permisos |
|-------|----------|
| Visitante | Lectura (5) |
| Usuario registrado | Lectura + comentar (6) |
| Editor | CRUD de posts, comentarios, categorías y etiquetas (19) |
| Administrador | Todos los permisos de la app (20) |

No otorga `is_staff` / `is_superuser`. Se puede repetir sin efectos adversos.

```powershell
python manage.py setup_groups
```

---

## `duel` (`blog/management/commands/duel.py`)

Corre las 8 preguntas del duelo contra las respuestas del equipo o de la IA.

```powershell
python manage.py duel                 # respuestas del equipo (team.py)
python manage.py duel --source ai     # respuestas de la IA (ai_answers.py)
python manage.py duel --question q4   # solo una pregunta
python manage.py duel --strict        # error si alguna no es correcta
```

**Fuentes** (`blog/duel/runner.py`): `team`, `ai`, `solutions` (esta última desde
`teacher/solutions`, ausente en la copia del alumnado).

**Estados:** `[OK] correcta`, `[!] correcta pero cara`, `[X] resultado distinto`,
`[X] error`, `[ ] sin escribir`.

No cuenta intentos; para depurar una pregunta se usa `--question`.

---

## `agent` (`blog/management/commands/agent.py`)

Pasa una intención por la pasarela de acciones (`blog/agent/registry.py`).

```powershell
python manage.py agent --intent '{"action": "posts_per_author", "args": {}}'
python manage.py agent --intent '{"action": "comments_of_post", "args": {"post_id": 46}}'
python manage.py agent --intent '{"action": "delete_comments_of_post", "args": {"post_id": 46}}'
python manage.py agent --intent '{"action": "delete_comments_of_post", "args": {"post_id": 46}}' --approve <plan_hash>
python manage.py agent --intent '{"action": "run_sql", "args": {}}'   # denied
python manage.py agent --ask "muéstrame los posts por autor"          # usa el modelo local (opcional)
```

> En PowerShell, los JSON con comillas dobles se destrozan al pasarlos a un
> ejecutable nativo. Usa el token de parada `--%`:
> `python manage.py --% agent --intent "{\"action\": \"posts_per_author\", \"args\": {}}"`

---

## Cómo ejecutar (resumen)

```powershell
python manage.py migrate
python manage.py seed_blog
python manage.py setup_groups
python manage.py duel
python manage.py duel --source ai
python manage.py agent --intent '{"action": "posts_per_author", "args": {}}'
python manage.py test
```

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Arquitectura-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Consultas-ORM-y-Duelo]]
- [[Pasarela-de-Acciones-Agent]]
- [[Pruebas-Automatizadas]]
