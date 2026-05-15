from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.services.agua_caliente.agua_caliente_service import save_data_agua_caliente, get_all_agua_caliente
from src.services.database.db_connection import get_db
from src.utils.security.token.jwt_login import verify_token
from src.models.schemas.agua_caliente.agua_caliente_sanitaria import AguaCalienteSanitariaCreate


router_agua_caliente = APIRouter()


@router_agua_caliente.post("/agua-caliente/{project_id}", tags=["Agua Caliente"])
async def save_agua_caliente(
    project_id: int,
    data: AguaCalienteSanitariaCreate,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return save_data_agua_caliente(project_id, current_user, db, data)
    



@router_agua_caliente.get('/agua-caliente-obtener/{project_id}', tags=["Agua Caliente"])
async def get_agua_caliente(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_all_agua_caliente(project_id, current_user, db)


