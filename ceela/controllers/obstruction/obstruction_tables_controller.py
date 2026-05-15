from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.obstruction.obstruction_table import get_table_obstruction, delete_table

router_obstruction_controller = APIRouter()


@router_obstruction_controller.get("/obstruction/{enclosure_id}", tags=["Obstruction"])
def get_table_endpoint(enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_table_obstruction(enclosure_id, current_user, db)


@router_obstruction_controller.delete("/obstruction/{orientation_id}", tags=["Obstruction"])
def delete_table_endpoint(orientation_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_table(orientation_id, current_user, db)

