from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.models.schemas.indicadores_finales.indicadores_finales import IndicadoresFinalesSave
from src.services.indicadores_finales.indicadores_finales import save_indicadores_finales, get_indicadores_finales


router_indicadores_finales = APIRouter()


@router_indicadores_finales.post('indicadores-finales/{project_id}/{type}', tags=['Indicadores Finales'])
def save_indicadores(indicadores: IndicadoresFinalesSave, type: str, project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return save_indicadores_finales(indicadores, type, project_id, current_user, db)



@router_indicadores_finales.get('/get-indicadores-finales/{project_id}/', tags=['Indicadores Finales'])
def get_indicadores(type: Optional[str], project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_indicadores_finales(project_id, current_user, db, type)