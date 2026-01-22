from passlib.context import CryptContext

# Crear el esquema para bcrypt
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_bcrypt_context():
    """Devuelve el contexto de bcrypt configurado."""
    return bcrypt_context
