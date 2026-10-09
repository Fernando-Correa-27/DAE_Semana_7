# Pruebas Automatizadas

> Suite de tests con pytest y pytest-django.

---

## Configuración

- **Framework:** `pytest` + `pytest-django`
- **Configuración:** `pyproject.toml` → `[tool.pytest.ini_options]`
  - `DJANGO_SETTINGS_MODULE = "config.settings"`
  - `pythonpath = ["."]`

---

## Tests

### `test_front_page.py` — Optimización N+1

**Archivo:** `blog/tests/test_front_page.py`

```python
@pytest.mark.django_db
def test_front_page_min_queries(client):
    """La vista debe usar select_related / prefetch_related para no tener N+1."""
    # Seed datos
    call_command("seed_blog")
    # Ejecutar vista
    with assert_num_queries(2):
        response = client.get("/")
    # Verificar que se muestran los posts
    assert b"Título del post 1" in response.content
    assert b"Título del post 2" in response.content
```

**Propósito:** Asegurar que la página principal genere exactamente **2 consultas SQL** (una para posts con `select_related`, otra para tags con `prefetch_related`).

**Estado actual:** **Fallará** hasta que se corrija `queries.py` (el `TODO` indica que falta agregar `select_related` y `prefetch_related`).

---

### `test_duel.py` — Consistencia del Duelo

**Archivo:** `blog/tests/test_duel.py`

```python
class TestDuelOracleConsistency:
    def test_ai_fails_p4(self):
        """El código proporcionado falla P4: usa tags__name='Python' vs tags__id=1."""
    
    def test_ai_fails_p5_n_plus_1(self):
        """El código proporcionado falla P5: no usa annotate/Count, genera N+1."""
    
    def test_ai_fails_p8_wrong_count(self):
        """El código proporcionado falla P8: usa Count('author__posts') en vez de Count('comments')."""
    
    def test_oracle_matches_seed(self):
        """El oráculo produce las mismas respuestas que seed_data si se siembra primero."""
```

**Propósito:** Verificar que el oráculo es consistente con los datos seed y que las fallas conocidas de la IA se mantienen (no regressiones).

---

### `test_agent.py` — Seguridad del Agent

**Archivo:** `blog/tests/test_agent.py`

```python
class TestAgentSecurity:
    def test_r0_read_no_approval(self):
        """R0 (lectura) debe funcionar sin hash de aprobación."""
    
    def test_r1_create_requires_approval(self):
        """R1 (crear) debe fallar sin hash."""
    
    def test_r1_create_with_valid_hash(self):
        """R1 (crear) debe funcionar con hash válido."""
    
    def test_r1_create_with_invalid_hash(self):
        """R1 (crear) debe rechazar hash inválido."""
    
    def test_r3_delete_requires_approval(self):
        """R3 (borrar) debe fallar sin hash."""
    
    def test_untrusted_data_r0(self):
        """Los datos no confiables no pueden causar ejecución arbitraria en R0."""
    
    def test_untrusted_data_r1(self):
        """Los datos no confiables no pueden evadir la aprobación en R1."""
```

**Propósito:** Validar que la pasarela de seguridad:
- Acepta lecturas sin aprobación (R0)
- Requiere hash para escritura/destrucción (R1–R3)
- Rechaza hashes inválidos
- Es resistente a datos no confiables (inyección de acciones maliciosas)

---

### `test_seed.py` — Validación del Seed

**Archivo:** `blog/tests/test_seed.py`

```python
class TestSeedData:
    def test_seed_counts(self):
        """Verifica que seed_blog crea el número correcto de entidades."""
        call_command("seed_blog")
        assert Author.objects.count() == 3
        assert Profile.objects.count() == 3
        assert Category.objects.count() == 3
        assert Tag.objects.count() == 3
        assert Post.objects.count() == 2
        assert Comment.objects.count() == 3
```

**Propósito:** Asegurar que el seed crea exactamente las cantidades esperadas.

---

## Ejecutar tests

```bash
pytest
# o con más detalle:
pytest -v
# o solo tests fallidos:
pytest --tb=short
```

---

## Resumen de estado esperado

| Test | Estado esperado (sin cambios) |
|------|-------------------------------|
| `test_front_page_min_queries` | **FAIL** (N+1 no corregido) |
| `test_ai_fails_p4` | **PASS** |
| `test_ai_fails_p5_n_plus_1` | **PASS** |
| `test_ai_fails_p8_wrong_count` | **PASS** |
| `test_oracle_matches_seed` | **PASS** |
| `test_r0_read_no_approval` | **PASS** |
| `test_r1_create_requires_approval` | **PASS** |
| `test_r1_create_with_valid_hash` | **PASS** |
| `test_r1_create_with_invalid_hash` | **PASS** |
| `test_r3_delete_requires_approval` | **PASS** |
| `test_untrusted_data_r0` | **PASS** |
| `test_untrusted_data_r1` | **PASS** |
| `test_seed_counts` | **PASS** |

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Consultas-ORM-y-Duelo]]
- [[Pasarela-de-Acciones-Agent]]
- [[Management-Commands]]
- [[Observaciones-y-Pendientes]]
