# Management Commands

> Comandos personalizados de Django para seed, duel y agent.

---

## `seed_blog` (`blog/management/commands/seed_blog.py`)

**Propósito:** Poblar la base de datos con datos deterministas para pruebas y desarrollo.

**Origen de datos:** `blog.seed_data.DATA`

**Datos creados:**
| Entidad | Cantidad |
|---------|----------|
| Authors | 3 |
| Profiles | 3 |
| Categories | 3 |
| Tags | 3 |
| Posts | 2 |
| Comments | 3 |

**Total:** 17 entidades.

**Implementación:**
1. Limpia datos existentes (borra Comments, Posts, Tags, Categories, Profiles, Authors — en orden inverso de dependencias)
2. Crea cada entidad desde `DATA`
3. Maneja ManyToMany con `set()`
4. Imprime conteo de entidades creadas

---

## `duel` (`blog/management/commands/duel.py`)

**Propósito:** Ejecutar el sistema de duelo comparando respuestas del equipo humano vs IA.

**Flujo:**
1. Importa `run_duel` de `blog.duel.runner`
2. Ejecuta `run_duel()`
3. Muestra resultados detallados y resumen

---

## `agent` (`blog/management/commands/agent.py`)

**Propósito:** Simular y probar la pasarela de acciones del LLM.

**Flujo:**
1. Crea `AgentClient()`
2. Ejecuta secuencia de acciones R0–R3 con y sin aprobación
3. Muestra resultados (éxito o `SecurityError`)

---

## Cómo ejecutar

```bash
# Seed de datos
python manage.py seed_blog

# Ejecutar duelo
python manage.py duel

# Ejecutar simulación de agente
python manage.py agent
```

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Consultas-ORM-y-Duelo]]
- [[Pasarela-de-Acciones-Agent]]
- [[Pruebas-Automatizadas]]
- [[Observaciones-y-Pendientes]]
