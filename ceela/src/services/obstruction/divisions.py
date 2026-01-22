from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.entity.project_table import Project
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.schemas.obstruction.obstruction import DivisionCreate
from src.models.entity.obstruction import Orientation, Division
from sqlalchemy import func



def create_divison(
    orientation_id: int,
    divison: DivisionCreate,
    current_user: dict,
    db: Session
):
    # ————— Validaciones previas igual que antes —————
    enclosure_id = (
        db
        .query(Orientation.enclosure_id)
        .filter(Orientation.id == orientation_id)
        .scalar()
    )
    if not enclosure_id:
        raise HTTPException(status_code=400, detail="No hay una orientación asociada")
    project_id = (
        db
        .query(EnclosureGenerals.project_id)
        .filter(EnclosureGenerals.id == enclosure_id)
        .scalar()
    )
    if not project_id:
        raise HTTPException(status_code=400, detail="No se encontró el proyecto")
    project = (
        db
        .query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user["user_id"],
            Project.is_deleted == False
        )
        .first()
    )
    if not project:
        raise HTTPException(status_code=400, detail="Proyecto no pertenece al usuario")

    # ————— Cálculo de num_orientation —————
    max_num = (
        db
        .query(func.max(Division.num_orientation))
        .filter(Division.orientation_id == orientation_id)
        .scalar()
    )
    nuevo_num = 1 if max_num is None else max_num + 1

    # ————— Creación de la división con num_orientation —————
    my_division = Division(
        **divison.model_dump(),            # tus otros campos
        orientation_id=orientation_id,
        num_orientation=nuevo_num
    )

    try:
        db.add(my_division)
        db.commit()
        db.refresh(my_division)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=403, detail="Error al crear la división")

    return my_division



def update_division(division_id: int, division_update: DivisionCreate, current_user: dict, db: Session):
    # Obtener la división existente
    my_division = db.query(Division).filter(Division.id == division_id).first()
    if not my_division:
        raise HTTPException(status_code=404, detail="División no encontrada")
    
    # Validar permisos: obtener el enclosure_id a partir de la orientación de la división
    orientation_id = my_division.orientation_id
    enclosure_id = db.query(Orientation.enclosure_id).filter(Orientation.id == orientation_id).scalar()
    if not enclosure_id:
        raise HTTPException(
            status_code=400,
            detail="La orientación no está asociada a un recinto"
        )
    
    # Validar que el recinto esté vinculado a un proyecto
    project_id = db.query(EnclosureGenerals.project_id).filter(EnclosureGenerals.id == enclosure_id).scalar()
    if not project_id:
        raise HTTPException(
            status_code=400,
            detail="No se encontró el recinto vinculado a un proyecto"
        )
    
    # Validar que el proyecto pertenezca al usuario actual
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"],
        Project.is_deleted == False
    ).first()
    if not project:
        raise HTTPException(
            status_code=400,
            detail="El proyecto no pertenece al usuario actual"
        )
    
    # Actualizar los campos enviados; usamos model_dump(exclude_unset=True) para solo actualizar lo enviado
    update_data = division_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(my_division, key, value)
    
    try:
        db.commit()
        db.refresh(my_division)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error al actualizar la división"
        )
        
    return my_division


def get_division(division_id: int, current_user: dict, db: Session):
    # Obtener la división
    my_division = db.query(Division).filter(Division.id == division_id).first()
    if not my_division:
        raise HTTPException(status_code=404, detail="División no encontrada")
    
    # Validar permisos, usando la misma cadena de validación
    orientation_id = my_division.orientation_id
    enclosure_id = db.query(Orientation.enclosure_id).filter(Orientation.id == orientation_id).scalar()
    if not enclosure_id:
        raise HTTPException(
            status_code=400,
            detail="La orientación no está asociada a un recinto"
        )
    
    project_id = db.query(EnclosureGenerals.project_id).filter(EnclosureGenerals.id == enclosure_id).scalar()
    if not project_id:
        raise HTTPException(
            status_code=400,
            detail="No se encontró el recinto vinculado a un proyecto"
        )
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"],
        Project.is_deleted == False
    ).first()
    if not project:
        raise HTTPException(
            status_code=400,
            detail="El proyecto no pertenece al usuario actual"
        )
    
    return my_division


def delete_division(division_id: int, current_user: dict, db: Session):
    # Obtener la división
    my_division = db.query(Division).filter(Division.id == division_id, Division.is_deleted == False).first()
    if not my_division:
        raise HTTPException(status_code=404, detail="División no encontrada")
    
    # Validar permisos (igual que antes)
    orientation_id = my_division.orientation_id
    enclosure_id = db.query(Orientation.enclosure_id).filter(Orientation.id == orientation_id).scalar()
    if not enclosure_id:
        raise HTTPException(status_code=400, detail="La orientación no está asociada a un recinto")
    
    project_id = db.query(EnclosureGenerals.project_id).filter(EnclosureGenerals.id == enclosure_id).scalar()
    if not project_id:
        raise HTTPException(status_code=400, detail="No se encontró el recinto vinculado a un proyecto")
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"],
        Project.is_deleted == False
    ).first()
    if not project:
        raise HTTPException(status_code=400, detail="El proyecto no pertenece al usuario actual")
    
    try:
        # Marcar como eliminada
        my_division.is_deleted = True
        db.commit()

        # Reordenar num_orientation de las divisiones restantes en la misma orientación
        divisiones_activas = (
            db.query(Division)
            .filter(
                Division.orientation_id == orientation_id,
                Division.is_deleted == False
            )
            .order_by(Division.num_orientation.asc())
            .all()
        )

        for idx, division in enumerate(divisiones_activas, start=1):
            division.num_orientation = idx
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=403, detail="Error al eliminar o reordenar divisiones")
    
    return {"message": "División eliminada y numeración actualizada"}