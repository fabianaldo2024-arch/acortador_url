"""
NiceGUI Pure Python UI Module.
Módulo de Interfaz Gráfica 100% Python con NiceGUI.
"""
import string
import random
from typing import Optional
from nicegui import ui, app
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash, verify_password
from app.models.models import User, URL


def generate_short_code(length: int = 6) -> str:
    """Generate random short code / Generar código corto aleatorio."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def init_ui():
    """Initialize UI Pages and State / Inicializar Páginas y Estado de UI."""

    @ui.page('/')
    async def index_page():
        # Estado de sesión guardado en la memoria de la app cliente
        session = app.storage.user
        if 'authenticated' not in session:
            session['authenticated'] = False
            session['user_id'] = None
            session['email'] = ""

        # Layout Principal
        ui.query('body').classes('bg-slate-900 text-white')

        # Header
        with ui.header().classes('justify-between bg-slate-800 p-4 border-b border-slate-700'):
            ui.label('✂️ URLShortener Pro').classes('text-2xl font-bold text-indigo-400')

            with ui.row().classes('items-center gap-3'):
                auth_info = ui.label('').classes('text-slate-300 text-sm')

                def update_auth_header():
                    if session.get('authenticated'):
                        auth_info.set_text(f"👤 {session.get('email')}")
                        login_btn.set_visibility(False)
                        reg_btn.set_visibility(False)
                        logout_btn.set_visibility(True)
                    else:
                        auth_info.set_text('')
                        login_btn.set_visibility(True)
                        reg_btn.set_visibility(True)
                        logout_btn.set_visibility(False)

                login_btn = ui.button('Iniciar Sesión', on_click=lambda: login_dialog.open()).classes('bg-slate-700')
                reg_btn = ui.button('Registrarse', on_click=lambda: register_dialog.open()).classes('bg-indigo-600')

                def do_logout():
                    session['authenticated'] = False
                    session['user_id'] = None
                    session['email'] = ""
                    update_auth_header()
                    ui.notify('Sesión cerrada correctamente', type='info')

                logout_btn = ui.button('Salir', on_click=do_logout).classes('bg-red-600/80')

        # Modal de Login
        with ui.dialog() as login_dialog, ui.card().classes('bg-slate-800 text-white w-96 p-6 space-y-4'):
            ui.label('Iniciar Sesión').classes('text-xl font-bold')
            login_email = ui.input('Correo Electrónico').classes('w-full').props('dark')
            login_pass = ui.input('Contraseña', password=True).classes('w-full').props('dark')

            async def process_login():
                async with AsyncSessionLocal() as db:
                    stmt = select(User).where(User.email == login_email.value)
                    res = await db.execute(stmt)
                    user = res.scalar_one_or_none()

                    if user and verify_password(login_pass.value, user.hashed_password):
                        session['authenticated'] = True
                        session['user_id'] = user.id
                        session['email'] = user.email
                        update_auth_header()
                        login_dialog.close()
                        ui.notify(f'¡Bienvenido {user.email}!', type='positive')
                    else:
                        ui.notify('Credenciales inválidas', type='negative')

            ui.button('Entrar', on_click=process_login).classes('w-full bg-indigo-600')

        # Modal de Registro
        with ui.dialog() as register_dialog, ui.card().classes('bg-slate-800 text-white w-96 p-6 space-y-4'):
            ui.label('Registro de Usuario').classes('text-xl font-bold')
            reg_email = ui.input('Correo Electrónico').classes('w-full').props('dark')
            reg_pass = ui.input('Contraseña', password=True).classes('w-full').props('dark')

            async def process_register():
                if not reg_email.value or not reg_pass.value:
                    ui.notify('Completa todos los campos', type='warning')
                    return

                async with AsyncSessionLocal() as db:
                    stmt = select(User).where(User.email == reg_email.value)
                    res = await db.execute(stmt)
                    if res.scalar_one_or_none():
                        ui.notify('El correo ya está registrado', type='warning')
                        return

                    new_user = User(email=reg_email.value, hashed_password=get_password_hash(reg_pass.value))
                    db.add(new_user)
                    await db.commit()
                    ui.notify('Registro exitoso. Ya puedes iniciar sesión.', type='positive')
                    register_dialog.close()
                    login_dialog.open()

            ui.button('Crear Cuenta', on_click=process_register).classes('w-full bg-indigo-600')

        # Área Principal (Formulario Acortador)
        with ui.column().classes('w-full max-w-2xl mx-auto my-12 items-center gap-6 p-4'):
            ui.label('Acorta tus enlaces en segundos').classes('text-4xl font-extrabold text-center')
            ui.label('Interfaz construida 100% en Python Puro').classes('text-slate-400 text-center')

            with ui.row().classes('w-full gap-2 items-center'):
                url_input = ui.input(placeholder='https://tu-enlace-largo.com/ruta').classes('flex-1').props('dark outline')

                async def process_shorten():
                    if not url_input.value or not url_input.value.startswith(('http://', 'https://')):
                        ui.notify('Ingresa una URL válida con http:// o https://', type='warning')
                        return

                    async with AsyncSessionLocal() as db:
                        code = generate_short_code()
                        user_id = session.get('user_id') if session.get('authenticated') else None
                        new_url = URL(original_url=url_input.value, short_code=code, user_id=user_id)
                        db.add(new_url)
                        await db.commit()

                        short_link = f"http://localhost:8000/{code}"
                        result_card.set_visibility(True)
                        result_link.set_text(short_link)
                        result_link.props(f'href="{short_link}" target="_blank"')
                        ui.notify('¡URL acortada generada!', type='positive')

                ui.button('Acortar', on_click=process_shorten).classes('bg-indigo-600 h-14 px-6')

            # Tarjeta de Resultado
            with ui.card().classes('w-full bg-slate-800/80 border border-indigo-500/30 p-4 text-center hidden') as result_card:
                ui.label('¡Enlace listo para compartir!').classes('text-sm text-slate-400')
                result_link = ui.link('', '').classes('text-xl text-indigo-400 font-mono underline')

        update_auth_header()
