"""
NiceGUI Web UI Components & Pages.
Componentes y Páginas de Interfaz Web NiceGUI.
"""

from typing import Optional
from nicegui import ui, app
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.models.models import User, URL

def get_current_user_id() -> Optional[int]:
    """Retrieves current user ID from browser session cookie."""
    token = app.storage.user.get("access_token")
    if not token:
        return None
    payload = decode_access_token(token)
    return payload.get("sub") if payload else None

def init_ui():
    """Initializes NiceGUI Pages / Inicializa las páginas de NiceGUI."""

    @ui.page("/")
    async def dashboard_page():
        ui.colors(primary="#2563eb")
        user_id = get_current_user_id()
        
        # Header / Navegación Superior
        with ui.header().classes("justify-between items-center bg-blue-600 text-white p-4 shadow-md"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("link", size="md")
                ui.label("Acortador de URLs").classes("text-xl font-bold")
            
            with ui.row().classes("items-center gap-3"):
                ui.button("Documentación API", on_click=lambda: ui.navigate.to("/docs")).props("flat color=white icon=api")
                if user_id:
                    async def logout():
                        app.storage.user.clear()
                        ui.navigate.to("/login")
                    ui.button("Cerrar Sesión", on_click=logout).props("color=red icon=logout")
                else:
                    ui.button("Login", on_click=lambda: ui.navigate.to("/login")).props("flat color=white icon=login")
                    ui.button("Registro", on_click=lambda: ui.navigate.to("/register")).props("outline color=white icon=person_add")

        # Contenido Principal
        with ui.column().classes("items-center w-full max-w-4xl mx-auto mt-10 p-4"):
            ui.label("Acorta tus Enlaces en Segundos").classes("text-3xl font-extrabold text-gray-800 mb-2 text-center")
            ui.label("Genera enlaces cortos y gestiona tu historial de manera sencilla.").classes("text-gray-500 mb-8 text-center")
            
            with ui.card().classes("w-full p-6 shadow-md rounded-lg border"):
                url_input = ui.input("Ingresa tu URL de origen", placeholder="https://ejemplo.com/pagina-muy-larga").classes("w-full text-lg")
                
                result_container = ui.column().classes("w-full mt-4 items-center hidden")
                short_url_label = ui.label("").classes("text-lg font-bold text-blue-600")
                
                async def shorten_url():
                    val = (url_input.value or "").strip()
                    if not val.startswith(("http://", "https://")):
                        ui.notify("La URL debe comenzar con http:// o https://", color="warning")
                        return
                    
                    import string, random
                    chars = string.ascii_letters + string.digits
                    code = "".join(random.choice(chars) for _ in range(6))
                    
                    async with AsyncSessionLocal() as db:
                        new_item = URL(target_url=val, short_code=code, user_id=user_id)
                        db.add(new_item)
                        await db.commit()
                    
                    full_short_url = f"http://127.0.0.1:8000/r/{code}"
                    short_url_label.set_text(full_short_url)
                    result_container.classes(remove="hidden")
                    ui.notify("¡URL acortada con éxito!", color="positive")
                    url_input.value = ""

                ui.button("Acortar URL", on_click=shorten_url).classes("w-full mt-4 bg-blue-600 text-white font-bold py-3 text-lg")
                
                with result_container:
                    ui.label("Tu URL Acortada:").classes("text-sm text-gray-500 font-semibold")
                    with ui.row().classes("items-center gap-2 bg-gray-100 p-3 rounded w-full justify-between mt-1"):
                        short_url_label
                        def copy_to_clipboard():
                            ui.run_javascript(f'navigator.clipboard.writeText("{short_url_label.text}")')
                            ui.notify("Copiado al portapapeles", color="positive")
                        ui.button("Copiar", on_click=copy_to_clipboard).props("icon=content_copy color=blue")

            # Sección de Historial de URLs del Usuario
            if user_id:
                ui.label("Tus Enlaces Guardados").classes("text-2xl font-bold mt-12 mb-4 text-gray-800 w-full text-left")
                async with AsyncSessionLocal() as db:
                    stmt = select(URL).where(URL.user_id == user_id).order_by(URL.id.desc())
                    res = await db.execute(stmt)
                    user_urls = res.scalars().all()
                    
                    if user_urls:
                        columns = [
                            {"name": "code", "label": "Código Corto", "field": "short_code", "align": "left"},
                            {"name": "target", "label": "URL Destino Original", "field": "target_url", "align": "left"},
                        ]
                        rows = [{"short_code": f"http://127.0.0.1:8000/r/{item.short_code}", "target_url": item.target_url} for item in user_urls]
                        ui.table(columns=columns, rows=rows, row_key="short_code").classes("w-full shadow-md")
                    else:
                        ui.label("Aún no has creado ningún enlace guardado.").classes("text-gray-400 italic text-center w-full my-4")
            else:
                with ui.card().classes("w-full mt-8 p-4 bg-blue-50 border-blue-200 border text-center"):
                    ui.label("💡 Consejo: Regístrate e inicia sesión para guardar el historial de tus URLs acortadas.").classes("text-blue-700 text-sm")

    @ui.page("/register")
    async def register_page():
        ui.colors(primary="#2563eb")
        with ui.card().classes("w-96 absolute-center p-6 shadow-lg"):
            ui.label("Crear Cuenta").classes("text-2xl font-bold mb-4 text-center w-full text-blue-600")
            
            email_input = ui.input("Correo Electrónico").classes("w-full mb-2")
            pass_input = ui.input("Contraseña", password=True, password_toggle_button=True).classes("w-full mb-4")
            
            async def handle_register():
                if not email_input.value or "@" not in email_input.value:
                    ui.notify("Ingresa un correo electrónico válido", color="warning")
                    return
                if len(pass_input.value or "") < 8:
                    ui.notify("La contraseña debe tener al menos 8 caracteres", color="negative")
                    return
                
                async with AsyncSessionLocal() as db:
                    stmt = select(User).where(User.email == email_input.value)
                    result = await db.execute(stmt)
                    if result.scalar_one_or_none():
                        ui.notify("El correo ya está registrado", color="warning")
                        return
                    
                    new_user = User(email=email_input.value, hashed_password=hash_password(pass_input.value))
                    db.add(new_user)
                    await db.commit()
                    ui.notify("¡Registro exitoso! Redirigiendo al login...", color="positive")
                    ui.navigate.to("/login")

            ui.button("Registrarse", on_click=handle_register).classes("w-full bg-blue-600 text-white font-bold py-2 mb-2")
            ui.link("¿Ya tienes cuenta? Inicia sesión", "/login").classes("text-sm text-center w-full block text-blue-500")

    @ui.page("/login")
    async def login_page():
        ui.colors(primary="#2563eb")
        with ui.card().classes("w-96 absolute-center p-6 shadow-lg"):
            ui.label("Iniciar Sesión").classes("text-2xl font-bold mb-4 text-center w-full text-blue-600")
            
            email_input = ui.input("Email").classes("w-full mb-2")
            pass_input = ui.input("Contraseña", password=True, password_toggle_button=True).classes("w-full mb-4")
            
            async def handle_login():
                async with AsyncSessionLocal() as db:
                    stmt = select(User).where(User.email == email_input.value)
                    result = await db.execute(stmt)
                    user = result.scalar_one_or_none()
                    
                    if not user or not verify_password(pass_input.value, user.hashed_password):
                        ui.notify("Credenciales inválidas", color="negative")
                        return
                    
                    token = create_access_token({"sub": user.id, "email": user.email})
                    app.storage.user["access_token"] = token
                    ui.notify("¡Bienvenido!", color="positive")
                    ui.navigate.to("/")

            ui.button("Entrar", on_click=handle_login).classes("w-full bg-blue-600 text-white font-bold py-2 mb-2")
            ui.link("¿No tienes cuenta? Regístrate aquí", "/register").classes("text-sm text-center w-full block text-blue-500")
