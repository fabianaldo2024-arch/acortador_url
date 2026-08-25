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

app = FastAPI(title="URL Shortener")

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

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    print("📄 Página de login cargada")
    return templates.TemplateResponse("login.html", {"request": request})

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
@app.post("/api/register", response_model=dict)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {"message": "Usuario creado exitosamente"}

@app.post("/api/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=1800,
    )
    return response

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
