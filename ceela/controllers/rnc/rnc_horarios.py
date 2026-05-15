from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.services.database.db_connection import get_db
from src.utils.security.token.jwt_login import verify_token
from src.services.rnc.rnc_horarios import calculate_tabla_horarios_1
import logging
import traceback


router_rnc_horarios = APIRouter()

@router_rnc_horarios.get("/rnc/horarios/{project_id}", tags=["RNC"], summary="Obtener datos de RNC")
def get_rnc_horarios_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        return calculate_tabla_horarios_1(db, current_user, project_id)
    except Exception as e:
        logging.error(f"[RNC HORARIOS] Error en endpoint: {str(e)}")
        logging.error(traceback.format_exc())
        raise

