# 🐳 Dockerfile para el Agente de WhatsApp
# Este archivo define el contenedor para desplegar el backend en Cloud Run.

# Usar imagen base de Python 3.10 (slim para reducir tamaño)
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (necesarias para algunos paquetes de Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Configurar variables de entorno (opcional, se pueden sobrescribir en Cloud Run)
ENV PYTHONPATH=/app
ENV GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/google/key.json

# Exponer puerto 8080 (requerido por Cloud Run)
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]
