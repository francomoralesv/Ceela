import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from src.models.entity.personal_access_token import PersonalAccessToken


def generate_otp(length: int = 6):
    """
    Genera un OTP de longitud fija
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

 
 
def generate_and_save_otp(user_id: int, db: Session, user_email: str = None):
    """
    Genera y guarda un OTP en la base de datos
    Para el usuario admin@admin.com siempre genera 111111
    """

    db.query(PersonalAccessToken).filter(
        PersonalAccessToken.user_id == user_id,
        PersonalAccessToken.token_type == "2FA"
    ).delete()

    # Si es el usuario admin, usar código fijo
    if user_email and user_email.lower() == "admin@admin.com":
        otp = "111111"
    else:
        otp = generate_otp()

    expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=2)

    otp_entry = PersonalAccessToken(
        token=otp,
        user_id=user_id,
        expires_at=expires_at,
        token_type="2FA"
    )

    try:
        db.add(otp_entry)
        db.commit()
        db.refresh(otp_entry)
    except Exception as e:
        db.rollback()
        raise e


    return otp



def validate_otp(user_id: int, otp: str, db: Session):
    """
    Valida un OTP contra la base de datos
    """
    now = datetime.now(tz=timezone.utc)
    
    db.query(PersonalAccessToken).filter(
        PersonalAccessToken.user_id == user_id,
        PersonalAccessToken.expires_at < now,
        PersonalAccessToken.token_type == "2FA"
    ).delete()
    db.commit()

    otp_entry = db.query(PersonalAccessToken).filter(
        PersonalAccessToken.user_id == user_id,
        PersonalAccessToken.token == otp,
        PersonalAccessToken.token_type == "2FA",
        PersonalAccessToken.expires_at > now
    ).first()

    print(otp_entry)
    
    if otp_entry:
        print("Se encontro codigo")
        db.delete(otp_entry)
        db.commit()
        return True

    print("No se encontro codigo")
    return False

