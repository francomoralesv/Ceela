from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.services.database.db_connection import get_db 
from src.services.datos.materials import get_material_details, get_nodos_area_by_orientation, get_translucent_window_area, get_material_details_by_project, get_nodos_area_by_orientation_by_project, get_translucent_window_area_by_project
from src.utils.security.token.jwt_login import verify_token # Asegúrate de tener definida la dependencia para la sesión de base de datos

router_controller_datos = APIRouter()

@router_controller_datos.get("/materials/{enclosure_id}")
def obtener_datos_recinto(enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        resultados = get_material_details(enclosure_id, current_user, db)
        return {"ok": True, "data": resultados}
    except Exception as e:
        print(f"Error al procesar los datos del recinto: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar los datos del recinto")
    
    
@router_controller_datos.get("/distributions/{enclosure_id}")
def obtener_datos_nodos_area(enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        resultados = get_nodos_area_by_orientation(enclosure_id, db, current_user)
        return resultados
    except Exception as e:
        print(f"Error al procesar los datos del recinto: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar los datos del recinto")
    
    
@router_controller_datos.get("/windows-total/{enclosure_id}")
def obtener_datos_windows_total(enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        resultados = get_translucent_window_area(enclosure_id, current_user, db)
        return resultados
    except Exception as e:
        print(f"Error al procesar los datos del recinto: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar los datos del recinto")
    
    
    
@router_controller_datos.get("/materials-by-project/{project_id}")
def obtener_datos_recinto_by_project(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        resultados = get_material_details_by_project(project_id, current_user, db)
        return {"ok": True, "data": resultados}
    except Exception as e:
        print(f"Error al procesar los datos del recinto: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar los datos del recinto")
    
    
@router_controller_datos.get("/distributions-by-project/{project_id}")
def obtener_datos_nodos_area_by_project(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        resultados = get_nodos_area_by_orientation_by_project(project_id, db, current_user)
        return resultados
    except Exception as e:
        print(f"Error al procesar los datos del recinto: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar los datos del recinto")
    
    
@router_controller_datos.get("/windows-total-by-project/{project_id}")
def obtener_datos_windows_total_by_project(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        resultados = get_translucent_window_area_by_project(project_id, current_user, db)
        return resultados
    except Exception as e:
        print(f"Error al procesar los datos del recinto: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar los datos del recinto")