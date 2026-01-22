from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.entity.agua_caliente import AguaCalienteSanitaria
from src.models.entity.project_table import Project
from src.models.schemas.agua_caliente.agua_caliente_sanitaria import AguaCalienteSanitariaCreate


def save_data_agua_caliente(project_id: int, current_user: dict, db: Session, data: AguaCalienteSanitariaCreate):
    if current_user.get("role_id") == 1:
        raise HTTPException(status_code=403, detail="El administrador no puede crear ni actualizar Agua Caliente Sanitaria.")

    exist_project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"]
    ).first()

    if not exist_project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    try:
        db_data = db.query(AguaCalienteSanitaria).filter(
            AguaCalienteSanitaria.project_id == project_id
        ).first()

        if db_data:
            for field, value in data.model_dump().items():
                setattr(db_data, field, value)
        else:
            db_data = AguaCalienteSanitaria(
                **data.model_dump(), project_id=project_id)
            db.add(db_data)

        db.commit()
        db.refresh(db_data)
        return db_data

    except Exception as e:
        db.rollback()
        print(f"❌ Error al guardar los datos de agua caliente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_all_agua_caliente(project_id: int, current_user: dict, db: Session) -> List[AguaCalienteSanitaria]:
    # Verificar si el proyecto existe y pertenece al usuario actual
    if current_user["role_id"] == 1:
        project = db.query(Project).filter(Project.id == project_id).first()
    else:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user["user_id"]
        ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Obtener todos los registros relacionados al proyecto
    try:
        records = db.query(AguaCalienteSanitaria).filter(
            AguaCalienteSanitaria.project_id == project_id
        ).all()

        return records
    except Exception as e:
        print(f"❌ Error al obtener los datos de agua caliente: {e}")
        raise HTTPException(
            status_code=500, detail="Error al obtener los datos")


def get_agua_caliente_by_project(project_id: int, current_user=None, db: Session = None):
    # Verificar si el proyecto existe y pertenece al usuario actual
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

        # Obtener el registro asociado al proyecto


    record = db.query(AguaCalienteSanitaria).filter(
        AguaCalienteSanitaria.project_id == project_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=404, detail="Registro de agua caliente no encontrado")

    return record
