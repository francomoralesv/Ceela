from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from sqlalchemy import desc, not_

from src.models.calculation_result import CalculationResult
from src.models.entity.project_table import Project
from sqlalchemy import extract

def upsert_calculation_result(
    project_id: int,
    final_indicators: Dict[str, Any],
    result_by_enclosure: Dict[str, Any],
    co2_eq: Dict[str, Any],
    current_user: dict,
    db: Session,
    result_id: Optional[int] = None
):
    """
    Crea o actualiza un resultado de cálculo para un proyecto.
    Si result_id es proporcionado, actualiza el resultado existente.
    Si result_id es None pero existe un resultado para el project_id, actualiza el resultado existente.
    Si no existe ningún resultado, crea uno nuevo.
    """
    
    # Verificar que el proyecto existe y pertenece al usuario
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()
        
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
    # Si se proporciona result_id, intentar actualizar ese resultado específico
    if result_id is not None:
        result = db.query(CalculationResult).filter(CalculationResult.id == result_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Resultado de cálculo no encontrado")
        
        # Verificar que el resultado pertenece al proyecto correcto
        if result.project_id != project_id:
            raise HTTPException(status_code=400, detail="El resultado no pertenece al proyecto especificado")
            
        is_update = True
            
    else:
        # Si no se proporciona result_id, buscar si existe algún resultado para el project_id
        # y actualizar el más reciente
        result = db.query(CalculationResult).filter(
            CalculationResult.project_id == project_id
        ).order_by(desc(CalculationResult.created_at)).first()
        
        is_update = result is not None
    
    try:
        if is_update:
            # Actualizar el resultado existente
            result.final_indicators = final_indicators
            result.result_by_enclosure = result_by_enclosure
            result.co2_eq = co2_eq
            db.commit()
            db.refresh(result)
            
            return {
                "id": result.id,
                "project_id": result.project_id,
                "final_indicators": result.final_indicators,
                "result_by_enclosure": [datos for datos in result.result_by_enclosure if not datos["is_base"]],
                "co2_eq": result.co2_eq,
                "created_at": result.created_at,
                "message": "Resultado de cálculo actualizado exitosamente"
            }
        else:
            # Crear nuevo resultado
            new_calculation_result = CalculationResult(
                project_id=project_id,
                final_indicators=final_indicators,
                result_by_enclosure=result_by_enclosure,
                co2_eq=co2_eq
            )
            
            db.add(new_calculation_result)
            db.commit()
            db.refresh(new_calculation_result)
            
            return {
                "id": new_calculation_result.id,
                "project_id": new_calculation_result.project_id,
                "final_indicators": new_calculation_result.final_indicators,
                "result_by_enclosure": [datos for datos in new_calculation_result.result_by_enclosure if not datos["is_base"]],
                "co2_eq": new_calculation_result.co2_eq,
                "created_at": new_calculation_result.created_at,
                "message": "Resultado de cálculo creado exitosamente"
            }
    except Exception as e:
        db.rollback()
        operation = "actualizar" if is_update else "crear"
        raise HTTPException(status_code=500, detail=f"Error al {operation} el resultado de cálculo: {str(e)}")


def get_calculation_result(
    result_id: int,
    current_user: dict,
    db: Session
):
    """
    Obtiene un resultado de cálculo específico por su ID.
    """
    result = db.query(CalculationResult).filter(CalculationResult.id == result_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Resultado de cálculo no encontrado")
    
    # Verificar que el usuario tiene acceso al proyecto asociado
    project = db.query(Project).filter(
        Project.id == result.project_id,
        Project.user_id == current_user["user_id"],
        not Project.is_deleted
    ).first()
    
    if not project and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a este resultado")
    
    return {
        "id": result.id,
        "project_id": result.project_id,
        "final_indicators": result.final_indicators,
        "result_by_enclosure": result.result_by_enclosure,
        "co2_eq": result.co2_eq,
        "created_at": result.created_at
    }


def get_calculation_results_by_project(
    project_id: int,
    current_user: dict,
    db: Session
):
    """
    Obtiene el resultado de cálculo más reciente para un proyecto específico.
    """
    result = db.query(CalculationResult).filter(
        CalculationResult.project_id == project_id
    ).order_by(
        desc(CalculationResult.created_at)
    ).first()
    
    if not result:
        return None
    return {
        "id": result.id,
        "project_id": result.project_id,
        "final_indicators": result.final_indicators,
        "result_by_enclosure": [datos for datos in result.result_by_enclosure if not datos["is_base"]],
        "co2_eq": result.co2_eq,
        "created_at": result.created_at
    }

def delete_calculation_result(
    result_id: int,
    current_user: dict,
    db: Session
):
    """
    Elimina un resultado de cálculo existente.
    """
    result = db.query(CalculationResult).filter(CalculationResult.id == result_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Resultado de cálculo no encontrado")
    project = db.query(Project).filter(
        Project.id == result.project_id,
        Project.user_id == current_user["user_id"],
        not Project.is_deleted
    ).first()
    
    if not project and current_user.get("role", "") != "admin":
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este resultado")
    
    try:
        db.delete(result)
        db.commit()
        
        return {
            "message": "Resultado de cálculo eliminado exitosamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar el resultado de cálculo: {str(e)}")


def get_calculation_results_report(db: Session, user_id=None, year=None, zone=None, country=None, building_type=None) -> Dict:
    """
    Genera un reporte agregado de los resultados de cálculo con filtros por año, país, zona y tipología de edificación.
    Si no se proporciona ningún filtro, devuelve datos de todos los resultados de cálculo.

    Args:
        user_id: ID del usuario para filtrar los resultados
        year: Año para filtrar los resultados (basado en created_at)
        zone: Zona del proyecto (desde project_metadata['zone'])
        country: País para filtrar los proyectos
        building_type: Tipo de edificación (main_use_type del proyecto)
        db: Sesión de base de datos

    Returns:
        Diccionario con los datos agregados del reporte
    """
    query = db.query(CalculationResult).join(Project, CalculationResult.project_id == Project.id).filter(not_(Project.is_deleted))

    if year is not None:
        query = query.filter(extract('year', CalculationResult.created_at) == year)
    if user_id is not None:
        query = query.filter(Project.user_id == user_id)
    if country is not None:
        query = query.filter(Project.country == country)
    if building_type is not None:
        query = query.filter(Project.building_type == building_type)

    results = query.all()

    if zone is not None:
        results = [r for r in results if r.project and r.project.project_metadata and r.project.project_metadata.get("zone") == zone]

    total_co2_eq = 0
    total_disconfort_calef = 0
    total_disconfort_ref = 0
    total_co2_eq_baseline = 0
    total_disconfort_baseline = 0
    count_co2_baseline = 0
    count_disconfort_baseline = 0

    total_demanda_calef = 0
    total_demanda_ref = 0
    total_consumo_calef = 0
    total_consumo_ref = 0

    for result in results:
        if isinstance(result.co2_eq, dict):
            total_co2_eq += result.co2_eq.get("total", 0)

        if isinstance(result.final_indicators, dict):
            total_disconfort_calef += result.final_indicators.get("disconfort_calef", 0)
            total_disconfort_ref += result.final_indicators.get("disconfort_ref", 0)

            if "co2_eq_vs_caso_base" in result.final_indicators:
                total_co2_eq_baseline += result.final_indicators["co2_eq_vs_caso_base"]
                count_co2_baseline += 1
            
            if "disconfort_vs" in result.final_indicators:
                total_disconfort_baseline += result.final_indicators["disconfort_vs"]
                count_disconfort_baseline += 1

            total_demanda_calef += result.final_indicators.get("demanda_calefaccion_final2", 0)
            total_demanda_ref += result.final_indicators.get("demanda_ref_final2", 0)
            total_consumo_calef += result.final_indicators.get("consumo_calefaccion_final2", 0)
            total_consumo_ref += result.final_indicators.get("consumo_refrigeracion_final2", 0)

        elif isinstance(result.result_by_enclosure, list):
            # Fallback to calculate from result_by_enclosure
            enclosure_co2_total = 0
            enclosure_co2_base_total = 0
            enclosure_disconfort_total = 0
            enclosure_disconfort_base_total = 0

            for enclosure in result.result_by_enclosure:
                enclosure_co2_total += enclosure.get("co2_eq_total", 0)
                enclosure_co2_base_total += enclosure.get("caso_base_co2_eq_total", 0)
                enclosure_disconfort_total += enclosure.get("hrs_disconfort_calefaccion", 0) + enclosure.get("hrs_disconfort_refrigeracion", 0)
                enclosure_disconfort_base_total += enclosure.get("caso_base_hrs_disconfort_calefaccion", 0) + enclosure.get("caso_base_hrs_disconfort_refrigeracion", 0)

            if enclosure_co2_base_total > 0:
                co2_baseline = (1 - (enclosure_co2_total / enclosure_co2_base_total)) * 100
                total_co2_eq_baseline += co2_baseline
                count_co2_baseline += 1

            if enclosure_disconfort_base_total > 0:
                disconfort_baseline = (1 - (enclosure_disconfort_total / enclosure_disconfort_base_total)) * 100
                total_disconfort_baseline += disconfort_baseline
                count_disconfort_baseline += 1

    num_results = len(results)
    avg_co2_eq = total_co2_eq / num_results if num_results > 0 else 0
    avg_disconfort_calef = total_disconfort_calef / num_results if num_results > 0 else 0
    avg_disconfort_ref = total_disconfort_ref / num_results if num_results > 0 else 0
    avg_co2_baseline = total_co2_eq_baseline / count_co2_baseline if count_co2_baseline > 0 else 0
    avg_disconfort_baseline = total_disconfort_baseline / count_disconfort_baseline if count_disconfort_baseline > 0 else 0

    avg_demanda_calef = total_demanda_calef / num_results if num_results > 0 else 0
    avg_demanda_ref = total_demanda_ref / num_results if num_results > 0 else 0
    avg_consumo_calef = total_consumo_calef / num_results if num_results > 0 else 0
    avg_consumo_ref = total_consumo_ref / num_results if num_results > 0 else 0
    
    return {
        "co2_eq": {
            "total": round(avg_co2_eq, 2),
            "baseline": round(avg_co2_baseline, 2)
        },
        "horas_confort_anual": {
            "calefaccion": round(avg_disconfort_calef, 2),
            "refrigeracion": round(avg_disconfort_ref, 2),
            "baseline": round(avg_disconfort_baseline, 2)
        },
        "demanda_vs_consumo": {
            "calefaccion": {
                "demanda": round(avg_demanda_calef, 2),
                "consumo": round(avg_consumo_calef, 2)
            },
            "refrigeracion": {
                "demanda": round(avg_demanda_ref, 2),
                "consumo": round(avg_consumo_ref, 2)
            }
        },
        "total_resultados": num_results,
        "filtros_aplicados": {
            "year": year,
            "zone": zone,
            "country": country,
            "building_type": building_type,
            "user_id": user_id
        }
    }
