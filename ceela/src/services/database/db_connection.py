import asyncio
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

from src.external.logging import Log

load_dotenv()
database_url = os.getenv("DB_CONNECTION")

print(database_url)

# Add connection timeout parameters
engine = create_engine(
    database_url, 
    echo=False,
    connect_args={
        "connect_timeout": 60,  # Connection timeout in seconds
        "keepalives": 1,  # Enable keepalives
        "keepalives_idle": 30,  # Seconds between keepalives
        "keepalives_interval": 10,  # Seconds between keepalive probes
        "keepalives_count": 5,  # Number of keepalive probes before giving up
        "tcp_user_timeout": 60000,  # TCP timeout in milliseconds
        "options": "-c statement_timeout=60000"  
    },
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,  # Seconds to wait before timing out on getting a connection from the pool
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True  # Test connections for liveness upon checkout
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    SQLModel.metadata.create_all(bind=engine)

def log_message_sync(message: str):
    """Ejecuta Log.save en un entorno no asíncrono."""
    try:
        asyncio.run(Log.save(message=message))
    except RuntimeError:  
        loop = asyncio.get_event_loop()
        loop.run_until_complete(Log.save(message=message))

def get_db():
    """Proporciona una sesión de base de datos y la cierra correctamente al finalizar"""
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        log_message_sync(message=f"Error en la sesión de base de datos: {str(e)}")
        session.rollback()
        raise e
    finally:
        session.close()
