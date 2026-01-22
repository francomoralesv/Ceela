from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.entity.project_table import Project
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.schemas.obstruction.obstruction import DivisionCreate
from src.models.entity.obstruction import Orientation, Division


def get_table_obstruction(enclosure_id: int, current_user: dict, db: Session):
    # Validar que el recinto esté vinculado a un proyecto
    project_id = db.query(EnclosureGenerals.project_id).filter(
        EnclosureGenerals.id == enclosure_id
    ).scalar()
    if not project_id:
        raise HTTPException(
            status_code=400,
            detail="No se encontró el recinto vinculado a un proyecto"
        )
    
    # Si el usuario no es administrador (role_id != 1), se valida que el proyecto pertenezca al usuario
    if current_user["role_id"] != 1:
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
    else:
        # Si es administrador, se valida solo que el proyecto exista y no esté borrado
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.is_deleted == False
        ).first()
        if not project:
            raise HTTPException(
                status_code=400,
                detail="El proyecto no existe o fue eliminado"
            )
    
    # Obtener orientaciones no borradas para el recinto
    orientations = db.query(Orientation).filter(
        Orientation.enclosure_id == enclosure_id,
        Orientation.is_deleted == False
    ).all()
    
    orientation_list = []
    for orient in orientations:
        # Copiar los atributos de la orientación en un diccionario y eliminar _sa_instance_state
        orient_data = orient.__dict__.copy()
        orient_data.pop("_sa_instance_state", None)
        # Renombrar "id" a "orientation_id"
        orient_data["orientation_id"] = orient_data.pop("id")
        
        # Obtener las divisiones no borradas para esta orientación
        divisions = db.query(Division).filter(
            Division.orientation_id == orient_data["orientation_id"],
            Division.is_deleted == False
        ).order_by(Division.num_orientation.asc()).all()
        
        division_list = []
        for div in divisions:
            div_data = div.__dict__.copy()
            div_data.pop("_sa_instance_state", None)
            # Renombrar "id" a "division_id"
            div_data["division_id"] = div_data.pop("id")
            division_list.append(div_data)
        
        orient_data["divisions"] = division_list
        orientation_list.append(orient_data)
    
    full_table = {
        "enclosure_id": enclosure_id,
        "orientations": orientation_list
    }
    return full_table



def delete_table(orientation_id: int, current_user: dict, db: Session):
    # Obtener la orientación que no esté marcada como eliminada
    my_orientation = db.query(Orientation).filter(
        Orientation.id == orientation_id,
        Orientation.is_deleted == False
    ).first()
    
    if not my_orientation:
        raise HTTPException(status_code=404, detail="Orientación no encontrada")
    
    # Obtener el enclosure_id asociado a la orientación
    enclosure_id = my_orientation.enclosure_id
    
    # Validar que el recinto esté vinculado a un proyecto
    project_id = db.query(EnclosureGenerals.project_id).filter(
        EnclosureGenerals.id == enclosure_id
    ).scalar()
    
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
    
    try:
        # Soft delete: marcar la orientación como eliminada
        my_orientation.is_deleted = True
        
        # También se marcan como eliminadas todas las divisiones asociadas a esta orientación
        divisions = db.query(Division).filter(
            Division.orientation_id == orientation_id,
            Division.is_deleted == False
        ).all()
        for division in divisions:
            division.is_deleted = True
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error al eliminar la orientación"
        )
    
    return {"message": "Orientación eliminada exitosamente (soft delete)"}