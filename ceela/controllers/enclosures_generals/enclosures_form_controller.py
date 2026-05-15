from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.models.schemas.enclosures_generals.enclosure_create import EnclosureGeneralsCreate
from src.services.enclosures_generals.enclosure_form_service import create_enclosure_general, get_enclosures_general, update_enclosure_general, delete_enclosure_general
from src.services.enclosures_generals.levels import get_levels

router_enclosure_generals_controller = APIRouter()


@router_enclosure_generals_controller.post("/enclosure-generals-create/{project_id}", tags=["Enclosures-Generals"])
def create_enclosure_general_endpoint(project_id: int, enclosure: EnclosureGeneralsCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_enclosure_general(project_id, enclosure, current_user, db)


@router_enclosure_generals_controller.get("/enclosure-generals/{project_id}", tags=["Enclosures-Generals"])
def get_enclosure_general_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_enclosures_general(project_id, current_user, db)


@router_enclosure_generals_controller.put("/enclosure-generals-update/{project_id}/{enclosure_id}", tags=["Enclosures-Generals"])
def update_enclosure_general_endpoint(project_id: int, enclosure_id: int, enclosure: EnclosureGeneralsCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_enclosure_general(project_id, enclosure_id, enclosure, current_user, db)


@router_enclosure_generals_controller.delete("/enclosure-generals-delete/{project_id}/{enclosure_id}", tags=["Enclosures-Generals"])
def delete_enclosure_general_endpoint(project_id: int, enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_enclosure_general(project_id, enclosure_id, current_user, db)


@router_enclosure_generals_controller.get("/levels", tags=["Enclosures-Generals"])
def get_levels_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_levels(db, current_user)
