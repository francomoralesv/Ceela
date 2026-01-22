from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.obstruction.orientation import get_orientation, update_orientation, delete_orientation, create_orientation
from src.models.entity.obstruction import OrientationCreate

router_orientation_controller = APIRouter()


@router_orientation_controller.post("/orientation-create/{enclosure_id}", tags=["Obstruction-Orientation"])
def create_orientation_endpoint(enclosure_id: int, orientation: OrientationCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_orientation(enclosure_id, orientation, current_user, db)


@router_orientation_controller.get("/orientation/{orientation_id}", tags=["Obstruction-Orientation"])
def get_orientation_endpoint(orientation_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_orientation(orientation_id, current_user, db)


@router_orientation_controller.put("/orientation-update/{orientation_id}", tags=["Obstruction-Orientation"])
def update_orientation_endpoint(orientation_id: int, orientation: OrientationCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_orientation(orientation_id, orientation, current_user, db)


@router_orientation_controller.delete("/orientation-delete/{orientation_id}", tags=["Obstruction-Orientation"])
def delete_orientation_endpoint(orientation_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_orientation(orientation_id, current_user, db)