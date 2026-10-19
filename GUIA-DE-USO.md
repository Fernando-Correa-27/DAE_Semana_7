# Guía de uso y ejecución — Lab Blog

Guía práctica para instalar, ejecutar y usar la aplicación **Lab Blog**
(blog con autores, artículos, categorías, etiquetas y comentarios construido
sobre el laboratorio de ORM de la semana 7).

---

## 1. Requisitos

| Componente | Versión / nota |
|---|---|
| Python | 3.10 o superior |
| Django | `>=5.2,<7` (ver `requirements.txt`) |
| Base de datos | SQLite (incluida con Python, no requiere servidor) |
| Sistema | Windows (los comandos usan PowerShell; en Linux/macOS ajusta las rutas del venv) |

---

## 2. Instalación desde cero

Ejecuta los comandos en la raíz del proyecto
(`C:\Users\lenovo\Downloads\dae-s07-orm-con-ia`).

```powershell
# 1. Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear el esquema de la base de datos
python manage.py migrate

# 4. Cargar los datos de ejemplo (opcional pero recomendado)
python manage.py seed_blog

# 5. Crear los grupos y permisos (RBAC)
python manage.py setup_groups
```

En Linux/macOS, el paso 1 de activación es `source .venv/bin/activate`.

---

## 3. Ejecutar la aplicación

```powershell
python manage.py runserver
```

Abre el navegador en **http://127.0.0.1:8000/**.

Para detener el servidor: `Ctrl + C`.

### Panel de administración

El blog se gestiona también desde el Admin de Django:

```powershell
python manage.py createsuperuser
# introduce usuario, correo y contraseña
python manage.py runserver
```

Panel en **http://127.0.0.1:8000/admin/**. Desde ahí puedes crear/editar
autores, perfiles, categorías, etiquetas, artículos y comentarios, con inlines y
autocompletado para las relaciones.

---

## 4. Comandos de gestión

| Comando | Qué hace |
|---|---|
| `python manage.py migrate` | Crea/actualiza el esquema de la base de datos |
| `python manage.py seed_blog` | **Borra** los datos del blog y carga los datos fijos (4 autores, 4 categorías, 5 etiquetas, 15 artículos, 23 comentarios) |
| `python manage.py setup_groups` | Crea/actualiza los grupos y permisos (repetible) |
| `python manage.py createsuperuser` | Crea una cuenta de administrador |
| `python manage.py test` | Ejecuta la suite de pruebas (66 tests) |
| `python manage.py runserver` | Arranca el servidor de desarrollo |
| `python manage.py check` | Valida la configuración sin arrancar |

`seed_blog` y `setup_groups` son **idempotentes**: se pueden repetir sin problema.

> Aviso: `seed_blog` elimina todos los artículos, comentarios, autores,
> categorías y etiquetas actuales antes de volver a cargarlos. No lo uses si ya
> tienes contenido propio que quieras conservar.

---

## 5. Roles y permisos

La aplicación usa los **grupos nativos de Django**. Asígnalos desde el Admin
(**Autenticación y autorización → Usuarios → Grupos**).

| Grupo | Puede hacer |
|---|---|
| **Visitante** | Leer artículos publicados, categorías y etiquetas |
| **Usuario registrado** | Lo anterior + comentar + editar su propio perfil |
| **Editor** | CRUD completo de artículos, comentarios, categorías y etiquetas |
| **Administrador** | Todos los permisos de la app blog |

Los grupos **no** otorgan `is_staff` ni `is_superuser`: eso se marca por usuario
desde el Admin (casilla "Estado del personal" / "Superusuario"). Un editor no
necesita ser `staff` para gestionar artículos; un usuario `staff` además ve el
Admin.

---

## 6. Guía de uso

### 6.1 Como visitante (sin cuenta)

- Portada (`/`): artículos **publicados**.
- `/articulos/`: listado paginado (6 por página).
- `/articulos/<id>/`: detalle con cuerpo, etiquetas y comentarios.
- `/categorias/` y `/etiquetas/`: listados con conteo de artículos.
- Solo se muestran artículos con `published = True`; los borradores dan 404.

### 6.2 Como usuario registrado

