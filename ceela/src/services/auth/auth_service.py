from fastapi import HTTPException
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlmodel import func
from src.models.entity.user_table import UserTable
from src.models.schemas.users.user_create import UserCreate, UserCreateAdmin
from src.models.schemas.users.user_login import UserLogin
from src.utils.security.password.hash_password import hash_password
from src.utils.security.password.verify_password import verify_password
from src.utils.security.token.jwt_login import create_access_token
from src.utils.constants import IS_ADMIN
from src.services.auth.mail_service import send_email
from src.utils.security.token._2fa import generate_and_save_otp, validate_otp
from src.models.schemas.autentication_2fa.request2FA import Request2FA
from src.models.entity.personal_access_token import PersonalAccessToken

# Funcion para lanzar excepcion de credenciales invalidas
def raise_invalid_credentials():
    raise HTTPException(
        status_code=401,
        detail="Correo electrónico o contraseña incorrectos"
    )
    
# Metodo para verificar la existencia de un usuario
def get_user_by_email(email: str, db: Session)-> UserTable:
    return db.query(UserTable).filter(func.lower(UserTable.email) == email.lower()).first()


def register_admin(user: UserCreateAdmin, current_user: dict, db: Session):
    if current_user["role_id"] == 2:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para crear usuarios"
        )
        
    existing_user = get_user_by_email(user.email, db)
    
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="El correo electrónico ya está registrado."
        )
        
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    
    new_user = UserTable(**user.model_dump(), active=False)
    
    user_date = jsonable_encoder(new_user, exclude={"password"})
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
    except SQLAlchemyError as e:
        db.rollback()
        print(f"SQLAlchemy error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error al registrar el usuario. Por favor, inténtalo de nuevo más tarde."
        )
    
    return {"message": "Usuario registrado correctamente", "user": user_date}


# Metodo para hacer el registro de usuarios
def register(user: UserCreate, db: Session):
    existing_user = get_user_by_email(user.email, db)
    
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="El correo electrónico ya está registrado."
        )
        
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    
    new_user = UserTable(**user.model_dump(), active=True)

    user_date = jsonable_encoder(new_user, exclude={"password"})
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
    except SQLAlchemyError as e:
        db.rollback()
        print(f"SQLAlchemy error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error al registrar el usuario. Por favor, inténtalo de nuevo más tarde."
        )
    
    return {"message": "Usuario registrado correctamente", "user": user_date}



# Metodo para iniciar sfdsfdsesion
def login(user: UserLogin, db: Session):
    if not user.email:
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico es obligatorio"
        )

    db_user = get_user_by_email(user.email, db)
    print(db_user)
    if db_user:
        if not verify_password(user.password, db_user.password):
            raise_invalid_credentials()
            
        if db_user.is_deleted:
            raise HTTPException(
                status_code=400,
                detail="La cuenta asociada a este correo ha sido eliminada"
            )
        
        if not db_user.active:
            raise HTTPException(
                status_code=400,
                detail="La cuenta está inactiva."
            )
        
        otp = generate_and_save_otp(db_user.id, db, db_user.email)

        email = db_user.email

        # No enviar correo si es el usuario admin
        if email.lower() == "admin@admin.com":
            message_success = True
            otp_status = "Código de autenticación generado (admin)"
        else:
            subject = "Código de Autenticación en Doble Factor"
            body = f"Su código de autenticación es: {otp}"
            message_success = send_email(email, subject, body)
            otp_status = "Correo enviado exitosamente" if message_success else "Error al enviar el correo"

        token = create_access_token(db_user.id, db, in_used=False)

        return {
            "success": True,
            "otp_status": otp_status,
            "email": email
        }

    else:
        raise_invalid_credentials()


def validate_2fa(two_factor_data: Request2FA, db: Session):
    exist_user = db.query(UserTable).filter(func.lower(UserTable.email) == two_factor_data.email.lower()).first()
    
    if not exist_user:
        raise HTTPException(
            status_code=400,
            detail="Usuario no registrado"
        )    
    
    
    now = datetime.now(tz=timezone.utc)
    
    db.query(PersonalAccessToken).filter(
        PersonalAccessToken.user_id == exist_user.id,
        PersonalAccessToken.expires_at < now,
        PersonalAccessToken.token_type == "2FA"
    ).delete()
    db.commit()

    
    if not validate_otp(exist_user.id, two_factor_data.otp, db):
        raise HTTPException(
            status_code=400,
            detail="Código de autenticación inválido"
        )

    
    token = db.query(PersonalAccessToken).filter(
        PersonalAccessToken.user_id == exist_user.id,
        PersonalAccessToken.token_type == "access",
        PersonalAccessToken.in_used == False
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Token de acceso no encontrado o ya en uso"
        )
        
    user_data = jsonable_encoder(exist_user, exclude={"password"})
    token.in_used = True
    
    try:
        db.commit()  
    except Exception as e:
        db.rollback()  
        raise HTTPException(status_code=500, detail="Error al actualizar el token de autenticación")
    
    return {
        "message": "Inicio de sesion exitoso",
        "user": user_data,
        "access_token": token.token,
        "token_type": "bearer"
    }
    
    
    
    
# Metodo para Verificar un usuario admin
def admin(user: dict, db: Session):
    role = user["role_id"]
    
    if role is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )
        
    if role != IS_ADMIN:
        raise HTTPException(
            status_code=400,
            detail="Usuario no autorizado"
        )
    
    return {"message": "Usuario Autorizado"} 



def logout(
    current_user: dict,
    token: str,
    db: Session
):
    # Se busca el token asociado al usuario actual
    token_instance = db.query(PersonalAccessToken).filter(
        PersonalAccessToken.token == token,
        PersonalAccessToken.user_id == current_user["user_id"]
    ).first()

    if token_instance:
        try:
            db.delete(token_instance)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error al eliminar el token de la base de datos"
            )
        return {"message": "Logout exitoso"}
    else:
        raise HTTPException(
            status_code=404,
            detail="Token no encontrado para el usuario actual"
        )
