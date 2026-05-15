from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.services.database.db_connection import get_db 
from src.utils.security.token.jwt_login import verify_token
from src.services.datos.recintos import get_info_recinto


router_controller_recinto = APIRouter()


@router_controller_recinto.get("/recinto-info/{project_id}", description="Si se proporciona un enclosure_id, se retorna únicamente ese enclosure; de lo contrario, se retornan todos los enclosures asociados al project_id.")
def obtener_datos_nodos_area(project_id: int, enclosure_id: int = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        resultados = get_info_recinto(project_id, current_user, db, enclosure_id)
        return resultados
    except Exception as e:
        print(f"Error al procesar los datos del recinto: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar los datos del recinto")