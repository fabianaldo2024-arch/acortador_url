"""Script para inicializar la base de datos"""
import sys
import os

# Asegurar que el directorio actual está en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app import models

def init_db():
    """Crea todas las tablas en la base de datos"""
    print("📦 Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")

if __name__ == "__main__":
    init_db()
