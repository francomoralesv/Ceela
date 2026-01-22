import textwrap
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.services.database.db_connection import get_db
from src.utils.security.token.jwt_login import verify_token
from src.services.calculation_result.calculation_result_service import (
    get_calculation_result,
    get_calculation_results_by_project,
    delete_calculation_result
)
from src.services.calculation_result.calculation_result_service import get_calculation_results_report
router_calculation_result_controller = APIRouter(prefix="/calculation-results")



@router_calculation_result_controller.get("/report",
                                          response_model=dict,
                                          summary="Generar reporte de resultados de cálculo",
                                          description="Genera un reporte agregado de resultados de cálculo con filtros por año, país, zona y tipología de edificación.",
                                          responses={
                                              200: {"description": "Reporte generado exitosamente"},
                                              403: {"description": "Permiso denegado"},
                                              500: {"description": "Error interno del servidor"}
                                          }
                                          )
def get_calculation_results_report_endpoint(
        year: Optional[int] = None,
        country: Optional[str] = None,
        zone: Optional[str] = None,
        building_type: Optional[str] = None,
        db: Session = Depends(get_db)
):

    try:
        report = get_calculation_results_report(
            year=year,
            country=country,
            zone=zone,
            building_type=building_type,
            db=db
        )
        return report
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el reporte: {str(e)}"
        )

@router_calculation_result_controller.get(
    "/projects/{project_id}",
    tags=["Calculation Results"],
    summary="Obtener el resultado de cálculo más reciente de un proyecto",
    description=textwrap.dedent("""
    **Obtiene el resultado de cálculo más reciente para un proyecto específico.**
    
    🚀 **Funcionamiento:**  
    - Verifica que el usuario tenga permisos sobre el proyecto.  
    - Retorna el resultado de cálculo más reciente para el proyecto.  
    
    🔒 **Restricciones:**  
    - Solo el propietario del proyecto o un administrador puede ver los resultados.  
    
    📤 **Respuestas:**  
    - ✅ `200`: Resultado obtenido exitosamente.  
    - ❌ `403`: No tienes permisos para este proyecto.  
    - ❌ `404`: Proyecto no encontrado.  
    - ❌ `500`: Error interno del servidor.
    """)
)
def get_calculation_results_by_project_endpoint(
    project_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return get_calculation_results_by_project(
        project_id=project_id,
        current_user=current_user,
        db=db,
    )



@router_calculation_result_controller.delete(
    "/calculation-results/{result_id}/",
    tags=["Calculation Results"],
    summary="Eliminar un resultado de cálculo",
    description=textwrap.dedent("""
    **Elimina un resultado de cálculo existente.**
    
    🚀 **Funcionamiento:**  
    - Verifica que el usuario tenga permisos sobre el proyecto asociado al resultado.  
    - Elimina el resultado de cálculo de la base de datos.  
    
    🔒 **Restricciones:**  
    - Solo el propietario del proyecto o un administrador puede eliminar los resultados.  
    
    📤 **Respuestas:**  
    - ✅ `200`: Eliminación exitosa.  
    - ❌ `403`: No tienes permisos para eliminar este resultado.  
    - ❌ `404`: Resultado no encontrado.  
    - ❌ `500`: Error interno del servidor.
    """)
)
def delete_calculation_result_endpoint(
    result_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return delete_calculation_result(
        result_id=result_id,
        current_user=current_user,
        db=db
    )
