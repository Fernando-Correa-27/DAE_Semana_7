# Pasarela de Acciones (Agent)

> Sistema de seguridad para permitir que un LLM interactúe con datos de forma controlada.

---

## Propósito

Permitir que un modelo de lenguaje natural (LLM) ejecute acciones sobre los datos de la
aplicación **sin acceso directo a la base de datos**. En su lugar, el LLM solicita acciones
a través de una **pasarela de seguridad** que valida, aprueba y ejecuta cada operación.

---

## Architecture

```
LLM (natural language)
    ↓ parse_intents(text)
AgentClient (agent/llm.py)
    ↓ request_action(action_id, data)
ActionRegistry (agent/registry.py)
    ├── R0: lectura (aprobado automáticamente)
    ├── R1: creación → requiere hash de aprobación humana
    ├── R2: actualización → requiere hash de aprobación humana
    └── R3: borrado → requiere hash de aprobación humana
    ↓
Base de datos (solo si está aprobado)
```

---

## ActionRegistry

El registro (`agent/registry.py`) define cuatro acciones:

| Acción | ID | Descripción | Requiere aprobación |
|--------|----|-------------|---------------------|
| **Read** | `R0` | Leer posts (`Post.objects.all()`) | ❌ No |
| **Create** | `R1` | Crear post (`Post.objects.create(...)`) | ✅ Hash |
| **Update** | `R2` | Actualizar post (`post.save()`) | ✅ Hash |
| **Delete** | `R3` | Borrar post (`post.delete()`) | ✅ Hash |

### Clave secreta y hash de aprobación

```python
SECRET_KEY = "dae-s07-override-for-lab-testing-only"

def approve_hash(payload: dict) -> str:
    "Devuelve un hash HMAC-SHA256 del payload serializado."
    ...
```

La aprobación se simula firmando un payload con HMAC. En producción real, esto sería un flujo
de UI con un humano revisando y confirmando la acción.

### Ejecución (`execute_action`)

```python
def execute_action(action_id: str, data: dict, approval_hash: str | None) -> dict:
    # 1. Buscar la acción en el registro
    # 2. Si es R0 (lectura): ejecutar sin aprobación
    # 3. Si es R1/R2/R3: verificar approval_hash con approve_hash(data)
    # 4. Si el hash no coincide: lanzar SecurityError
    # 5. Ejecutar la acción y retornar resultado
```

---

## LLM Client (`agent/llm.py`)

El `AgentClient` es una simulación de un cliente LLM que:

1. Recibe texto natural (ej: "muéstrame todos los posts", "crea un post con título X")
2. Pasa el texto por `parse_intents(text)` para extraer una lista de `Intent`
3. Para cada intent, llama a `request_action(action_id, data)`
4. Devuelve los resultados

```python
@dataclass
class Intent:
    action_id: str       # R0, R1, R2, R3
    data: dict           # Datos de la acción
```

### `parse_intents` (stub)

Actualmente es un placeholder. En un escenario real, se integraría con una llamada a la API
de un modelo de lenguaje para extraer las intenciones del texto natural.

---

## Management Command: `agent`

`python manage.py agent` ejecuta una secuencia de acciones para probar la pasarela:

1. **R0 (read):** Leer todos los posts → ✅ aprobado automáticamente
2. **R1 (create):** Crear un post → ✅ con hash válido
3. **R1 (create):** Crear un post → ❌ sin hash → lanza `SecurityError`
4. **R1 (create):** Crear un post → ❌ con hash inválido → lanza `SecurityError`
5. **R2 (update):** Actualizar un post → ✅ con hash válido
6. **R3 (delete):** Borrar un post → ✅ con hash válido
7. **R3 (delete):** Borrar un post → ❌ sin hash → lanza `SecurityError`

---

## Seguridad

- **R0 (lectura):** Sin restricciones — leer datos no es destructivo.
- **R1/R2/R3 (escritura/destrucción):** Requieren hash HMAC de aprobación.
- **Sin acceso directo:** El LLM nunca interactúa con `models` o `QuerySet` directamente.
- **Aislamiento:** Solo las acciones registradas en `registry.ACTIONS` pueden ejecutarse.

---

## Notas relacionadas

- [[Analisis-del-proyecto]]
- [[Modelos-y-base-de-datos]]
- [[Consultas-ORM-y-Duelo]]
- [[Pruebas-Automatizadas]]
- [[Observaciones-y-Pendientes]]
