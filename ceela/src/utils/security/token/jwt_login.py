from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from src.models.entity.personal_access_token import PersonalAccessToken
from src.models.entity.user_table import UserTable
from src.models.user_base import UserBase
from src.services.database.db_connection import get_db


SECRET_KEY = "secret"
ALGORITHM = "HS256"

security = HTTPBearer()

def get_token(authorization: HTTPAuthorizationCredentials = Depends(security)):
    if not authorization or not authorization.credentials:
        raise HTTPException(status_code=403, detail="Token requerido")
    return authorization.credentials


# Crear el token de accesoafdsf
def create_access_token(user_id: int, db: Session, in_used: bool = True):
    
    # Borra solo los tokens expirados para el usuario
    db.query(PersonalAccessToken).filter(
        PersonalAccessToken.user_id == user_id,
        PersonalAccessToken.token_type == "access",
        PersonalAccessToken.expires_at < datetime.now(tz=timezone.utc)
    ).delete()
    
    expire_time = timedelta(days=2)
    expire_token = datetime.now(tz=timezone.utc) + expire_time
    
    token_data = {"user_id": user_id, "exp": expire_token}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    new_token = PersonalAccessToken(
        user_id=user_id,
        token=token,
        token_type="access",
        expires_at=expire_token,
        in_used=in_used
    )
    
    try:
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al agregar token a la base de datos"
        )
    
    return token


# Verificar el token y obtiene el usuario correspondiente
def verify_token(token: str = Depends(get_token), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="El token no tiene un ID de usuario válido")
        
        token_instance = db.query(PersonalAccessToken).filter_by(
            token=token,
            user_id=user_id,
            in_used=True
        ).first()
      
      
        if not token_instance:
            raise HTTPException(status_code=401, detail="El token no es válido o no existe")
        
        if token_instance.expires_at.replace(tzinfo=timezone.utc) < datetime.now(tz=timezone.utc):
            try:
                db.delete(token_instance)
                db.commit()
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail="Error al eliminar el token expirado")
            
            raise HTTPException(status_code=401, detail="El token ha expirado y ha sido eliminado")
        
        
        user = db.query(UserTable).filter(UserTable.id == user_id).first()
        
        
        if not user:
            raise HTTPException(status_code=401, detail="El usuario no existe")

        user.last_activity = datetime.now(tz=timezone.utc)
        db.add(user) 
        try:
            db.commit()
            db.refresh(user)
        except Exception as e:
            # Log the error but don't fail authentication due to DB issues
            print(f"Error al actualizar last_activity: {str(e)}")
            # We'll still proceed with authentication
        return {
            "user_id": user.id,
            "name": user.name,
            "lastname": user.lastname,
            "email": user.email,
            "number_phone": user.number_phone,
            "birthdate": user.birthdate,
            "country": user.country,
            "ubigeo": user.ubigeo,
            "role_id": user.role_id,
            "last_activity": user.last_activity
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="El token es inválido")
