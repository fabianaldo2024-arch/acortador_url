FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias
RUN pip install --no-cache-dir fastapi uvicorn

# Copiar TODO el código (incluyendo app/)
COPY . /app/

# Configurar PYTHONPATH
ENV PYTHONPATH=/app

# Verificar que los archivos existen
RUN ls -la /app/ && ls -la /app/app/

# Ejecutar la aplicación
CMD ["uvicorn", "app.run:app", "--host", "0.0.0.0", "--port", "8000"]
