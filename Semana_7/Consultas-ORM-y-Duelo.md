# Consultas ORM y Duelo

> Sistema de comparativa entre respuestas humanas e IA para ocho preguntas ORM.

---

## Estructura del Duelo

El sistema de duelo está en `blog/duel/` y consta de cuatro archivos principales:

| Archivo | Propósito |
|---------|-----------|
| `questions.py` | Define las 8 preguntas, sus consultas, y el oráculo con respuestas esperadas |
| `runner.py` | Lógica de ejecución: compara respuestas, cuenta consultas SQL |
| `team.py` | **Estudiante:** respuestas del equipo humano (todos `NotImplementedError`) |
| `ai_answers.py` | Respuestas generadas por IA (incluye respuestas incorrectas y costos SQL) |

---

## Las 8 Preguntas

### P1 — Todos los posts
- **Consulta:** `Post.objects.all()`
- **Ordenación:** Ninguna
- **Respuesta esperada (oráculo):** `"Título del post 1\n\nTítulo del post 2\n"`
- **Notas:** Muestra que no hay orden implícito en `all()`

### P2 — Posts ordenados por fecha
- **Consulta:** `Post.objects.all().order_by('-published_at')`
- **Ordenación:** descendente por `published_at`
- **Respuesta esperada:** `"Título del post 2\n\nTítulo del post 1\n"`

### P3 — Posts de un autor específico
- **Consulta:** `Post.objects.filter(author_id=1)` (author_id=1 = Ada Lovelace)
- **Respuesta esperada:** `"Título del post 1\n"` (solo el post de Ada)
- **Notas:** Filtrado por FK

### P4 — Posts con un tag específico
- **Consulta:** `Post.objects.filter(tags__id=1)` (tag_id=1 = Python)
- **Respuesta esperada:** `"Título del post 1\n"`
- **Notas:** Uso de lookup `__` para M2M

### P5 — Contar comentarios por post
- **Consulta:** Loop `for post in Post.objects.all(): post.comments.count()`
- **Respuesta esperada:** `"Post 1: 1 comentarios\nPost 2: 2 comentarios\n"`
- **Notas:** Pregunta sobre N+1 — cada `.count()` genera una consulta separada

### P6 — Posts con autor y categoría
- **Consulta:** `Post.objects.select_related('author', 'category').all()`
- **Ordenación:** `-published_at`
- **Respuesta esperada:** Muestra título, autor y categoría ordenados
- **Notas:** `select_related` para optimizar FK joins

### P7 — Posts con tags (prefetch)
- **Consulta:** `Post.objects.prefetch_related('tags').all()`
- **Respuesta esperada:** Título + lista de tags por post
- **Notas:** `prefetch_related` para optimizar M2M

### P8 — Posts con conteo de comentarios optimizado
- **Consulta:** `Post.objects.annotate(comment_count=Count('comments'))`
- **Respuesta esperada:** `"Post 1 (1 comentarios)\nPost 2 (2 comentarios)\n"`
- **Notas:** Uso de `annotate()` + `Count()` para evitar N+1

---

## Runner (lógica de comparación)

El `runner.py` hace lo siguiente:

1. Para cada pregunta:
   - Ejecuta la consulta del oráculo (`get_expected_output`)
   - Ejecuta la consulta del equipo humano (`team_answers`)
   - Ejecuta la consulta de la IA (`ai_answers`)
   - Compara textos y reporta diferencias
   - Cuenta cuántas consultas SQL ejecutó cada versión (`connection.queries`)

2. Al final, resume:
   - Cuántas preguntas ganó el equipo humano
   - Cuántas ganó la IA
   - Cuántas quedaron empatadas
   - Costo total en consultas SQL para cada bando

---

## Respuestas de la IA (ai_answers.py)

| Pregunta | Correcta | Consultas | Problema |
|----------|----------|-----------|----------|
| P1 | ✅ | 1 | — |
| P2 | ✅ | 1 | — |
| P3 | ✅ | 1 | — |
| P4 | ❌ | 1 | Usa `filter(tags__name='Python')` (por nombre en vez de ID, da resultado diferente) |
| P5 | ❌ | 11 | N+1 (1 base + 3 por cada `.count()`). El oráculo espera 4 |
| P6 | ✅ | 1 | `select_related` correcto |
| P7 | ✅ | 2 | `prefetch_related` correcto (1 para posts, 1 para tags) |
| P8 | ❌ | 1 | Usa `Count('author__posts')` en vez de `Count('comments')` |

**Total:** IA gana 5/8, el oráculo 3/8. IA usa 14 consultas vs 9 del oráculo.

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Management-Commands]]
- [[Pruebas-Automatizadas]]
- [[Observaciones-y-Pendientes]]
