from contextlib import asynccontextmanager
from app.database import engine, Base
from app import models # Asegúrate de importar tus modelos

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.url_service import URLService
from app.services.metadata_service import MetadataService
from app.auth import get_current_user, authenticate_user, create_access_token, get_password_hash, get_user_by_email
from app.dependencies import get_current_admin_user, get_current_active_user
from app.schemas import UserCreate, UserLogin, URLCreate, URLResponse, Token
from app.models import User
from datetime import timedelta
import asyncio
from fastapi.templating import Jinja2Templates

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Código que se ejecuta al INICIAR la app ---
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas verificadas/creadas al iniciar la app.")
    yield
    # --- Código que se ejecuta al CERRAR la app (opcional) ---
    # await engine.dispose()

app = FastAPI(title="URL Shortener", lifespan=lifespan)

# ====== CONFIGURACIÓN DE TEMPLATES ======

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ====== PÁGINAS HTML (¡PRIMERO! ANTES DE /{short_code}) ======

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>URL Shortener</title></head>
    <body>
        <h1>Bienvenido al Acortador de URLs</h1>
        <p>La aplicación está funcionando correctamente.</p>
        <ul>
            <li><a href="/register">Registro</a></li>
            <li><a href="/login">Login</a></li>
            <li><a href="/docs">Documentación API</a></li>
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Login - URL Shortener</title></head>
    <body>
        <h1>Inicio de Sesión</h1>
        <p>Esta es la página de login (pendiente de implementación).</p>
        <a href="/">Volver al inicio</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)



@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    print("📄 Dashboard cargado para:", current_user.email)
    urls = await URLService.get_user_urls(db, current_user.id)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "urls": urls, "user": current_user}
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    print("📄 Admin dashboard cargado")
    urls = await URLService.get_all_urls(db)
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request, "urls": urls, "user": current_user}
    )

# ====== API ENDPOINTS ======

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>URL Shortener</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f4; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            ul { list-style: none; padding: 0; }
            li { margin: 15px 0; }
            a { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            a:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Bienvenido al Acortador de URLs</h1>
            <p>La aplicación está funcionando correctamente.</p>
            <ul>
                <li><a href="/register">📝 Registro</a></li>
                <li><a href="/login">🔑 Login</a></li>
                <li><a href="/docs">📚 Documentación API</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registro - URL Shortener</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f4; }
            .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            label { display: block; margin: 10px 0 5px; font-weight: bold; }
            input[type="text"], input[type="email"], input[type="password"] { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
            button { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #218838; }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 Registro de Usuario</h1>
            <form action="/api/register" method="post">
                <label>Email:</label>
                <input type="email" name="email" required>
                <label>Usuario:</label>
                <input type="text" name="username" required>
                <label>Contraseña:</label>
                <input type="password" name="password" required>
                <br><br>
                <button type="submit">Registrarse</button>
            </form>
            <p>¿Ya tienes cuenta? <a href="/login">Inicia sesión</a></p>
            <p><a href="/">Volver al inicio</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - URL Shortener</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f4; }
            .container { max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            label { display: block; margin: 10px 0 5px; font-weight: bold; }
            input[type="text"], input[type="password"] { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔑 Inicio de Sesión</h1>
            <form action="/api/login" method="post">
                <label>Usuario o Email:</label>
                <input type="text" name="username" required>
                <label>Contraseña:</label>
                <input type="password" name="password" required>
                <br><br>
                <button type="submit">Iniciar sesión</button>
            </form>
            <p>¿No tienes cuenta? <a href="/register">Regístrate</a></p>
            <p><a href="/">Volver al inicio</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
    

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Login - URL Shortener</title></head>
    <body>
        <h1>Inicio de Sesión</h1>
        <form action="/api/login" method="post">
            <label>Email: <input type="email" name="email" required></label><br>
            <label>Contraseña: <input type="password" name="password" required></label><br>
            <button type="submit">Ingresar</button>
        </form>
        <p><a href="/register">Registrarse</a></p>
        <p><a href="/">Volver al inicio</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/urls", response_model=URLResponse)
async def create_short_url(
    url_data: URLCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    new_url = await URLService.create_short_url(db, url_data, current_user.id)
    asyncio.create_task(MetadataService.fetch_and_save_metadata(db, new_url.id, str(url_data.original_url)))
    return new_url

# ====== REDIRECCIÓN DE URLS CORTAS (¡AL FINAL! DESPUÉS DE LAS RUTAS ESPECÍFICAS) ======

@app.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    url = await URLService.get_url_by_code(db, short_code)
    if not url:
        raise HTTPException(status_code=404, detail="URL no encontrada")
    
    asyncio.create_task(URLService.increment_clicks(db, url.id))
    return RedirectResponse(url.original_url)

print("=" * 50)
print("🚀 URL Shortener iniciado correctamente")
print("📌 Rutas disponibles:")
print("   - /              → Página de inicio")
print("   - /register      → Página de registro")
print("   - /login         → Página de login")
print("   - /dashboard     → Dashboard del usuario")
print("   - /admin         → Panel de administración")
print("=" * 50)
