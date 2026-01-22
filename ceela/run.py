import os
import signal
import subprocess

from dotenv import load_dotenv

load_dotenv()

# Global flag to control shutdown
shutdown_flag = False


def signal_handler(sig, frame):
    global shutdown_flag
    print("\nShutdown signal received. Gracefully shutting down...")
    shutdown_flag = True


def start_gunicorn():
    # Usar principalmente el archivo de configuración
    cmd = [
        "gunicorn",
        "src.main:app",
        "--config", "gunicorn.conf.py",
    ]

    subprocess.run(cmd)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Starting Gunicorn server...")
    try:
        start_gunicorn()
    except KeyboardInterrupt:
        print("Received interrupt signal")
