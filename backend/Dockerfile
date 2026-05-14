# Usamos una versión ligera de Python
FROM python:3.11-slim

# Instalamos dependencias del sistema necesarias para FAISS y procesamiento de datos
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Instalamos uv
RUN pip install uv

# Establecemos nuestra carpeta de trabajo
WORKDIR /app

# Copiamos primero los archivos de dependencias
COPY pyproject.toml uv.lock ./

# Configuramos uv para que no intente hacer hardlinks en Docker
ENV UV_LINK_MODE=copy

# Sincronizamos e instalamos las librerías
RUN uv sync

# Copiamos el resto de tu código
COPY . .

# Exponemos el puerto de FastAPI
EXPOSE 8000

# Comando para encender el servidor
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]