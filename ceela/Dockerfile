FROM python:3.12

# Desactivar buffering de Python para ver logs en tiempo real
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .

# Instalar todas las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir \
    "uvicorn[standard]==0.34.0" \
    "gunicorn==23.0.0" \
    "httptools>=0.5.0" \
    "uvloop>=0.14.0; sys_platform != 'win32'" \
    "websockets>=10.0"

# Copiar todo el código de la aplicación
COPY . .

# Exponer el puerto que usará la aplicación
EXPOSE 8000

ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000
ENV APP_WORKERS=1
ENV APP_TIMEOUT=1800
ENV APP_LOG_LEVEL=info

CMD ["python", "run.py"]
