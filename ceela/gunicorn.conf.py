import logging
import os
import sys

# Obtener configuración de variables de entorno con valores por defecto
bind = "0.0.0.0:8000"
workers = int(os.getenv("APP_WORKERS", "2"))
worker_class = "uvicorn.workers.UvicornWorker"
# NOTA: NO usar 'threads' con UvicornWorker - causa que gunicorn use gthread en su lugar
# UvicornWorker es asíncrono y no necesita threads
timeout = int(os.getenv("APP_TIMEOUT", "300"))
keepalive = 1800
max_requests = 1000
max_requests_jitter = 50
loglevel = "debug"  # Cambiar a debug para ver TODO
accesslog = "-"  # stdout
errorlog = "-"   # stderr
capture_output = True  # Capturar print() y stdout/stderr de workers
preload_app = False  # No precargar la app con ASGI

# Hook para configurar logging en cada worker después del fork
def post_fork(server, worker):
    """
    Configurar logging después de que cada worker se forkea.
    Esto asegura que cada worker pueda loguear correctamente.
    """
    import logging
    import sys

    # Configurar el root logger para el worker - NIVEL DEBUG
    logging.basicConfig(
        level=logging.DEBUG,
        format='[Worker-%(process)d] %(asctime)s | %(levelname)s | %(name)s | %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)],
        force=True
    )

    # Configurar el logger específico de la app - NIVEL DEBUG
    app_logger = logging.getLogger('my_app')
    app_logger.setLevel(logging.DEBUG)

    # Configurar uvicorn para que también loguee todo
    uvicorn_logger = logging.getLogger('uvicorn')
    uvicorn_logger.setLevel(logging.DEBUG)

    uvicorn_access = logging.getLogger('uvicorn.access')
    uvicorn_access.setLevel(logging.DEBUG)

    print(f"✅ Worker {worker.pid} logging configured (DEBUG mode)", file=sys.stderr, flush=True)

# Hook cuando el worker está listo
def worker_int(worker):
    print(f"🔴 Worker {worker.pid} received INT or QUIT signal", file=sys.stderr, flush=True)
