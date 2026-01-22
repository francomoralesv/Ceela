from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.services.database.db_connection import get_db 
from src.utils.security.token.jwt_login import verify_token
from src.services.datos.suma_puentes import get_htr_wk_by_project

router_suma_puentes = APIRouter()


@router_suma_puentes.get('/get-htr-wk/{project_id}', tags=['HTR-WK'])
def get_htr_wk_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_htr_wk_by_project(project_id, current_user, db)