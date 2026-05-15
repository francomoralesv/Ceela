from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from src.services.database.db_connection import get_db
from src.models.schemas.users.user_create import UserCreate, UserCreateAdmin
from src.models.schemas.users.user_login import UserLogin
from src.models.entity.user_table import UserTable
from src.services.auth.auth_service import register, login, admin, validate_2fa, register_admin, logout
from src.utils.security.token.jwt_login import verify_token
from src.models.schemas.autentication_2fa.request2FA import Request2FA


router_auth_controller = APIRouter()


@router_auth_controller.delete("/logout", tags=["Auth"])
def logout_user(token: str = Header(..., description="Revocar Token"), db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    return logout(current_user, token, db)


@router_auth_controller.post("/register", tags=["Auth"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return register(user, db)


@router_auth_controller.post("/register-admin", tags=["Auth"])
def register_admin_endpoint(user: UserCreateAdmin, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return register_admin(user, current_user, db)


@router_auth_controller.post("/login", tags=["Auth"])
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    return login(user, db)


@router_auth_controller.post("/2fa-verify", tags=["Auth"])
def two_factor_authentication(two_factor_data: Request2FA, db: Session = Depends(get_db)):
    print(two_factor_data.otp)
    print(two_factor_data.email)
    return validate_2fa(two_factor_data, db)
    

@router_auth_controller.post("/admin", tags=["Auth"])
def admin_user(user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return admin(user, db)

    
@router_auth_controller.get("/profile")
def get_user_profile(current_user: dict = Depends(verify_token)):
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "lastname": current_user["lastname"],
        "role_id": current_user["role_id"]
    }