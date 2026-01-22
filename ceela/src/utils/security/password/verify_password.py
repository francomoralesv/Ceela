from src.utils.security.password.scheme_bcrypt import get_bcrypt_context

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash dado.
    
    Args:
        plain_password (str): La contraseña en texto plano.
        hashed_password (str): La contraseña hasheada.
    
    Returns:
        bool: True si coinciden, False de lo contrario.
    """
    bcrypt_context = get_bcrypt_context()
    return bcrypt_context.verify(plain_password, hashed_password)
