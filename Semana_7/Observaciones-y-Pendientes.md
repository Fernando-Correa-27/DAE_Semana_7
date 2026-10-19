# Observaciones y Pendientes

> Notas técnicas, problemas identificados y próximos pasos recomendados.

---

## Problemas resueltos

### ✅ 1. N+1 en `front_page` (queries.py) — RESUELTO

**Solución aplicada:**
```python
def posts_for_front_page():
    return (
        Post.objects.filter(published=True)
        .select_related("author", "category")
        .prefetch_related("tags")
        .order_by("-published_at")
    )
```

**Resultado:** `test_front_page_runs_two_queries` pasa. Medición real: **32 → 2**
consultas.

---

### ✅ 2. Duelo completo — RESUELTO

**Resultado:** Equipo humano **8/8 correctas** vs IA **3/8 correctas**.

**Errores de la IA identificados:**
- Q3: Límites exclusivos (`gt`/`lt`) en vez de inclusivos (`gte`/`lte`)
- Q4: Filtro en Python (N+1, 16 consultas) en vez de `annotate()`
- Q5: `Count` sin `distinct=True` (números inflados)
- Q6: Ignoró el modelo `Profile` intermedio (`author__country` inexistente)
- Q8: `filter(posts__published=False)` equivocado

---

### ✅ 3. Seguridad del Agent — RESUELTO

**Verificaciones realizadas:**
- R0 (lectura) funciona sin hash ✅
- R2 (destrucción) requiere hash válido ✅
- Invalidación por hash: al cambiar los datos, el hash viejo se rechaza
  (`cd78643bb9a9` → `b2bac4d78629`) ✅
- Intención desconocida (`run_sql`) denegada ✅
- `test_agent.py`: todos los tests pasando ✅

---

## Observaciones técnicas

- **Base de datos:** SQLite (no recomendado para producción)
- **Framework de tests:** runner de Django (`python manage.py test`)
- **Versión de Django:** `>=5.2,<7`
- **Python:** requerido (verificar versión con `python --version`)
- **Instalación de dependencias:** `pip install -r requirements.txt`
- **Comandos de PowerShell:** para pasar JSON con comillas dobles a `agent` usar `--%`

## Notas finales

- El `test_seed_counts` original describía las cantidades del starter; el seed se
  recreó para el laboratorio (4 Authors, 15 Posts, 23 Comments). Ver `test_seed.py`.
- Se corrigió el test obsoleto `test_the_starter_has_nothing_written` de
  `test_duel.py`: el equipo ya respondió las 8 preguntas, así que ahora se
  verifica que todas estén en estado `ok`.
- El entregable final se compiló en `entregable.md`.
- Transformación completa del blog documentada en [[Blog-Funcionalidades]].

## Estado final de la suite

`python manage.py test` → **66 tests, OK (2 skipped)**.

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Consultas-ORM-y-Duelo]]
- [[Pasarela-de-Acciones-Agent]]
- [[Management-Commands]]
- [[Pruebas-Automatizadas]]
- [[Blog-Funcionalidades]]

