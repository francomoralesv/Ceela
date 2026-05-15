from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.services.auth.password_services import password_recovery, change_password
from src.models.schemas.password_recovery.password_recovery import PasswordRecoveryRequest, PasswordResetRequest
from src.services.database.db_connection import get_db 

router_password_controller = APIRouter()

@router_password_controller.post("/forgot-password", tags=["Management Password"])
def forgot_password(user: PasswordRecoveryRequest, db: Session = Depends(get_db)):
    return password_recovery(user, db)


@router_password_controller.post("/reset-password", tags=["Management Password"])
def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    return change_password(request, db)


    