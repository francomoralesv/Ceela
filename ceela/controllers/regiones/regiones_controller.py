from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.regiones.regiones import get_comunas_by_region, get_zona_termicas, get_regiones


router_regiones_controller = APIRouter()



@router_regiones_controller.get("/regiones", tags=["Regiones"])
def get_regiones_endpoint(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_regiones(current_user, db)


@router_regiones_controller.get("/comunas/{region_id}", tags=["Regiones"])
def get_comunas_by_region_endpoint(region_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_comunas_by_region(region_id, current_user, db)


@router_regiones_controller.get("/zonas-termicas/{comuna_id}", tags=["Regiones"])
def get_zona_termicas_endpoint(comuna_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_zona_termicas(comuna_id, current_user, db)
