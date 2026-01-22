from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.obstruction.divisions import get_division, update_division, delete_division, create_divison
from src.models.schemas.obstruction.obstruction import DivisionCreate


router_division_controller = APIRouter()


@router_division_controller.post("/division-create/{orientation_id}", tags=["Obstruction-Divisions"])
def create_division_endpoint(orientation_id: int, division: DivisionCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_divison(orientation_id, division, current_user, db)


@router_division_controller.get("/divisions/{division_id}", tags=["Obstruction-Divisions"])
def get_division_endpoint(division_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_division(division_id, current_user, db)


@router_division_controller.put("/division-update/{division_id}", tags=["Obstruction-Divisions"])
def update_division_endpoint(division_id: int, division: DivisionCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_division(division_id, division, current_user, db)


@router_division_controller.delete("/division-delete/{division_id}", tags=["Obstruction-Divisions"])
def delete_division_endpoint(division_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_division(division_id, current_user, db)