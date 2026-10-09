# Observaciones y Pendientes

> Notas técnicas, problemas identificados y próximos pasos recomendados.

---

## Problemas identificados

### 1. N+1 en `front_page` (queries.py:6-12)

**Archivo:** `blog/queries.py`

```python
def posts_for_front_page():
    """
    TODO: this is a terrible query, improve it!
    """
    return Post.objects.all()
```

**Problema:** `Post.objects.all()` genera:
- 1 consulta para posts
- 1 consulta por cada autor accedido (N)
- 1 consulta por cada categoría accedida (N)
- 1 consulta por cada tag accedido (M:N, N consultas)

**Solución recomendada:**
```python
def posts_for_front_page():
    return Post.objects.select_related('author', 'category').prefetch_related('tags').all()
```

**Test asociado:** `test_front_page_min_queries` espera exactamente 2 consultas.

---

### 2. La IA pierde 3 de 8 preguntas en el duelo

| Pregunta | Problema |
|----------|----------|
| P4 | Usa `tags__name='Python'` en vez de `tags__id=1` → resultado diferente |
| P5 | N+1 (11 consultas vs 4 del oráculo) → orden diferente |
| P8 | Usa `Count('author__posts')` en vez de `Count('comments')` → conteo incorrecto |

---

### 3. La IA gana en cantidad pero no en calidad

- La IA resuelve 5/8 preguntas correctamente (vs 3 del oráculo)
- Pero usa más consultas SQL: 14 vs 9
- Las preguntas que gana la IA son las más simples (P1, P2, P3, P6, P7)
- Las que pierde son las que requieren conocimiento específico del ORM (P4, P5, P8)

---

## Próximos pasos recomendados

### Fase 1: Corrección de N+1
1. Modificar `blog/queries.py` para usar `select_related` y `prefetch_related`
2. Verificar que `test_front_page_min_queries` pasa
3. Confirmar que la vista renderiza correctamente

### Fase 2: Completar el Duelo
1. Implementar las 8 respuestas en `blog/duel/team.py`
2. Ejecutar `python manage.py duel` para comparar
3. Documentar diferencias y costos

### Fase 3: Integración LLM real
1. Reemplazar `parse_intents` stub con integración real (OpenAI, Claude, etc.)
2. Configurar API keys de forma segura (variables de entorno)
3. Testing con prompts reales

### Fase 4: Persistencia de aprobaciones
1. Almacenar hashes de aprobación en base de datos
2. UI para revisión humana de acciones pendientes
3. Log de auditoría de acciones ejecutadas

---

## Notas técnicas

- **Base de datos:** SQLite (no recomendado para producción)
- **Framework de tests:** pytest + pytest-django
- **Versión de Django:** 5.2+
- **Python:** requerido (verificar versión con `python --version`)
- **Instalación de dependencias:** `pip install -r requirements.txt`

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Consultas-ORM-y-Duelo]]
- [[Pasarela-de-Acciones-Agent]]
- [[Management-Commands]]
- [[Pruebas-Automatizadas]]
