# URL Shortener - Acortador de URLs

## Descripción
Aplicación web para acortar URLs, construida con **FastAPI**, **SQLAlchemy** (asíncrono) y **SQLite** (por defecto). Incluye autenticación de usuarios, dashboard personal y panel de administración.

## Características
- Registro e inicio de sesión de usuarios.
- Acortamiento de URLs con código único.
- Redirección automática a la URL original.
- Estadísticas de clics (opcional, según implementación).
- Panel de administración para gestión de URLs y usuarios (opcional).
- Documentación interactiva de la API en `/docs`.

## Tecnologías utilizadas
- **FastAPI** - Framework web asíncrono.
- **SQLAlchemy** - ORM asíncrono.
- **SQLite** (por defecto) / PostgreSQL (opcional con variables de entorno).
- **Jinja2** - Motor de plantillas (para dashboards).
- **Passlib / bcrypt** - Hash de contraseñas.
- **Uvicorn** - Servidor ASGI.

## Requisitos previos
- Python 3.10 o superior.
- `pip` y `venv` (entornos virtuales).
- (Opcional) PostgreSQL si se desea en producción.

## Instalación y ejecución

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/acortador_url.git
   cd acortador_url
'EOF'
