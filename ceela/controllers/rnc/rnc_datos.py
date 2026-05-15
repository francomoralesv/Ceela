from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.rnc.rnc_calculator import calculate_rnc_area_u_km_op, calculate_rnc_muro, calculate_rnc_piso, calculate_rnc_techo, datos_rnc


router_rnc_datos = APIRouter()

@router_rnc_datos.get("/rnc/area_u_km_op/{project_id}", tags=["RNC"], summary="Obtener datos de RNC")
def get_rnc_datos_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return calculate_rnc_area_u_km_op(current_user, project_id, db)
    
@router_rnc_datos.get("/rnc/muro/{project_id}", tags=["RNC"], summary="Obtener datos de RNC")
def get_rnc_datos_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return calculate_rnc_muro(current_user, project_id, db)

@router_rnc_datos.get("/rnc/techo/{project_id}", tags=["RNC"], summary="Obtener datos de RNC")
def get_rnc_datos_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return calculate_rnc_techo(current_user, project_id, db)


@router_rnc_datos.get("/rnc/piso/{project_id}", tags=["RNC"], summary="Obtener datos de RNC")
def get_rnc_datos_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return calculate_rnc_piso(current_user, project_id, db)

@router_rnc_datos.get("/rnc/datos/{project_id}", tags=["RNC"], summary="Obtener datos de RNC")
def get_rnc_datos_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return datos_rnc(current_user, project_id, db)
