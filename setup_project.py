#!/usr/bin/env python3
"""
Script para crear la estructura del proyecto URL Shortener
Ejecutar: python3 setup_project.py
"""

import os
import stat

# Configuración
PROJECT_NAME = "url_shortener"
BASE_DIR = os.path.join(os.getcwd(), PROJECT_NAME)

# Estructura de carpetas y archivos
STRUCTURE = {
    "app": {
        "__init__.py": "",
        "main.py": "# Punto de entrada principal\n",
        "database.py": "# Configuración de base de datos\n",
        "models.py": "# Modelos de datos\n",
        "schemas.py": "# Esquemas Pydantic para validación\n",
        "auth.py": "# Autenticación y autorización\n",
        "dependencies.py": "# Dependencias de FastAPI\n",
        "config.py": "# Variables de configuración\n",
        "services": {
            "__init__.py": "",
            "url_service.py": "# Servicio para manejo de URLs\n",
            "metadata_service.py": "# Servicio para metadatos\n"
        },
        "templates": {
            "base.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>URL Shortener</title>\n</head>\n<body>\n    {% block content %}{% endblock %}\n</body>\n</html>",
            "dashboard.html": "{% extends 'base.html' %}\n{% block content %}\n<h1>Dashboard</h1>\n{% endblock %}",
            "admin_dashboard.html": "{% extends 'base.html' %}\n{% block content %}\n<h1>Admin Dashboard</h1>\n{% endblock %}",
            "login.html": "{% extends 'base.html' %}\n{% block content %}\n<h1>Login</h1>\n{% endblock %}",
            "register.html": "{% extends 'base.html' %}\n{% block content %}\n<h1>Register</h1>\n{% endblock %}"
        },
        "static": {
            "style.css": "/* Estilos personalizados */\nbody { font-family: Arial, sans-serif; }"
        }
    },
    "requirements.txt": "fastapi==0.104.1\nuvicorn[standard]==0.24.0\nsqlalchemy==2.0.23\npython-dotenv==1.0.0\nrequests==2.31.0\nbeautifulsoup4==4.12.2\nbcrypt==4.0.1\njinja2==3.1.2\npython-multipart==0.0.6\npython-jose[cryptography]==3.3.0\npasslib[bcrypt]==1.7.4\n",
    ".env": "SECRET_KEY=tu_clave_secreta_aqui\nDATABASE_URL=sqlite:///./shortener.db\nDEBUG=True\n",
    ".gitignore": "venv/\n__pycache__/\n*.pyc\n*.db\n.env.local\n.DS_Store\n*.log\n"
}

def create_structure(base_path, structure):
    """Crea recursivamente la estructura de carpetas y archivos"""
    for name, content in structure.items():
        current_path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            # Es una carpeta
            os.makedirs(current_path, exist_ok=True)
            create_structure(current_path, content)
        else:
            # Es un archivo
            with open(current_path, 'w') as f:
                f.write(content)
            print(f"✅ Creado: {current_path}")

def make_scripts_executable():
    """Hace ejecutables los archivos de scripts si existen"""
    scripts = ["setup_project.py"]
    for script in scripts:
        script_path = os.path.join(BASE_DIR, script)
        if os.path.exists(script_path):
            os.chmod(script_path, os.stat(script_path).st_mode | stat.S_IEXEC)

def main():
    print("🚀 Creando proyecto URL Shortener...")
    
    # Crear directorio base
    os.makedirs(BASE_DIR, exist_ok=True)
    print(f"📁 Directorio creado: {BASE_DIR}")
    
    # Crear estructura
    create_structure(BASE_DIR, STRUCTURE)
    
    # Hacer scripts ejecutables
    make_scripts_executable()
    
    print("\n✅ ¡Estructura creada exitosamente!")
    print(f"\n📂 Navega al proyecto: cd {PROJECT_NAME}")
    print("\n🔧 Siguientes pasos:")
    print("1. Crear entorno virtual: python3 -m venv venv")
    print("2. Activar entorno: source venv/bin/activate")
    print("3. Instalar dependencias: pip install -r requirements.txt")
    print("4. Crear archivo .env con tus variables")
    print("5. Ejecutar: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()