1. Regístrate en **/registro/** (usuario, nombre, correo, país y contraseña).
   Al registrarte se crea tu cuenta y tu perfil de autor, y quedas con la sesión
   iniciada.
2. Inicia sesión en **/entrar/** y cierra sesión con el botón **Salir** (envía
   POST, no basta con abrir `/salir/`).
3. Comenta cualquier artículo publicado desde su detalle.
4. Edita tu perfil en **/perfil/editar/** (nombre visible, país, biografía y
   correo). Puedes eliminar tus propios comentarios.

### 6.3 Como editor / administrador

- Crear artículo: **/articulos/nuevo/**
- Editar artículo: **/articulos/<id>/editar/**
- Eliminar artículo: **/articulos/<id>/eliminar/**
- Categorías: **/categorias/nueva/**, `/<id>/editar/`, `/<id>/eliminar/`
- Etiquetas: **/etiquetas/nueva/**, `/<id>/editar/`, `/<id>/eliminar/`
- Puede eliminar cualquier comentario y editar cualquier artículo.

Al crear un artículo como editor, la autoría se asigna automáticamente a tu
perfil de autor. Un usuario `staff` puede además elegir el autor explícitamente.

---

## 7. Mapa de rutas

| Ruta | Nombre | Acceso |
|---|---|---|
| `/` | `front_page` | Público |
| `/articulos/` | `post_list` | Público |
| `/articulos/<id>/` | `post_detail` | Público (borradores: solo editores) |
| `/articulos/nuevo/` | `post_create` | Permiso `blog.add_post` |
| `/articulos/<id>/editar/` | `post_update` | Permiso `blog.change_post` |
| `/articulos/<id>/eliminar/` | `post_delete` | Permiso `blog.delete_post` |
| `/articulos/<id>/comentar/` | `comment_create` | Sesión iniciada (POST) |
| `/comentarios/<id>/eliminar/` | `comment_delete` | Autor del comentario o permiso `blog.delete_comment` |
| `/entrar/` | `login` | Público |
| `/salir/` | `logout` | Sesión iniciada (POST) |
| `/registro/` | `register` | Público |
| `/perfil/` | `profile` | Sesión iniciada |
| `/perfil/editar/` | `profile_edit` | Sesión iniciada |
| `/categorias/` | `category_list` | Público |
| `/categorias/nueva/` | `category_create` | Permiso `blog.add_category` |
| `/etiquetas/` | `tag_list` | Público |
| `/etiquetas/nueva/` | `tag_create` | Permiso `blog.add_tag` |

---

## 8. Estructura del proyecto

```
config/                 Configuración y URLs raíz
  settings.py           Ajustes (SQLite, login/logout, plantillas)
  urls.py               Incluye blog.urls + alias "front_page"
blog/
  models.py             Author, Profile, Category, Tag, Post, ArticleTag, Comment
  views.py              Vistas públicas, de auth y CRUD con permisos
  forms.py              Formularios (registro, login, posts, comentarios, perfil...)
  urls.py               Rutas de la app (namespace "blog")
  admin.py              Admin personalizado con inlines y autocompletado
  queries.py            posts_for_front_page() (consultas optimizadas)
  seed_data.py          Datos fijos en Python puro
  migrations/           Esquema de la base de datos
  management/commands/  seed_blog, setup_groups, duel, agent
  templates/blog/       Plantillas (base, partials y páginas)
  static/css/style.css  Sistema de diseño en modo oscuro
  tests/                Suite de pruebas
Semana_7/               Notas del proyecto (Obsidian)
db.sqlite3              Base de datos local (no se versiona)
```

---

## 9. Pruebas

```powershell
python manage.py test                 # toda la suite
python manage.py test blog.tests.test_auth   # solo autenticación
python manage.py test blog.tests.test_permissions
```

Resultado esperado: **66 tests OK** (2 se omiten si no existe la carpeta
`teacher/`). Las pruebas cubren modelos, autenticación, permisos, propiedad y
CRUD, además de la portada (que debe generar exactamente 2 consultas SQL).

---

## 10. Solución de problemas

| Síntoma | Causa / solución |
|---|---|
| `No module named django` | El entorno virtual no está activado o faltan dependencias: `.venv\Scripts\activate` y `pip install -r requirements.txt` |
| `no such table: ...` | Falta migrar: `python manage.py migrate` |
| No aparecen grupos en el Admin | Ejecuta `python manage.py setup_groups` |
| Al comentar me redirige a login | El envío de comentarios exige sesión iniciada |
| "Salir" da error 405 | El logout es solo por **POST**; usa el botón del menú, no la URL |
| `UnorderedObjectListWarning` | No debería aparecer: los listados van ordenados explícitamente |
| Puerta 8000 ocupada | `python manage.py runserver 8001` |

---

## 11. Notas

- Es una configuración **solo para desarrollo** (`DEBUG = True`, `SECRET_KEY`
  de relleno). Para producción hay que definir `DJANGO_SECRET_KEY`, apagar
  `DEBUG`, ajustar `ALLOWED_HOSTS` y servir los estáticos correctamente.
- El idioma es `es` y la zona horaria `America/Lima` (ver `config/settings.py`).
- La documentación ampliada del proyecto está en la carpeta `Semana_7/`
  (ver `Blog-Funcionalidades.md`).

---

## 12. Ejecutar las pruebas del laboratorio (evidencias A–F)

Runbook para generar las evidencias del entregable (`entregable.md`). Ejecuta en
PowerShell con el venv activado.

### A. Preparación y datos iniciales

```powershell
python manage.py migrate
python manage.py seed_blog        # "4 autores, 15 artículos, 23 comentarios"
python manage.py setup_groups
python manage.py shell -c "from blog.models import *; print('autores',Author.objects.count(),'| categorias',Category.objects.count(),'| etiquetas',Tag.objects.count(),'| articulos',Post.objects.count(),'| comentarios',Comment.objects.count())"
```

Conteos: **4 autores, 4 categorías, 5 etiquetas, 15 artículos, 23 comentarios**.
El diagrama de relaciones se dibuja a mano desde `blog/models.py`.

### B. Consultas ORM (duelo)

```powershell
python manage.py duel                 # respuestas del equipo
python manage.py duel --question q4   # una sola (depuración)
python manage.py duel --strict        # error si algo no está OK
python manage.py shell -c "from blog.duel import team; print(team.q8().query)"   # ver SQL
```

El comando no cuenta intentos; regístralos a mano.

### C. Comparación con la IA

```powershell
python manage.py duel --source ai
python manage.py shell -c "from blog.duel import team, ai_answers; print(team.q8().query); print(ai_answers.q8().query)"
```

Fallos reales de la IA: q3 (fechas `gt`/`lt`), q4 (N+1, 16 consultas), q5
(`Count` sin `distinct`), q6 (`author__country` inexistente), q8 (`filter` vs
`exclude`).

### D. Rendimiento

```powershell
python manage.py test blog.tests.test_front_page -v 2
```

Antes (sin `select_related`/`prefetch_related`): **32 consultas**. Después: **2**.

### E. Seguridad del agente

> Los IDs cambian en cada `seed_blog` (SQLite no reinicia el autoincremento):
> localiza el artículo por título.

```powershell
python manage.py shell -c "from blog.models import Post; print(Post.objects.get(title='Introducción al ORM de Django').pk)"
```

En PowerShell, para pasar JSON con comillas dobles a un ejecutable nativo usa
`--%`:

```powershell
python manage.py --% agent --intent "{\"action\": \"posts_per_author\", \"args\": {}}"
python manage.py --% agent --intent "{\"action\": \"comments_of_post\", \"args\": {\"post_id\": 46}}"
python manage.py --% agent --intent "{\"action\": \"delete_comments_of_post\", \"args\": {\"post_id\": 46}}"
python manage.py --% agent --intent "{\"action\": \"delete_comments_of_post\", \"args\": {\"post_id\": 46}}" --approve <PLAN_HASH>
python manage.py --% agent --intent "{\"action\": \"run_sql\", \"args\": {}}"
```

Al terminar, restaura los datos:

```powershell
python manage.py seed_blog
```

### F. Uso de IA

Tabla que llena el equipo con su uso real (sin inventar). Plantilla:

| Actividad o pregunta | Herramienta o IA | Solicitud realizada | Respuesta obtenida | Aceptado/Rechazado | Justificación |
|---|---|---|---|---|---|
| | | | | | |

### Todas las pruebas

```powershell
python manage.py test          # 66 tests OK (2 skipped si falta teacher/)
```