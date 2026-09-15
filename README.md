# Acortador de URLs / Modern URL Shortener

<p align="center">
  <b>FastAPI + NiceGUI + SQLite (Async) + Tailwind CSS</b>
</p>

---

## 🇪🇸 Descripción del Proyecto
Aplicación web moderna y robusta para acortar URLs construida con un stack de alto rendimiento en Python sobre Linux Mint. Utiliza **FastAPI** para la API de redirección asíncrona y gestión de endpoints, **NiceGUI** para la interfaz gráfica reactiva de usuario, y **SQLAlchemy Async** con SQLite para la persistencia segura de datos.

### Características Principales:
- 🚀 **Redirección ultrarrápida:** Procesamiento de URLs en milisegundos mediante consultas asíncronas.
- 🎨 **Interfaz web moderna:** Panel interactivo para recortar enlaces, copiar con un clic y gestionar el historial.
- 🔒 **Autenticación y Seguridad:** Registro e inicio de sesión seguros mediante tokens JWT y contraseñas hasheadas con `bcrypt`.
- 📊 **Historial personal de enlaces:** Muestra las URLs acortadas de forma privada para cada usuario autenticado.
- 🛠️ **Aislamiento de rutas:** Separación clara entre los endpoints de la UI (`/`, `/login`, `/register`) y la redirección corta (`/r/{short_code}`).

---

## 🇬🇧 Project Description
Modern and robust web application for URL shortening built with a high-performance Python stack on Linux Mint. It utilizes **FastAPI** for asynchronous redirection, **NiceGUI** for the reactive web UI, and **SQLAlchemy Async** with SQLite for secure data persistence.

---

## 🛠️ Stack Tecnológico / Tech Stack
- **Python 3.10+**
- **FastAPI** (Web framework & REST API)
- **NiceGUI** (Full-stack UI framework)
- **SQLAlchemy [Asyncio]** (ORM)
- **Aiosqlite** (Async SQLite driver)
- **Poetry** (Dependency management)

---

## ⚙️ Guía de Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/acortador_url.git](https://github.com/fabian2024-arch/acortador_url.git)
   cd acortador_url

   Instalar dependencias:

Bash
poetry install
Iniciar el servidor:

Bash
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000