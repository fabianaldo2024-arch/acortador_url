#!/bin/sh
set -e

echo "🚀 Esperando a que PostgreSQL esté listo..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ PostgreSQL está listo"

echo "🚀 Ejecutando migraciones de base de datos..."

# ✅ FIX: Usar Python directamente sin módulo externo
python3 << 'PYTHON_SCRIPT'
import sys
import os

# Asegurar que podemos importar app
sys.path.insert(0, '/app')
os.chdir('/app')

try:
    from app.database import engine, Base
    from app import models
    print("📦 Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Migraciones completadas")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
PYTHON_SCRIPT

echo "🚀 Iniciando aplicación..."
exec uvicorn app.run:app --host 0.0.0.0 --port 8000
