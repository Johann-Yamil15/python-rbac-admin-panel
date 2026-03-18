# Python RBAC Admin Panel

> **Plataforma web ligera de administración con control de acceso basado en roles (RBAC), arquitectura limpia y motor de plantillas propio — sin frameworks pesados.**

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Características Principales](#características-principales)
4. [Tech Stack](#tech-stack)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Guía de Instalación](#guía-de-instalación)
7. [Variables de Entorno y Configuración](#variables-de-entorno-y-configuración)
8. [Endpoints de la API](#endpoints-de-la-api)
9. [Sistema RBAC — Permisos](#sistema-rbac--permisos)
10. [Despliegue en Producción](#despliegue-en-producción)

---

## Descripción General

**Python RBAC Admin Panel** es una plataforma web desarrollada desde cero en Python puro (con Werkzeug como capa WSGI mínima), diseñada para gestionar usuarios, perfiles y permisos de forma granular. Su principal diferenciador es que **no depende de Django ni Flask**: implementa su propio motor de plantillas (`render_view`), su propio sistema de rutas y su propia capa de datos, manteniendo el stack extremadamente ligero y auditable.

El sistema está pensado para entornos empresariales donde se necesita control total sobre el código y bajo overhead en producción.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTE (Browser)                       │
│              HTML5 · CSS3 · Vanilla JS (ES6+)                   │
│         Fetch API · Async/Await · DOM dinámico                  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/HTTPS
┌────────────────────────────▼────────────────────────────────────┐
│                     SERVIDOR WSGI                               │
│          Gunicorn (producción) / server_local.py (dev)          │
│                    Werkzeug Request/Response                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     CAPA DE ROUTING                             │
│              router.py — Mapeo URL → Handler                    │
│         Soporte GET · POST · PUT · DELETE · multipart           │
└──────────┬─────────────────┬──────────────────┬────────────────┘
           │                 │                  │
┌──────────▼───────┐ ┌───────▼──────┐ ┌────────▼───────┐
│   CONTROLLERS    │ │   API Views  │ │  Static Files  │
│  (page actions)  │ │ /api/usuarios│ │  CSS · JS · IMG│
│  profile_action  │ │ /api/perfil  │ └────────────────┘
│  home_action     │ │ /api/sexos   │
└──────────┬───────┘ └───────┬──────┘
           │                 │
┌──────────▼─────────────────▼────────────────────────────────────┐
│                       CAPA DE SERVICIOS                         │
│  UserService · HomeService · PermisosService · AuthService      │
│           Lógica de negocio desacoplada del transporte          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   MOTOR DE PLANTILLAS PROPIO                    │
│    render_view() — Inyección de variables con dot-notation      │
│    resolve_dot_notation() — Aplanado de dicts anidados          │
│    Menú dinámico · Breadcrumbs · Reemplazo seguro con regex     │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   BASE DE DATOS — SQL Server                    │
│                       pymssql driver                            │
│    Local: SQL Server Express   /   Nube: Azure SQL / Render     │
└─────────────────────────────────────────────────────────────────┘
```

**Patrón:** MVC adaptado a servicios. Los controladores (`*_action`) son delgados: solo orquestan; la lógica vive en `services/`.

---

## Características Principales

- **Menú Lateral 100% Dinámico** — El sidebar se genera consultando la BD según el perfil del usuario. No hay menús hardcodeados en el HTML.
- **Control de Acceso Granular (RBAC)** — Permisos por módulo: `bitAgregar`, `bitEditar`, `bitEliminar`, `bitConsulta`. Verificación tanto en backend (antes de ejecutar) como en frontend (antes de renderizar botones).
- **Motor de Plantillas Propio** — `render_view()` con soporte de dot-notation (`{{ usuario.Nombre }}`), aplanado de dicts anidados, sustitución segura contra backslashes con `lambda` en `re.sub`.
- **API RESTful Integrada** — Endpoints JSON bajo `/api/` para CRUD completo de usuarios, catálogos y permisos.
- **Subida de Imágenes** — Manejo de `multipart/form-data` con validación de extensión, vista previa en tiempo real y fallback a imagen por defecto.
- **Paginación y Filtros en Cliente** — Búsqueda estilo "Google Pill", filtros por rango de fechas y paginación sin recargar la página.
- **Dual-Environment Ready** — Mismo código corre en desarrollo local (SQL Server Express) y en producción en la nube (Azure SQL / Render).

---

## Tech Stack

| Capa | Tecnología |
|------|-----------|
| Servidor WSGI | Werkzeug 3.x |
| Servidor de Producción | Gunicorn |
| Autenticación | PyJWT |
| Base de datos | SQL Server (pymssql) |
| Templating | Motor propio (`core/render.py`) |
| Frontend | HTML5 + CSS3 + Vanilla JS ES6+ |
| Íconos | Font Awesome + Lucide |

---

## Estructura del Proyecto

```
python-rbac-admin-panel/
│
├── server_local.py          # Punto de entrada para desarrollo local
├── wsgi.py                  # Punto de entrada para Gunicorn (producción)
├── requirements.txt         # Dependencias del proyecto
├── .env                     # Variables de entorno (NO subir a git)
│
├── core/
│   ├── render.py            # Motor de plantillas: render_view(), resolve_dot_notation()
│   ├── router.py            # Enrutador HTTP — mapeo URL → handler
│   └── auth.py              # Middleware de sesión y JWT
│
├── controllers/
│   ├── home_controller.py   # Vistas principales (dashboard, perfil)
│   ├── user_controller.py   # CRUD de usuarios
│   └── security_controller.py  # Perfiles, módulos, permisos
│
├── services/
│   ├── user_service.py      # Lógica de usuarios y validaciones
│   ├── home_service.py      # Generación de menú jerárquico
│   ├── permisos_service.py  # Consulta de permisos RBAC
│   └── auth_service.py      # Login, logout, manejo de JWT
│
├── views/
│   └── home/
│       ├── layout.html      # Layout base con sidebar dinámico
│       ├── index.html       # Dashboard
│       ├── perfil.html      # Perfil de usuario
│       └── usuarios.html    # CRUD de usuarios
│
└── static/
    ├── css/
    │   ├── home/layout.css  # Estilos del layout global
    │   └── home/index.css   # Estilos por módulo
    ├── js/
    │   └── home/layout.js   # Lógica del sidebar y componentes globales
    └── Images/
        └── users/           # Imágenes de perfil de usuarios
```

---

## Guía de Instalación

### Requisitos Previos

- Python 3.10+
- SQL Server (Express o superior) con una instancia activa
- `pip` actualizado

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/python-rbac-admin-panel.git
cd python-rbac-admin-panel
```

### 2. Crear y Activar Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

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

### 4. Configurar la Base de Datos

Ejecuta el script de inicialización en tu instancia de SQL Server:

```bash
# Desde SQL Server Management Studio o sqlcmd
sqlcmd -S localhost -d master -i scripts/db_init.sql
```

El script crea las tablas: `Usuarios`, `Perfiles`, `Modulos`, `PermisosPerfil`, `Sexos`, `Estados`.

### 5. Configurar Variables de Entorno

Copia el archivo de ejemplo y edítalo:

```bash
cp .env.example .env
# Editar .env con tus credenciales (ver sección siguiente)
```

### 6. Ejecutar en Desarrollo

```bash
python server_local.py
```

El servidor quedará disponible en: `http://localhost:8000`

---

## Variables de Entorno y Configuración

Crea un archivo `.env` en la raíz del proyecto. **Nunca subas este archivo a git** (ya está en `.gitignore`).

```env
# ─── BASE DE DATOS ────────────────────────────────────────────
# Local (SQL Server Express)
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=nombre_base_de_datos
DB_USER=sa
DB_PASSWORD=tu_password_seguro
DB_PORT=1433

# ─── SERVIDOR ─────────────────────────────────────────────────
APP_HOST=0.0.0.0
APP_PORT=8000
APP_ENV=development          # development | production

# ─── SEGURIDAD ────────────────────────────────────────────────
JWT_SECRET_KEY=cambia_esto_por_una_clave_larga_y_aleatoria
JWT_EXPIRATION_HOURS=8
SESSION_COOKIE_NAME=rbac_session

# ─── ARCHIVOS ─────────────────────────────────────────────────
UPLOAD_FOLDER=static/Images/users
MAX_UPLOAD_SIZE_MB=2
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp
```

### Configuración para Producción (Render / Azure)

En la plataforma de despliegue, configura estas variables de entorno adicionales:

```env
APP_ENV=production

# SQL Server en la nube (Azure SQL o similar)
DB_SERVER=tu-servidor.database.windows.net
DB_NAME=nombre_base_produccion
DB_USER=admin_user
DB_PASSWORD=password_produccion
```

### Cómo se consumen en el código

```python
# core/config.py
import os

DB_CONFIG = {
    'server':   os.environ.get('DB_SERVER', 'localhost\\SQLEXPRESS'),
    'database': os.environ.get('DB_NAME', 'dev_db'),
    'user':     os.environ.get('DB_USER', 'sa'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'port':     int(os.environ.get('DB_PORT', 1433)),
}

JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'dev-secret-change-me')
```

---

## Endpoints de la API

Todos los endpoints requieren sesión activa (cookie JWT). Las respuestas son siempre `application/json`.

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/login` | Iniciar sesión. Body: `{ email, password }` |
| `GET` | `/logout` | Cerrar sesión y limpiar cookie |

**Respuesta exitosa de `/login`:**
```json
{
  "success": true,
  "redirect": "/",
  "user": {
    "id": 1,
    "nombre_completo": "Juan Pérez",
    "id_perfil": 1
  }
}
```

---

### Usuarios

| Método | Endpoint | Descripción | Permiso requerido |
|--------|----------|-------------|-------------------|
| `GET` | `/api/usuarios` | Lista todos los usuarios | `bitConsulta` |
| `GET` | `/api/usuarios?id={id}` | Obtiene un usuario por ID | `bitConsulta` |
| `POST` | `/api/usuarios` | Crea un nuevo usuario (multipart) | `bitAgregar` |
| `PUT` | `/api/usuarios` | Actualiza un usuario (multipart) | `bitEditar` |
| `DELETE` | `/api/usuarios` | Elimina un usuario. Body: `{ id }` | `bitEliminar` |

**Estructura de usuario (GET):**
```json
{
  "id": 5,
  "nombre": "María",
  "ap": "González",
  "am": "López",
  "nombre_completo": "María González López",
  "email": "maria@empresa.com",
  "celular": "7771234567",
  "id_perfil": 2,
  "id_sexo": 2,
  "id_estado": 1,
  "fecha_nac": "1995-03-15",
  "fecha_registro": "2024-01-10",
  "imagen_path": "static/Images/users/maria.jpg"
}
```

**Respuesta estándar (POST / PUT / DELETE):**
```json
{ "success": true, "msg": "Usuario registrado correctamente." }
{ "success": false, "msg": "Error de validación", "errors": { "email": "Ya está en uso" } }
```

---

### Catálogos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/perfil` | Lista todos los perfiles de acceso |
| `GET` | `/api/sexos` | Lista catálogo de sexos |
| `GET` | `/api/estados` | Lista estados de cuenta (Activo/Inactivo) |

**Respuesta de `/api/perfil`:**
```json
[
  { "id": 1, "strNombrePerfil": "Super Administrador" },
  { "id": 2, "strNombrePerfil": "Operador" }
]
```

---

### Seguridad (Módulos y Permisos)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/modulos` | Lista todos los módulos del sistema |
| `GET` | `/api/permisos?id_perfil={id}` | Permisos de un perfil específico |
| `PUT` | `/api/permisos` | Actualiza permisos de un perfil |

---

## Sistema RBAC — Permisos

El sistema evalúa 4 bits de permiso por módulo por perfil:

| Bit | Acción | Efecto en UI | Efecto en Backend |
|-----|--------|--------------|-------------------|
| `bitConsulta` | Ver | Muestra la tabla/vista | Permite GET |
| `bitAgregar` | Crear | Muestra botón "Nuevo" | Permite POST |
| `bitEditar` | Editar | Muestra botón de edición | Permite PUT |
| `bitEliminar` | Eliminar | Muestra botón de eliminar | Permite DELETE |

Los permisos se inyectan en el HTML como objeto global JS al renderizar la vista:

```html
<script>
  const PERMISOS_MODULO = {{ permisos_json }};
  // → { "canAdd": true, "canEdit": true, "canDelete": false, "canView": true }
</script>
```

---

## Despliegue en Producción

### Con Gunicorn (Render / VPS)

```bash
gunicorn wsgi:app --workers 2 --bind 0.0.0.0:$PORT
```

**`render.yaml` (si usas Render.com):**
```yaml
services:
  - type: web
    name: rbac-admin-panel
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn wsgi:app --workers 2 --bind 0.0.0.0:$PORT
    envVars:
      - key: APP_ENV
        value: production
      - key: DB_SERVER
        sync: false
      - key: DB_PASSWORD
        sync: false
      - key: JWT_SECRET_KEY
        generateValue: true
```

> **Nota sobre la BD en Render:** Render no tiene SQL Server nativo. Se recomienda usar **Azure SQL** (tier gratuito disponible) o **ElephantSQL** migrando a PostgreSQL con el driver `psycopg2`. La capa de servicios está desacoplada para facilitar ese cambio.