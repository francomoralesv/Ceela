from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.angle_azimut.angle_azimut_service import get_angulos_azimut, get_angulos_azimut_and_orientation


router_angle_azimut_controller = APIRouter()

@router_angle_azimut_controller.get("/angle-azimut", tags=["Azimuts"])
def get_angulos_azimut_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_angulos_azimut(current_user, db)


@router_angle_azimut_controller.get("/angle-azimut-and-orientation", tags=["Azimuts"])
def get_angulos_azimut_and_orientation_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_angulos_azimut_and_orientation(current_user, db)