from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import os
import asyncio

from app.database import engine, Base, get_db
from app import models
from app.services.url_service import URLService
from app.services.metadata_service import MetadataService
from app.auth import (
    get_current_user, authenticate_user, create_access_token,
    get_password_hash, get_user_by_email
)
from app.dependencies import get_current_admin_user, get_current_active_user
from app.schemas import UserCreate, UserLogin, URLCreate, URLResponse, Token

# ====== LIFESPAN PARA CREAR TABLAS AL INICIAR ======
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas verificadas/creadas al iniciar la app.")
    yield

# ====== INSTANCIA DE LA APP ======
app = FastAPI(title="URL Shortener", lifespan=lifespan)

# ====== CONFIGURACIÓN DE TEMPLATES Y STATIC ======
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ====== PÁGINAS HTML (rutas web) ======

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    html_content = """
   <!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acortador de URLs</title>
    <style>
        /* RESET y fondo oscuro */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0b0e14;  /* fondo oscuro */
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;   /* centrado vertical y horizontal */
            margin: 0;
            padding: 20px;
        }
        .container {
            background: #1e2430;   /* fondo de la tarjeta más claro que el body */
            border-radius: 24px;
            padding: 50px 40px;
            max-width: 700px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.6);
            text-align: center;
            transition: transform 0.3s ease;
        }
        .container:hover {
            transform: translateY(-5px);
        }
        h1 {
            font-size: 2.8rem;
            color: #ffffff;
            margin-bottom: 8px;
            font-weight: 700;
            letter-spacing: 1px;
        }
        .subtitle {
            font-size: 1.1rem;
            color: #b0b8c7;
            margin-bottom: 30px;
            border-bottom: 1px solid #2e3a47;
            padding-bottom: 20px;
        }
        .badge {
            display: inline-block;
            background: #2d8c5a;
            color: #ffffff;
            padding: 6px 20px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
        }
        .menu {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin-top: 10px;
        }
        .menu a {
            display: inline-block;
            text-decoration: none;
            background: #2a3442;
            color: #e0e6ef;
            padding: 14px 30px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            border: 1px solid #3b485a;
            transition: all 0.2s ease;
            flex: 1 0 auto;
            min-width: 140px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .menu a:hover {
            background: #3b4a5e;
            color: #ffffff;
            border-color: #5a6f88;
            transform: scale(1.03);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        .menu a.primary {
            background: #2b6cb0;
            color: white;
            border-color: #2b6cb0;
        }
        .menu a.primary:hover {
            background: #1f4e7a;
            border-color: #1f4e7a;
        }
        .footer {
            margin-top: 40px;
            font-size: 0.85rem;
            color: #7a88a0;
            border-top: 1px solid #2e3a47;
            padding-top: 20px;
        }
        .footer a {
            color: #6c9bd2;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
            color: #8bb4e6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="badge">Servicio activo</div>
        <h1>Acortador de URLs</h1>
        <div class="subtitle">Acorta enlaces largos de forma sencilla y segura</div>

        <div class="menu">
            <a href="/register" class="primary">Registro</a>
            <a href="/login" class="primary">Iniciar sesión</a>
            <a href="/shorten">Acortar URL</a>
            <a href="/docs">Documentación API</a>
        </div>

        <div class="footer">
            ¿Ya tienes cuenta? <a href="/login">Inicia sesión</a> · 
            ¿Problemas? <a href="/docs">Consulta la API</a>
        </div>
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
            body { font-family: Arial; max-width: 400px; margin: 50px auto; padding: 20px; }
            input { width: 100%; padding: 8px; margin: 5px 0 15px; box-sizing: border-box; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; width: 100%; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>Registro de Usuario</h1>
        <form id="registerForm">
            <label>Email:</label><br>
            <input type="email" id="email" required><br>
            <label>Nombre de usuario:</label><br>
            <input type="text" id="username" required><br>
            <label>Contraseña:</label><br>
            <input type="password" id="password" required><br>
            <button type="submit">Registrarse</button>
        </form>
        <p id="message"></p>
        <a href="/">Volver al inicio</a>

        <script>
            document.getElementById('registerForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('email').value;
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email, username, password})
                });
                const data = await response.json();
                const msg = document.getElementById('message');
                if (response.ok) {
                    msg.innerHTML = '<span class="success">✅ Usuario registrado. Ahora <a href="/login">inicia sesión</a></span>';
                } else {
                    msg.innerHTML = '<span class="error">❌ ' + (data.detail || 'Error desconocido') + '</span>';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # 🔥 CORREGIDO: ahora envía 'email' en lugar de 'username'
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - URL Shortener</title>
        <style>
            body { font-family: Arial; max-width: 400px; margin: 50px auto; padding: 20px; }
            input { width: 100%; padding: 8px; margin: 5px 0 15px; box-sizing: border-box; }
            button { background: #28a745; color: white; padding: 10px 20px; border: none; cursor: pointer; width: 100%; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>Inicio de Sesión</h1>
        <form id="loginForm">
            <label>Email:</label><br>
            <input type="email" id="email" required><br>
            <label>Contraseña:</label><br>
            <input type="password" id="password" required><br>
            <button type="submit">Iniciar sesión</button>
        </form>
        <p id="message"></p>
        <a href="/">Volver al inicio</a>

        <script>
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email, password})
                });
                const data = await response.json();
                const msg = document.getElementById('message');
                if (response.ok) {
                    msg.innerHTML = '<span class="success">✅ Login exitoso. Token: <code>' + data.access_token + '</code></span>';
                    localStorage.setItem('access_token', data.access_token);
                } else {
                    msg.innerHTML = '<span class="error">❌ ' + (data.detail || 'Error desconocido') + '</span>';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/shorten", response_class=HTMLResponse)
async def shorten_page(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Acortar URL - URL Shortener</title>
        <style>
            body { font-family: Arial; max-width: 500px; margin: 50px auto; padding: 20px; }
            input { width: 100%; padding: 8px; margin: 5px 0 15px; box-sizing: border-box; }
            button { background: #17a2b8; color: white; padding: 10px 20px; border: none; cursor: pointer; width: 100%; }
            .result { margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Acortar URL</h1>
        <form id="shortenForm">
            <label>URL original:</label><br>
            <input type="url" id="url" placeholder="https://ejemplo.com" required><br>
            <button type="submit">Acortar</button>
        </form>
        <div id="result" class="result" style="display:none;"></div>
        <a href="/">Volver al inicio</a>

        <script>
            document.getElementById('shortenForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const url = document.getElementById('url').value;
                const token = localStorage.getItem('access_token');
                if (!token) {
                    alert('Debes iniciar sesión primero. Ve a /login');
                    return;
                }
                const response = await fetch('/api/urls', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + token
                    },
                    body: JSON.stringify({original_url: url})
                });
                const data = await response.json();
                const resultDiv = document.getElementById('result');
                if (response.ok) {
                    const short_url = window.location.origin + '/' + data.short_code;
                    resultDiv.innerHTML = '<strong>✅ URL acortada:</strong><br><a href="' + short_url + '" target="_blank">' + short_url + '</a>';
                    resultDiv.style.display = 'block';
                } else {
                    resultDiv.innerHTML = '<span style="color:red;">❌ ' + (data.detail || 'Error desconocido') + '</span>';
                    resultDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
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
    current_user: models.User = Depends(get_current_admin_user)
):
    print("📄 Admin dashboard cargado")
    urls = await URLService.get_all_urls(db)
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {"request": request, "urls": urls, "user": current_user}
    )

# ====== API ENDPOINTS ======

@app.post("/api/register", status_code=201)
async def api_register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    hashed = get_password_hash(user_data.password)
    new_user = models.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed,
        is_active=True,
        is_admin=False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "Usuario registrado con éxito", "user_id": new_user.id}

@app.post("/api/login", response_model=Token)
async def api_login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    # 🔥 CORREGIDO: usa user_data.email (no username)
    user = await authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/urls", response_model=URLResponse)
async def create_short_url(
    url_data: URLCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    new_url = await URLService.create_short_url(db, url_data, current_user.id)
    asyncio.create_task(MetadataService.fetch_and_save_metadata(db, new_url.id, str(url_data.original_url)))
    return new_url

# ====== REDIRECCIÓN DE URLS CORTAS (DEBE IR AL FINAL) ======

@app.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    url = await URLService.get_url_by_code(db, short_code)
    if not url or not url.is_active:
        raise HTTPException(status_code=404, detail="URL no encontrada o inactiva")
    
    asyncio.create_task(URLService.increment_clicks(db, url.id))
    return RedirectResponse(url.original_url)

# ====== MENSAJE DE INICIO ======
print("=" * 50)
print("🚀 URL Shortener iniciado correctamente")
print("📌 Rutas disponibles:")
print("   - /              → Página de inicio")
print("   - /register      → Página de registro")
print("   - /login         → Página de login")
print("   - /shorten       → Acortar URL (requiere login)")
print("   - /dashboard     → Dashboard del usuario")
print("   - /admin         → Panel de administración")
print("   - /docs          → Documentación interactiva de la API")
print("=" * 50)
