from typing import Optional
from fastapi import HTTPException  
from sqlalchemy.orm import Session
from src.models.entity.indicadores_finales import IndicadoresFinales
from src.models.schemas.indicadores_finales.indicadores_finales import IndicadoresFinalesSave
from src.models.entity.project_table import Project

def save_indicadores_finales(indicadores: IndicadoresFinalesSave, type: str, project_id: int, current_user: dict, db: Session):
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user["user_id"]
        ).first()

        if not project:
            raise HTTPException(status_code=404, detail="El proyecto no existe o no pertenece al usuario.")

        indicador = IndicadoresFinales(**indicadores.model_dump(), type=type, project_id=project_id)
        db.add(indicador)
        db.commit()
        db.refresh(indicador)
        return {"message": "Indicadores guardados correctamente", "indicador": indicador}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar los indicadores: {str(e)}")
    
    
    

def get_indicadores_finales(project_id: int, current_user: dict, db: Session, type: Optional[str] = None):
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user["user_id"]
        ).first()

        if not project:
            raise HTTPException(status_code=404, detail="El proyecto no existe o no pertenece al usuario.")

        query = db.query(IndicadoresFinales).filter_by(project_id=project_id)

        if type:
            query = query.filter_by(type=type)

        indicadores = query.all()

        if not indicadores:
            raise HTTPException(status_code=404, detail="No se encontraron indicadores para este proyecto.")

        return indicadores

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los indicadores: {str(e)}")