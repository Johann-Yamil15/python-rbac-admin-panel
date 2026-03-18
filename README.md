# Python RBAC Admin Panel

> **Plataforma web de administración con control de acceso basado en roles (RBAC), construida en Python puro con arquitectura limpia de servicios — sin Django ni Flask.**

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Características Principales](#características-principales)
4. [Tech Stack](#tech-stack)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Guía de Instalación](#guía-de-instalación)
7. [Configuración de Base de Datos](#configuración-de-base-de-datos)
8. [Endpoints de la API](#endpoints-de-la-api)
9. [Sistema RBAC — Permisos](#sistema-rbac--permisos)
10. [Motor de Plantillas Propio](#motor-de-plantillas-propio)
11. [Despliegue en Producción](#despliegue-en-producción)

---

## Descripción General

**Python RBAC Admin Panel** es una plataforma web desarrollada desde cero sin frameworks pesados. Usa **Werkzeug** únicamente como capa WSGI (manejo de Request/Response y archivos), pero todo lo demás — enrutamiento, renderizado de vistas, inyección de variables, menús dinámicos — es código propio.

El sistema permite cambiar entre base de datos local y en la nube con **un solo booleano** en `config/settings.py`, lo que lo hace ideal para desarrollo y publicación en el mismo repositorio sin tocar el código de servicios.

```python
# config/settings.py
USE_LOCAL_DB = False   # True = SQL Server local | False = nube (Somee / Azure)
```

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENTE (Browser)                          │
│           HTML5 · CSS3 · Vanilla JS ES6+ · Fetch API            │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/HTTPS
┌────────────────────────────▼────────────────────────────────────┐
│                        PUNTO DE ENTRADA                         │
│   server_local.py (dev)  /  gunicorn app:application (prod)     │
│               wsgiref.simple_server en desarrollo               │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                        app.py — WSGI App                        │
│                                                                 │
│  1. Archivos estáticos  →  /static/** (CSS, JS, imágenes)       │
│  2. Middleware JWT       →  valida cookie 'auth_token'          │
│     ├─ No logueado      →  redirect /login  (vistas HTML)       │
│     └─ No logueado      →  401 JSON         (rutas /api/)       │
│  3. get_breadcrumbs()   →  genera nav contextual                │
│  4. get_route_handler() →  despacha al controlador correcto     │
└────────┬───────────────────────────────┬────────────────────────┘
         │                               │
┌────────▼──────────────┐    ┌───────────▼────────────────────────┐
│   VISTAS (HTML)       │    │   API ENDPOINTS (JSON)             │
│  *_manager_action()   │    │   *_api_dispatcher(environ,method) │
│                       │    │                                    │
│  home_controller      │    │  GET  /api/usuarios                │
│  user_controller      │    │  POST /api/usuarios                │
│  perfil_controller    │    │  PUT  /api/usuarios                │
│  permisos_controller  │    │  DELETE /api/usuarios              │
│  modulo_controller    │    │  GET  /api/perfil                  │
│  profile_controller   │    │  GET  /api/sexos · /api/estados    │
│  login_controller     │    │  POST /api/login                   │
└────────┬──────────────┘    └───────────┬────────────────────────┘
         │                               │
┌────────▼───────────────────────────────▼────────────────────────┐
│                       CAPA DE SERVICIOS                         │
│                                                                 │
│  UserService      → CRUD usuarios, hash SHA-256, imagen upload  │
│  HomeService      → Menú jerárquico desde BD por perfil         │
│  PermisosService  → Consulta permisos bitwise por módulo        │
│  AuthService      → Login, JWT encode/decode                    │
│  CatalogoService  → Sexos, estados, perfiles, módulos           │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    core/render.py                               │
│                                                                 │
│  render_view(template, context)                                 │
│  ├─ Lee layout.html  →  reemplaza {{content}}                   │
│  ├─ Genera menú HTML desde context['menu_sidebar']              │
│  ├─ Genera breadcrumbs desde context['breadcrumbs']             │
│  ├─ resolve_dot_notation()  →  aplana dicts anidados            │
│  │    { "usuario": {"Nombre": "Ana"} }                          │
│  │    → { "usuario.Nombre": "Ana" }                             │
│  └─ re.sub() con lambda  →  reemplaza {{ usuario.Nombre }}      │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               BASE DE DATOS — SQL Server                        │
│                                                                 │
│   LOCAL:  localhost  (SQL Server Express)                       │
│   NUBE:   DesarrolloWeb.mssql.somee.com                         │
│   Driver: pymssql — cursor(as_dict=True)                        │
│                                                                 │
│   Tablas: Usuario · Perfil · Modulo · PermisosPerfil            │
│           Sexo · EstadoUsuario · Menu                           │
└─────────────────────────────────────────────────────────────────┘
```

**Flujo de una petición típica `GET /usuarios`:**

```
Browser → app.py → valida cookie JWT → get_route_handler('/usuarios','GET')
       → user_manager_action(breadcrumbs, environ)
       → PermisosService.get_permisos_by_perfil(id_perfil)  →  filtra módulo 'Usuario'
       → HomeService.get_sidebar_menu(id_perfil)
       → render_view('seguridad/usuario.html', context)
       → HTML con variables inyectadas → Response 200
```

---

## Características Principales

- **Switch BD con un booleano** — `USE_LOCAL_DB = True/False` en `settings.py` alterna entre SQL Server local y la nube sin modificar ningún servicio.
- **Menú Lateral 100% Dinámico** — `HomeService` consulta la BD y construye la jerarquía `Menu → Submódulos` para el perfil activo. Ningún ítem está hardcodeado en el HTML.
- **Middleware JWT en `app.py`** — Cada petición (excepto `/login` y `/api/login`) valida la cookie `auth_token`. APIs responden 401 JSON; vistas redirigen a `/login`.
- **RBAC Granular** — 4 bits de permiso por módulo por perfil: `bitAgregar`, `bitEditar`, `bitEliminar`, `bitConsulta`. Verificados en backend antes de ejecutar e inyectados al frontend como objeto global `PERMISOS_MODULO`.
- **Motor de Plantillas Propio** — `render_view()` + `resolve_dot_notation()` soportan `{{ usuario.Nombre }}` en HTML plano con dicts anidados, sin Jinja2.
- **Subida de Imágenes Segura** — `UserService.save_profile_image()` valida extensión, genera nombre único con `uuid4` y guarda ruta relativa en BD. En edición, solo actualiza imagen si se sube una nueva.
- **Contraseñas con SHA-256** — El hash se genera en `UserService`. En edición, si el campo viene vacío, se conserva la contraseña existente sin tocarla.
- **Modelo `User` con doble mapeo** — `from_dict()` acepta columnas SQL Server (`Nombre`, `ApellidoP`, `idPerfil`) y `to_dict()` exporta formato para frontend (`nombre`, `ap`, `nombre_completo`).
- **Paginación y filtros en cliente** — Sin recargas. Búsqueda normalizada sin acentos, filtro por rango de fechas, paginación con `slice()` sobre arreglo en memoria. Race condition entre catálogos y usuarios resuelto con `.then()`.

---

## Tech Stack

| Capa | Tecnología | Rol |
|------|-----------|-----|
| WSGI | Werkzeug | Request, Response, redirect, manejo de archivos |
| Servidor dev | `wsgiref.simple_server` | `server_local.py` puerto 8000 |
| Servidor prod | Gunicorn | `gunicorn app:application` |
| Autenticación | PyJWT | Cookie `auth_token` firmada con HS256 |
| Base de datos | SQL Server + pymssql | `cursor(as_dict=True)` |
| Templating | Motor propio `core/render.py` | Dot-notation, regex, sin Jinja2 |
| Frontend | HTML5 + CSS3 + Vanilla JS ES6+ | Fetch API, async/await, DOM dinámico |
| Íconos | Font Awesome + Lucide | Layout y tablas |

> Jinja2 está en `requirements.txt` como dependencia instalada pero **no se utiliza** en el motor de plantillas actual.

---

## Estructura del Proyecto

```
python-rbac-admin-panel/
│
├── app.py                          # WSGI: estáticos, JWT middleware, routing central
├── server_local.py                 # Dev: wsgiref en puerto 8000
├── requirements.txt                # gunicorn pymssql werkzeug Jinja2 PyJWT
│
├── config/
│   ├── settings.py                 # USE_LOCAL_DB · LOCAL_DB · CLOUD_DB
│   └── database.py                 # get_connection() · test_connection()
│
├── core/
│   ├── render.py                   # render_view() · resolve_dot_notation()
│   └── router.py                   # get_route_handler() — dict de rutas exactas
│
├── models/
│   └── user_model.py               # class User: from_dict() ↔ to_dict()
│
├── controllers/
│   ├── home_controller.py          # index_action (dashboard)
│   ├── user_controller.py          # user_manager_action · user_api_dispatcher
│   ├── perfil_controller.py        # perfil_manager_action · perfil_api_dispatcher
│   ├── permisos_controller.py      # permisos_manager_action · permisos_api_dispatcher
│   ├── modulo_controller.py        # modulo_manager_action · modulo/menu api_dispatcher
│   ├── profile_controller.py       # profile_action (vista Mi Perfil)
│   ├── login_controller.py         # login_view · login_api_dispatcher · logout_action
│   ├── catalogo_controller.py      # catalogo_api_dispatcher (sexos, estados, etc.)
│   ├── vistasStaticas_controller.py # modulo_simulado_action
│   └── error_controller.py         # not_found_action (404)
│
├── services/
│   ├── user_service.py             # CRUD · SHA-256 · save_profile_image()
│   ├── home_service.py             # get_sidebar_menu() jerarquía Menu→Submódulos
│   ├── permisos_service.py         # get_permisos_by_perfil()
│   └── login_service.py            # autenticación · SECRET_KEY
│
├── views/
│   └── home/
│       ├── layout.html             # Base: sidebar dinámico · breadcrumbs · {{content}}
│       ├── index.html              # Dashboard
│       ├── perfil.html             # Mi Perfil
│       └── seguridad/
│           ├── usuario.html        # CRUD Usuarios
│           ├── perfil.html         # CRUD Perfiles
│           ├── modulo.html         # CRUD Módulos
│           └── permisos.html       # Asignación de permisos por perfil
│
└── static/
    ├── css/home/
    │   ├── layout.css              # Sidebar, navbar, breadcrumbs
    │   └── index.css               # Estilos por módulo
    ├── js/home/
    │   └── layout.js               # Sidebar dinámico, Lucide init
    └── Images/users/               # Imágenes de perfil (generadas por uuid4)
```

---

## Guía de Instalación

### Requisitos Previos

- Python 3.10+
- SQL Server (Express local) o acceso a servidor en la nube
- `pip` actualizado

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/python-rbac-admin-panel.git
cd python-rbac-admin-panel
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:
```
gunicorn
pymssql
werkzeug
Jinja2
PyJWT
```

### 3. Configurar la Conexión a BD

Edita `config/settings.py`:

```python
USE_LOCAL_DB = True   # True = local, False = nube

LOCAL_DB = {
    "server":   "localhost",
    "user":     "sa",
    "password": "tu_password",
    "database": "nombre_de_tu_bd",
}

CLOUD_DB = {
    "server":   "tu-servidor.mssql.somee.com",
    "user":     "tu_usuario_SQLLogin",
    "password": "tu_password_nube",
    "database": "nombre_bd_nube"
}
```

### 4. Verificar Conexión

```bash
python -c "from config.database import test_connection; print(test_connection())"
# Imprime la fecha/hora del servidor SQL si la conexión es exitosa
```

### 5. Ejecutar en Desarrollo

```bash
python server_local.py
# Servidor activo en: http://localhost:8000
```

---

## Configuración de Base de Datos

### Switch local/nube

`database.py` lee `USE_LOCAL_DB` y selecciona el bloque de credenciales. Todos los servicios llaman a `get_connection()` sin conocer el entorno:

```python
def get_connection():
    config = LOCAL_DB if USE_LOCAL_DB else CLOUD_DB
    return pymssql.connect(
        server=config["server"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
    )
```

### Patrón de consulta

Todos los `SELECT` usan `cursor(as_dict=True)` para obtener dicts con nombres de columna como llaves, directamente compatibles con `User.from_dict()`:

```python
cursor = conn.cursor(as_dict=True)
cursor.execute("SELECT * FROM Usuario WHERE id = %s", (user_id,))
row = cursor.fetchone()
# row → {"id": 5, "Nombre": "Ana", "ApellidoP": "García", ...}
return User.from_dict(row).to_dict()
```

### Tablas Requeridas

| Tabla | Columnas clave |
|-------|---------------|
| `Usuario` | `id`, `Nombre`, `ApellidoP`, `ApellidoM`, `strCorreo`, `strPwd` (SHA-256), `idPerfil`, `idEstadoUsuario`, `idSexo`, `strNumeroCelular`, `strImagenPath`, `FechaNacimiento`, `FechaRegistro` |
| `Perfil` | `id`, `strNombrePerfil` |
| `Modulo` | `id`, `strNombreModulo`, `strRuta`, `idMenu` |
| `Menu` | `id`, `strNombreMenu` |
| `PermisosPerfil` | `idPerfil`, `idModulo`, `bitAgregar`, `bitEditar`, `bitEliminar`, `bitConsulta` |
| `Sexo` | `id`, `strSexo` |
| `EstadoUsuario` | `id`, `strNombreEstado` |

---

## Endpoints de la API

Todos los endpoints (excepto `/api/login`) requieren cookie `auth_token` válida.

### Autenticación

| Método | Endpoint | Body | Descripción |
|--------|----------|------|-------------|
| `GET` | `/login` | — | Renderiza vista de login |
| `POST` | `/api/login` | `{ email, password }` | Valida credenciales, setea cookie JWT |
| `GET` | `/logout` | — | Elimina cookie → redirect `/login` |

---

### Usuarios

| Método | Endpoint | Descripción | Permiso requerido |
|--------|----------|-------------|-------------------|
| `GET` | `/api/usuarios` | Lista todos los usuarios | `bitConsulta` |
| `GET` | `/api/usuarios?id={id}` | Un usuario por ID | `bitConsulta` |
| `POST` | `/api/usuarios` | Crear usuario (`multipart/form-data`) | `bitAgregar` |
| `PUT` | `/api/usuarios` | Actualizar usuario (`multipart/form-data`) | `bitEditar` |
| `DELETE` | `/api/usuarios` | Eliminar. Body JSON: `{ "id": 5 }` | `bitEliminar` |

**Respuesta GET (un usuario):**
```json
{
  "id": 5,
  "nombre": "Ana",
  "ap": "García",
  "am": "López",
  "nombre_completo": "Ana García López",
  "email": "ana@empresa.com",
  "celular": "7771234567",
  "id_perfil": 2,
  "id_sexo": 2,
  "id_estado": 1,
  "fecha_nac": "1995-03-15",
  "fecha_registro": "2024-01-10",
  "imagen_path": "static\\Images\\users\\user_a3f9c1.jpg"
}
```

**Campos `multipart/form-data` para POST/PUT:**
```
Nombre, ApellidoP, ApellidoM, strCorreo, strPwd,
FechaNacimiento, deptoSelect (idPerfil),
sexoSelect (idSexo), estadoSelect (idEstadoUsuario),
strNumeroCelular, imagenInput (archivo — opcional en PUT)
```

**Respuesta estándar operaciones de escritura:**
```json
{ "success": true,  "msg": "Usuario registrado exitosamente" }
{ "success": false, "msg": "Error de validación", "errors": { "email": "Ya está en uso" } }
```

---

### Catálogos

| Endpoint | Descripción | Ejemplo de respuesta |
|----------|-------------|---------------------|
| `GET /api/perfil` | Perfiles de acceso | `[{ "id": 1, "strNombrePerfil": "Super Administrador" }]` |
| `GET /api/sexos` | Catálogo de sexos | `[{ "id": 1, "strSexo": "Masculino" }]` |
| `GET /api/estados` | Estados de cuenta | `[{ "id": 1, "strNombreEstado": "Activo" }]` |
| `GET /api/modulos` | Módulos del sistema | `[{ "id": 3, "strNombreModulo": "Usuario", "strRuta": "/usuarios" }]` |
| `GET /api/menus` | Agrupadores de menú | `[{ "id": 1, "strNombreMenu": "Seguridad" }]` |

---

### Seguridad

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET/POST/PUT/DELETE` | `/api/perfiles` | CRUD de perfiles de acceso |
| `GET/POST/PUT/DELETE` | `/api/modulos` | CRUD de módulos del sistema |
| `PUT/DELETE` | `/api/menus` | Gestión de agrupadores de menú |
| `GET` | `/api/permisos_perfil?id_perfil={id}` | Permisos de un perfil específico |
| `POST` | `/api/permisos_perfil` | Guardar/actualizar permisos |

---

## Sistema RBAC — Permisos

Cada combinación `(Perfil, Módulo)` tiene 4 bits independientes:

| Bit | Acción | Efecto en backend | Efecto en frontend |
|-----|--------|------------------|--------------------|
| `bitConsulta` | Ver | Permite GET | Muestra la tabla/vista |
| `bitAgregar` | Crear | Permite POST | Muestra botón "Nuevo" |
| `bitEditar` | Editar | Permite PUT | Muestra botón editar por fila |
| `bitEliminar` | Eliminar | Permite DELETE | Muestra botón eliminar por fila |

**Flujo de inyección de permisos:**

```python
# user_controller.py — user_manager_action()
todos_los_permisos = PermisosService.get_permisos_by_perfil(id_perfil)

permisos_usuario = next(
    (p for p in todos_los_permisos if p.get('strNombreModulo') == 'Usuario'),
    {"bitAgregar": False, "bitEditar": False, "bitEliminar": False, "bitConsulta": False}
)

render_view('seguridad/usuario.html', {
    "permisos_json": json.dumps(permisos_usuario)
})
```

```html
<!-- usuario.html — objeto global accesible desde cualquier JS de la vista -->
<script>
  const PERMISOS_MODULO = {{ permisos_json }};
</script>
```

```javascript
// users.js — renderTable()
if (PERMISOS_MODULO.bitEditar)
    botonesAccion += `<button class="btn-edit" onclick="UserManager.openModal(${u.id})">...</button>`;

if (PERMISOS_MODULO.bitEliminar)
    botonesAccion += `<button class="btn-delete" onclick="UserManager.delete(${u.id})">...</button>`;

if (!botonesAccion)
    botonesAccion = '<span class="text-muted small">Sin permisos</span>';
```

---

## Motor de Plantillas Propio

`core/render.py` reemplaza completamente a Jinja2. Funciona en 4 pasos:

**1. Une layout y vista:**
```python
final_html = layout.replace('{{content}}', content)
```

**2. Genera el menú sidebar desde Python (no desde HTML):**
```python
# Itera context['menu_sidebar'] construyendo divs y anchors
# Resultado reemplaza {{menu_sidebar_placeholder}} en layout.html
```

**3. Aplana dicts anidados — `resolve_dot_notation()`:**
```python
# Entrada:  { "usuario": {"Nombre": "Ana", "ap": "García"} }
# Salida:   { "usuario.Nombre": "Ana", "usuario.ap": "García" }
# Permite usar {{ usuario.Nombre }} en el HTML
```

**4. Reemplaza con regex + lambda (resistente a backslashes en rutas de imagen):**
```python
for key, value in flat_context.items():
    patron = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
    str_value = str(value) if value is not None else ''
    # Lambda con default arg: evita bug de closure en bucles
    # Lambda también evita que re.sub interprete \ en rutas Windows como escape
    final_html = re.sub(patron, lambda m, v=str_value: v, final_html)
```

---

## Despliegue en Producción

### Con Gunicorn

```bash
gunicorn app:application --workers 2 --bind 0.0.0.0:$PORT
```

### En Render.com

`render.yaml`:
```yaml
services:
  - type: web
    name: python-rbac-admin-panel
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:application --workers 2 --bind 0.0.0.0:$PORT
```

Antes de hacer push, asegúrate de que `config/settings.py` tenga:
```python
USE_LOCAL_DB = False   # apunta a CLOUD_DB
```

### Checklist antes de publicar

- `USE_LOCAL_DB = False` en `settings.py`
- Credenciales de `CLOUD_DB` apuntan al servidor de producción
- La carpeta `static/Images/users/` existe en el servidor (se crea automáticamente con `os.makedirs(..., exist_ok=True)` en `save_profile_image()`)
- El servidor SQL en la nube tiene whitelistada la IP de Render
- `SECRET_KEY` en `login_service.py` es una cadena larga y aleatoria, no el valor de desarrollo