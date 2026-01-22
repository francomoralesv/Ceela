from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from src.services.database.db_connection import get_db
from src.services.user.user_service import list_users, list_user_by_id, delete_user, update_user_by_admin, update_user_by_user, update_user_status, delete_user_and_dependencies
from src.models.schemas.users.user_update import UserUpdate, UserUpdateAdminRole, UserUpdateAdminActive
from src.models.entity.user_table import UserTable
from src.utils.security.token.jwt_login import verify_token

router_user_controller = APIRouter()

@router_user_controller.get("/users/", tags=["Management Users"])
def get_users(search: Optional[str] = None, limit: int = 5, num_pag: int = 1, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    return list_users(search, limit, num_pag, db, user)


@router_user_controller.get("/user/", tags=["Management Users"])
def get_user_by_id(id: int = None, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    return list_user_by_id(db, user, id)


@router_user_controller.delete("/user/{id}/delete", tags=["Management Users"])
def remove_user(id: int, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    return delete_user(id, db, user)


@router_user_controller.put("/user/me/update", tags=["Management Users"])
def update_by_user(user_update: UserUpdate, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    return update_user_by_user(user_update, db, user)


@router_user_controller.put("/user/{id}/update", tags=["Management Users"])
def update_by_admin(id: int, user: UserUpdateAdminRole, db: Session = Depends(get_db), user_table: dict = Depends(verify_token)):
    return update_user_by_admin(id, user, db, user_table)


@router_user_controller.put("/user/{id}/update-status", tags=["Management Users"])
def update_by_admin(id: int, user: UserUpdateAdminActive, db: Session = Depends(get_db), user_table: dict = Depends(verify_token)):
    return update_user_status(id, user, db, user_table)


@router_user_controller.delete("/user/{id}/force-delete", tags=["Management Users"])
def force_remove_user(id: int, db: Session = Depends(get_db)):
    """
    Elimina un usuario y todas sus dependencias sin requerir autenticación.
    """
    # Aquí deberías implementar la lógica para eliminar el usuario y sus dependencias.
    # Por ejemplo:
    # 1. Buscar y eliminar dependencias relacionadas (roles, perfiles, etc.)
    # 2. Eliminar el usuario
    # Puedes reutilizar la lógica de delete_user pero sin verify_token
    return delete_user_and_dependencies(id, db)
