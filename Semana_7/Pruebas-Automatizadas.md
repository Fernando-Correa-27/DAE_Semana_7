# Pruebas Automatizadas

> Suite del proyecto. Usa el **runner de Django** (no pytest).

---

## Cómo ejecutar

```powershell
python manage.py test                          # toda la suite
python manage.py test blog.tests.test_auth     # un módulo
python manage.py test blog.tests.test_front_page -v 2
```

Resultado actual: **66 tests, OK** (2 omitidos porque no existe `teacher/`).

---

## Archivos de tests (`blog/tests/`)

| Archivo | Cubre |
|---------|-------|
| `test_front_page.py` | La portada muestra los publicados y gasta **exactamente 2 consultas** |
| `test_models.py` | `Author.user`, `SET_NULL`, `Profile` 1-a-1, `ArticleTag` (through + unicidad), `Comment.clean()`, `SET_NULL` de categoría |
| `test_auth.py` | Registro (crea User+Author+Profile, no concede staff), login, logout por POST, perfil propio |
| `test_permissions.py` | Permisos nativos, visibilidad de borradores, CRUD prohibido sin permiso, propiedad de comentarios |
| `test_crud.py` | CRUD de posts/categorías/etiquetas vía HTTP y plantilla de detalle |
| `test_seed.py` | Conteos del seed |
| `test_agent.py` | Seguridad de la pasarela (R0/R2) |
| `test_duel.py` | Consistencia del oráculo y estado del equipo |

---

## Detalles relevantes

### `test_front_page.py`

- `test_front_page_runs_two_queries` — `assertNumQueries(2)`. Es el test "del rojo
  al verde" de la Parte 2: pasa gracias a `select_related` + `prefetch_related` en
  `blog/queries.py`.
- `test_front_page_shows_the_published_posts` — verifica el contenido.
- `test_the_reference_solution_is_green` — se **omite** sin `teacher/`.

### `test_duel.py`

`DuelTests.test_the_team_answered_every_question_correctly` verifica que las 8
respuestas del equipo estén en estado `ok`. (Reemplaza a la aserción original del
starter `test_the_starter_has_nothing_written`, ya obsoleta porque el equipo
completó las respuestas.)

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Consultas-ORM-y-Duelo]]
- [[Pasarela-de-Acciones-Agent]]
- [[Management-Commands]]
- [[Observaciones-y-Pendientes]]
- [[Blog-Funcionalidades]]
