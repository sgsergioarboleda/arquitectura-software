# Usar imagen base de Python 3.11 slim
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para las claves si no existe
RUN mkdir -p keys

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicaciónc
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
