# 🚀 URL Shortener - Acortador de Enlaces

Aplicación web profesional para acortar URLs, desarrollada con **FastAPI**, **SQLAlchemy** y **SQLite/PostgreSQL**. Incluye autenticación de usuarios, panel de administración, caché con Redis, limitación de peticiones, contenerización con Docker y migraciones con Alembic.

---

## ✨ Características

- **Acortamiento de URLs** con código corto único.
- **Autenticación JWT** (registro, login, tokens).
- **Dashboard de usuario** para ver y gestionar sus enlaces.
- **Panel de administración** para supervisar todas las URLs.
- **Caché con Redis** para redirecciones rápidas.
- **Rate Limiting** (límite de peticiones) para evitar abusos.
- **Migraciones automáticas** con Alembic.
- **Pruebas automatizadas** con pytest.
- **Contenerización** con Docker y Docker Compose.
- **Documentación interactiva** (Swagger UI) en `/docs`.

---

## 🛠️ Tecnologías utilizadas

- **Python 3.12+**
- **FastAPI** (framework web)
- **SQLAlchemy** (ORM asíncrono)
- **Alembic** (migraciones)
- **SQLite** (desarrollo) / **PostgreSQL** (producción)
- **Redis** (caché)
- **JWT** (autenticación)
- **SlowAPI** (rate limiting)
- **Pytest** (pruebas)
- **Docker** y **Docker Compose**
- **Jinja2** (templates HTML)
- **Bcrypt** (hash de contraseñas)

---

## 📋 Requisitos previos

- Python 3.12 o superior.
- pip y virtualenv (o venv).
- Docker y Docker Compose (opcional, para despliegue).
- Redis (opcional, para caché).

---

## 🔧 Instalación y configuración

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd acortador_url