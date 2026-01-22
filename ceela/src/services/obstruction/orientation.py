from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.entity.project_table import Project
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.schemas.obstruction.obstruction import OrientationCreate
from src.models.entity.obstruction import Orientation
from src.models.entity.constant import Constant


def create_orientation(enclosure_id: int, orientation_data: OrientationCreate, current_user: dict, db: Session):
    # Validar que el recinto esté vinculado a un proyecto
    project_id = db.query(EnclosureGenerals.project_id).filter(
        EnclosureGenerals.id == enclosure_id    
    ).scalar()
    
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
    
    # Obtener la tabla de constantes de azimut
    azimut_constant = db.query(Constant).filter(
        Constant.type == "orientation",
        Constant.name == "Azimut Table"
    ).first()
    
    if not azimut_constant:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la tabla de azimut en la base de datos."
        )
    
    # Supongamos que en orientation_data viene el ángulo del muro (wall_angulo_azimut)
    wall_angulo_azimut = orientation_data.azimut
    orientation_value = None
    # Se asume que en la constante se encuentra un diccionario en el atributo "atributs"
    # con una clave "orientations" que es una lista de diccionarios, cada uno con "range_az" y "orientation"
    for angulo in azimut_constant.atributs["orientations"]:
        if angulo["range_az"] == wall_angulo_azimut:
            orientation_value = angulo["orientation"]
            break

    if orientation_value is None:
        raise HTTPException(
            status_code=400,
            detail="Ángulo de azimut no encontrado en la tabla de orientación."
        )
    
    # Se crea el objeto Orientation. Se añade el enclosure_id y se asigna el valor obtenido al atributo "orientation"
    my_orientation = Orientation(
        **orientation_data.model_dump(),
        enclosure_id=enclosure_id,
        orientation=orientation_value  # Asumiendo que Orientation tiene un campo "orientation"
    )
    
    try:
        db.add(my_orientation)
        db.commit()
        db.refresh(my_orientation)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error al crear orientación"
        )
        
    return my_orientation



def update_orientation(orientation_id: int, orientation_data: OrientationCreate, current_user: dict, db: Session):
    # Obtener la orientación (solo no borrada)
    my_orientation = db.query(Orientation).filter(
        Orientation.id == orientation_id,
        Orientation.is_deleted == False
    ).first()
    
    if not my_orientation:
        raise HTTPException(status_code=404, detail="Orientación no encontrada")
    
    # Validar la relación: obtener el enclosure_id a partir de la orientación
    enclosure_id = my_orientation.enclosure_id
    
    # Obtener project_id desde EnclosureGenerals usando el enclosure_id
    project_id = db.query(EnclosureGenerals.project_id).filter(
        EnclosureGenerals.id == enclosure_id
    ).scalar()
    
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
    
    # Si en el payload se envía un nuevo wall_angulo_azimut, actualizar el campo orientation
    if orientation_data.azimut is not None:
        new_wall_angulo_azimut = orientation_data.azimut
        azimut_constant = db.query(Constant).filter(
            Constant.type == "orientation",
            Constant.name == "Azimut Table"
        ).first()
    
        if not azimut_constant:
            raise HTTPException(
                status_code=404,
                detail="No se encontró la tabla de azimut en la base de datos."
            )
    
        new_orientation_value = None
        for angulo in azimut_constant.atributs["orientations"]:
            if angulo["range_az"] == new_wall_angulo_azimut:
                new_orientation_value = angulo["orientation"]
                break
    
        if new_orientation_value is None:
            raise HTTPException(
                status_code=400,
                detail="Ángulo de azimut no encontrado en la tabla de orientación."
            )
    
        # Actualizamos el valor del campo "orientation" en el registro
        my_orientation.orientation = new_orientation_value
    
    # Actualizamos otros campos enviados (excluyendo aquellos que no se envían)
    update_data = orientation_data.model_dump(exclude_unset=True)
    # Removemos el campo wall_angulo_azimut para evitar sobrescribir el valor ya calculado
    update_data.pop("wall_angulo_azimut", None)
    for key, value in update_data.items():
        setattr(my_orientation, key, value)
    
    try:
        db.commit()
        db.refresh(my_orientation)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error al actualizar la orientación"
        )
    
    return my_orientation


def get_orientation(orientation_id: int, current_user: dict, db: Session):
    my_orientation = db.query(Orientation).filter(
        Orientation.id == orientation_id,
        Orientation.is_deleted == False
    ).first()
    
    if not my_orientation:
        raise HTTPException(status_code=404, detail="Orientación no encontrada")
    
    # Validar relación: usar enclosure_id para obtener project_id
    enclosure_id = my_orientation.enclosure_id
    project_id = db.query(EnclosureGenerals.project_id).filter(
        EnclosureGenerals.id == enclosure_id
    ).scalar()
    
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
    
    return my_orientation



def delete_orientation(orientation_id: int, current_user: dict, db: Session):
    my_orientation = db.query(Orientation).filter(
        Orientation.id == orientation_id,
        Orientation.is_deleted == False
    ).first()
    
    if not my_orientation:
        raise HTTPException(status_code=404, detail="Orientación no encontrada")
    
    # Validar relación: obtener enclosure_id y project_id
    enclosure_id = my_orientation.enclosure_id
    project_id = db.query(EnclosureGenerals.project_id).filter(
        EnclosureGenerals.id == enclosure_id
    ).scalar()
    
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
    
    try:
        # Soft delete: marcar la orientación como eliminada
        my_orientation.is_deleted = True
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=403,
            detail="Error al eliminar la orientación"
        )
    
    return {"message": "Orientación eliminada exitosamente"}
