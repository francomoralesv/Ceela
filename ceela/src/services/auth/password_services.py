from random import randint
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.models.schemas.password_recovery.password_recovery import PasswordRecoveryRequest, PasswordResetRequest
from src.models.entity.personal_access_token import PersonalAccessToken
from src.models.entity.user_table import UserTable
from src.services.auth.mail_service import send_email
from src.utils.security.password.hash_password import hash_password


# Metodo que envia un email con un token para la recuperacion de contraseña
def password_recovery(user: PasswordRecoveryRequest, db: Session):
    exist_user = db.query(UserTable).filter(UserTable.email == user.email).first()
    
    if not exist_user:
        raise HTTPException(
            status_code=400,
            detail="El Usuario no esta registrado"
        )
        
    now = datetime.now(tz=timezone.utc)
    
    # Eliminar los token expirados
    db.query(PersonalAccessToken).filter(
        PersonalAccessToken.user_id == exist_user.id,
        PersonalAccessToken.token_type == "recovery"
    ).delete()
    
    
    code = randint(100000, 999999)
    expiration_time = now + timedelta(minutes=10)
    
    recovery_token = PersonalAccessToken(
        user_id=exist_user.id,
        token=str(code),
        token_type="recovery",
        expires_at=expiration_time
    )
    
    
    subject = "Recuperacion de contraseña"
    body = f"Su codigo de recuperacion de contraseña es: {code}"
    
    
    try:
        db.add(recovery_token)
        db.commit()
        db.refresh(recovery_token)
        
        send_email(exist_user.email, subject, body)
    except IntegrityError as e:
        db.rollback()  
        raise HTTPException(
            status_code=500,
            detail="Error al guardar el token de recuperación en la base de datos"
        )
    
    
    return {
        "message": "Codigo enviado correctamente",
        "correo": exist_user.email
    }
    
    

# Metodo para cambiar de contraseña
def change_password(request: PasswordResetRequest, db: Session):
    exist_user = db.query(UserTable).filter(UserTable.email == request.email).first()
    
    if not exist_user:
        raise HTTPException(status_code=400, detail="El Usuario no está registrado")
    
    now = datetime.now(tz=timezone.utc)

    # Eliminar los tokens que ya vencieron de un respectivo usuario
    db.query(PersonalAccessToken).filter(
        PersonalAccessToken.user_id == exist_user.id,
        PersonalAccessToken.expires_at < now,
        PersonalAccessToken.token_type == "recovery"
    ).delete()
    db.commit()
    
    
    # Recupera de la base de datos un usuario cuyo token sea valido
    recovery_token = db.query(PersonalAccessToken).filter(
        PersonalAccessToken.user_id == exist_user.id,
        PersonalAccessToken.token == request.code,
        PersonalAccessToken.token_type == "recovery",
        PersonalAccessToken.expires_at > now
    ).first()
    
    if not recovery_token:
        raise HTTPException(
            status_code=400,
            detail="El código de recuperación es inválido o ha expirado"
        )
    
    hashed_password = hash_password(request.new_password)
    exist_user.password = hashed_password

    try:
        db.add(exist_user)
        db.query(PersonalAccessToken).filter(
            PersonalAccessToken.token == request.code,
            PersonalAccessToken.token_type == "recovery"
        ).delete()
        db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar la contraseña en la base de datos"
        )
    
    return {"message": "Contraseña actualizada correctamente"}
