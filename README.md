# Acortador de URLs Asíncrono (URL Shortener)

Una API web moderna, de alto rendimiento y asíncrona para acortar URLs, construida utilizando **FastAPI**, **SQLAlchemy** (asíncrono) y **SQLite** (con soporte opcional para PostgreSQL) [1, 2]. Incluye autenticación de usuarios por tokens JWT, un panel de control personal y administración avanzada [1].

---

## 🚀 Características Principales

*   **Autenticación Segura**: Registro e inicio de sesión de usuarios con hashing de contraseñas mediante `bcrypt` y protección de rutas con JWT [1, 2].
*   **Gestión de URLs**: Creación de códigos únicos de acortamiento para redirecciones inmediatas con baja latencia [1].
*   **Redirección Asíncrona**: Redirección rápida a la URL original implementando patrones asíncronos nativos [1].
*   **Panel de Administración**: Gestión y monitoreo de enlaces y usuarios (opcional) [1].
*   **Estadísticas en Tiempo Real**: Seguimiento y conteo de clics por cada URL acortada [1].
*   **Documentación Interactiva**: Autogenerada y accesible mediante `/docs` (Swagger UI) y `/redoc` (ReDoc) [1].

---

## 🛠️ Tecnologías y Librerías

*   **FastAPI**: Framework web asíncrono de alto rendimiento [2].
*   **SQLAlchemy**: ORM asíncrono para mapeo y manipulación de datos [2].
*   **Aiosqlite / Asyncpg**: Drivers asíncronos para SQLite y PostgreSQL respectivamente [2].
*   **Jinja2**: Motor de plantillas para renderizar dashboards HTML en el frontend [2].
*   **Passlib (con Bcrypt)**: Seguridad y encriptación de credenciales [2].
*   **Uvicorn**: Servidor ASGI ultrarrápido para producción y desarrollo [2].
*   **Alembic**: Herramienta de migraciones para bases de datos relacionales.
*   **Docker / Docker Compose**: Contenerización para despliegue simplificado y consistente.

---

## 📁 Estructura del Proyecto

De acuerdo con la estructura actual de archivos de la aplicación, el repositorio se organiza de la siguiente manera:

```text
acortador_url/
├── app/                      # Módulo de la aplicación principal (controladores, modelos, schemas y API)
├── migrations/               # Historial y versiones de migraciones de base de datos de Alembic
├── tests/                    # Suite de pruebas automatizadas de integración y unitarias
├── venv/                     # Entorno virtual de Python (excluido en .gitignore)
├── .env                      # Configuración de variables de entorno activas (excluido en .gitignore)
├── .env.example              # Plantilla para configurar las variables de entorno
├── .gitignore                # Reglas de exclusión para Git (evita subir venv, .env, DB local, etc.)
├── alembic.ini               # Archivo de configuración para las migraciones de Alembic
├── asyncio                   # Archivo temporal/herramienta de ejecución asíncrona
├── docker-compose.yml        # Configuración de servicios multi-contenedor (App + DB)
├── Dockerfile                # Receta de construcción de la imagen Docker de la aplicación
├── entrypoint.sh             # Script de inicialización de contenedores (corre migraciones y arranca la app)
├── init.sql                  # Script SQL inicial de base de datos
├── requirements.txt          # Dependencias y librerías de Python requeridas
├── url_shortener.db          # Base de datos SQLite local (generada automáticamente)
└── README.md                 # Documentación del proyecto
```

---

## ⚙️ Requisitos Previos

Asegúrate de tener instalado en tu sistema:
*   **Python 3.10** o superior [2].
*   **Docker** y **Docker Compose** (si deseas ejecutarlo mediante contenedores).
*   **pip** (gestor de paquetes de Python) y **venv** (módulo de entornos virtuales) [2].

---

## 📦 Instalación y Configuración Paso a Paso

### Opción A: Despliegue Rápido con Docker (Recomendado) 🚀

Esta opción compila la aplicación, instala las dependencias, aplica automáticamente las migraciones de la base de datos mediante Alembic y levanta el servidor en un contenedor aislado.

1.  **Clonar el Repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/acortador_url.git
    cd acortador_url
    ```

2.  **Configurar Variables de Entorno:**
    Copia la plantilla y edita las variables en tu nuevo archivo `.env` (como contraseñas o claves secretas):
    ```bash
    cp .env.example .env
    ```

3.  **Ejecutar con Docker Compose:**
    Levanta todo el entorno con un solo comando:
    ```bash
    docker-compose up --build
    ```

---

### Opción B: Ejecución en Entorno Local (Sin Docker) 🛠️

Si prefieres ejecutar el servidor directamente en tu sistema operativo:

1.  **Clonar el Repositorio y acceder:**
    ```bash
    git clone https://github.com/tu-usuario/acortador_url.git
    cd acortador_url
    ```

2.  **Crear y Activar el Entorno Virtual (`venv`):**
    *   **En Linux / macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **En Windows (Command Prompt - cmd):**
        ```cmd
        python -m venv venv
        call venv\Scripts\activate
        ```
    *   **En Windows (PowerShell):**
        ```powershell
        python -m venv venv
        .\venv\Scripts\Activate.ps1
        ```

3.  **Instalar las Dependencias:**
    ```bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

4.  **Configurar Variables de Entorno:**
    ```bash
    cp .env.example .env
    ```

5.  **Ejecutar Migraciones de Base de Datos:**
    Utiliza Alembic para sincronizar el esquema y crear las tablas en tu base de datos SQLite local:
    ```bash
    alembic upgrade head
    ```

6.  **Arrancar la Aplicación con Uvicorn:**
    ```bash
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    ```

---

## 🧪 Pruebas de Funcionamiento

### Correr Pruebas Automatizadas (Tests)
Para ejecutar la suite de pruebas automatizadas que se encuentra en la carpeta `/tests`:
```bash
pytest
```

### Ejemplos Manuales usando la API (Consola / curl)

#### A. Crear una Cuenta de Usuario
Envía una petición POST para registrar un nuevo usuario:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/users/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "usuario_examen",
  "email": "examen@correo.com",
  "password": "PasswordSegura123!"
}'
```

#### B. Obtener Token de Acceso (Login JWT)
Inicia sesión para obtener tu token Bearer de autenticación:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=usuario_examen&password=PasswordSegura123!'
```

#### C. Acortar una URL (Requiere Token)
Sustituye `TU_TOKEN_JWT` por la cadena obtenida en el paso de login anterior:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/urls/shorten' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer TU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
  "original_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}'
```

---

## 🌐 Direcciones Útiles

Una vez levantado el servidor, puedes acceder a:
*   **Dashboard principal / Frontend**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
*   **Documentación Interactiva (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) [1]
*   **Documentación Interactiva Alternativa (ReDoc)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)