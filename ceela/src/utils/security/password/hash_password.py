from src.utils.security.password.scheme_bcrypt import get_bcrypt_context

def hash_password(password: str) -> str:
    """
    Genera un hash para una contraseña dada.
    
    Args:
        password (str): La contraseña en texto plano.
    
    Returns:
        str: La contraseña hasheada.
    """
    bcrypt_context = get_bcrypt_context()
    return bcrypt_context.hash(password)
