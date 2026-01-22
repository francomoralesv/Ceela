from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.schemas.elements_enclosure.window_enclosure_create import WindowEnclosureCreate
from src.models.entity.constant import Constant
from src.models.entity.window import WindowEnclosure
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.project_table import Project
from src.models.entity.detail_part import DetailPart
from src.models.entity.elements import Element
from src.models.schemas.elements_enclosure.fav_create import FavCreate
from src.services.elements_enclosure.fav import create_fav_enclosure
from src.services.po.po_services import thermal_bridges_window
from src.services.base.caso_base import create_caso_base
from src.services.base.create_base.base import create_obj_base, delete_obj_base, update_obj_base
from src.utils.logging import logger


def create_window_enclosures(enclosure_id: int, window: WindowEnclosureCreate, current_user: dict, db: Session):
    # Buscar el elemento de ventana en la tabla Element, validando que sea de tipo "window"
    window_element = db.query(Element).filter(
        Element.id == window.window_id,
        Element.type == "window"
    ).first()
    
    if not window_element:
        raise HTTPException(status_code=404, detail="El id proporcionado no corresponde a una ventana.")
    
    # Obtener los atributos necesarios de window_element
    clousure_type = window_element.atributs.get("clousure_type")
    frame_type = window_element.atributs.get("frame_type")
    
    # Obtener el nombre de la ventana desde el elemento
    window_name = window_element.name_element
    
    window_angulo_azimut = window.angulo_azimut

    # Obtener la tabla de ángulos de azimut
    angulos_azimut = db.query(Constant).filter(
        Constant.type == "orientation",
        Constant.name == "Azimut Table"
    ).first()

    if not angulos_azimut:
        raise HTTPException(status_code=404, detail="No se encontró la tabla de azimut en la base de datos.")
    
    # Buscar la orientación en la tabla
    orientation = None
    for angulo in angulos_azimut.atributs["orientations"]:
        if angulo["range_az"] == window_angulo_azimut:
            orientation = angulo["orientation"]
            break

    if orientation is None:
        raise HTTPException(status_code=400, detail="Ángulo de azimut no encontrado en la tabla de orientación.")
    
    # Obtener el project_id a partir del enclosure_id
    project_id = db.query(EnclosureGenerals.project_id).filter(
        EnclosureGenerals.id == enclosure_id
    ).scalar()

    if not project_id:
        raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure_id.")

    user_id = current_user["user_id"] 

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id  
    ).first()

    if not project:
        raise HTTPException(status_code=403, detail="No se encontró el proyecto o no tienes permisos para modificarlo.")
    
    # Validar que el detail_part (house_in) pertenezca al proyecto
    detail_part = db.query(DetailPart).filter(DetailPart.id == window.housed_in).first()
    if not detail_part or detail_part.project_id != project_id:
        raise HTTPException(status_code=403, detail="El id de details_part no pertenece al proyecto.")
    
    # Crear la ventana en el enclosure
    new_window_enclosure = WindowEnclosure(
        **window.model_dump(), 
        clousure_type=clousure_type,
        frame=frame_type,
        orientation=orientation,
        enclosure_id=enclosure_id
    )
    
    db.add(new_window_enclosure)
    db.commit()
    db.refresh(new_window_enclosure)
    
    
    my_window = new_window_enclosure.model_dump()
    
    # Crear los datos de "fav" con valores por defecto (todos en 0)
    default_fav_data = {
        "fav1": {"d": 0, "l": 0},
        "fav2_izq": {"p": 0, "s": 0},
        "fav2_der": {"p": 0, "s": 0},
        "fav3": {"e": 0, "t": 0, "beta": 0, "alfa": 0}
    }
    
    # Se asume que FavCreate acepta este diccionario para inicializarse
    fav_create = FavCreate(**default_fav_data)
    
    # Llamar a la función para crear el "fav" correspondiente a la ventana creada
    new_fav = create_fav_enclosure(
        type="window",
        item_id=new_window_enclosure.id,
        enclosure_id=enclosure_id,
        fav_window=fav_create,
        current_user=current_user,
        db=db
    )
    thermal_bridges_window(window=new_window_enclosure, db=db)
    create_obj_base(enclosure_obj=new_window_enclosure, db=db)
    # Retornar un diccionario con la información de la ventana, el "fav" y el nombre de la ventana
    return {
        **my_window,
        "fav": new_fav,
        "window_name": window_name
    }
    
    

def update_window_enclosure(window_enclosure_id: int, window: WindowEnclosureCreate, current_user: dict, db: Session):
    try:
        # Buscar la ventana enclosure a actualizar
        existing_window_enclosure = db.query(WindowEnclosure).filter(
            WindowEnclosure.id == window_enclosure_id
        ).first()
        if not existing_window_enclosure:
            raise HTTPException(status_code=404, detail="No se encontró la ventana enclosure a actualizar.")

        # Obtener el enclosure_id a partir del registro existente y validar el proyecto asociado
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == existing_window_enclosure.enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure de la ventana.")

        # Verificar permisos del usuario
        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No se encontró el proyecto o no tienes permisos para modificarlo.")

        # Validar que el housed_in (id de DetailPart) pertenezca al proyecto
        detail_part = db.query(DetailPart).filter(
            DetailPart.id == window.housed_in
        ).first()
        if not detail_part or detail_part.project_id != project_id:
            raise HTTPException(status_code=403, detail="El id de details_part no pertenece al proyecto.")

        # Validar que el id de la ventana corresponde a un elemento de tipo "window"
        window_element = db.query(Element).filter(
            Element.id == window.window_id,
            Element.type == "window"
        ).first()
        if not window_element:
            raise HTTPException(status_code=404, detail="El id proporcionado no corresponde a una ventana.")

        # Extraer valores desde el JSON de atributos
        clousure_type = window_element.atributs.get("clousure_type")
        frame_type = window_element.atributs.get("frame_type")

        # Calcular la nueva orientación si se envía un nuevo ángulo de azimut
        angulos_azimut = db.query(Constant).filter(
            Constant.type == "orientation",
            Constant.name == "Azimut Table"
        ).first()
        if not angulos_azimut:
            raise HTTPException(status_code=404, detail="No se encontró la tabla de azimut en la base de datos.")
        
        new_orientation = None
        for angulo in angulos_azimut.atributs["orientations"]:
            if angulo["range_az"] == window.angulo_azimut:
                new_orientation = angulo["orientation"]
                break

        if new_orientation is None:
            raise HTTPException(status_code=400, detail="Ángulo de azimut no encontrado en la tabla de orientación.")

        # Actualizar los campos enviados del schema (solo los que se han enviado)
        window_data = window.model_dump(exclude_unset=True)
        for key, value in window_data.items():
            if key == "angulo_azimut":
                setattr(existing_window_enclosure, "angulo_azimut", value)
                setattr(existing_window_enclosure, "orientation", new_orientation)
            else:
                setattr(existing_window_enclosure, key, value)

        # Actualizar los campos adicionales fijos
        existing_window_enclosure.clousure_type = clousure_type
        existing_window_enclosure.frame = frame_type
        # No se modifica el enclosure_id en update

        db.commit()
        db.refresh(existing_window_enclosure)
        my_window = existing_window_enclosure.model_dump()
        thermal_bridges_window(window=existing_window_enclosure, db=db)
        update_obj_base(original_obj=existing_window_enclosure, db=db)
        
        return my_window

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar la ventana enclosure: {str(e)}")


def delete_window_enclosure(window_enclosure_id: int, current_user: dict, db: Session):
    try:
        # Buscar la ventana enclosure a eliminar
        window_enclosure = db.query(WindowEnclosure).filter(
            WindowEnclosure.id == window_enclosure_id
        ).first()
        if not window_enclosure:
            raise HTTPException(status_code=404, detail="No se encontró la ventana enclosure a eliminar.")

        # Obtener el enclosure_id a partir del registro y validar el proyecto asociado
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == window_enclosure.enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure de la ventana.")

        # Verificar permisos del usuario
        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No se encontró el proyecto o no tienes permisos para modificarlo.")

        db.delete(window_enclosure)
        db.commit()
        delete_obj_base(original_obj=window_enclosure, db=db)

        return {"detail": "Ventana enclosure eliminada exitosamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar la ventana enclosure: {str(e)}")


def get_window_enclosures(enclosure_id: int, current_user: dict, db: Session, skip_permission_check: bool = False):
    try:
        logger.info(f"Obteniendo ventanas de enclosure_id: {enclosure_id}")
        # Obtener el project_id asociado al enclosure_id
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure_id.")

        # Verificar permisos: si el usuario no es admin, el proyecto debe pertenecer al usuario actual
        if not skip_permission_check and current_user.get("role_id") != 1:
            user_id = current_user["user_id"]
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            if not project:
                raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este proyecto.")

        # Obtener todas las ventanas asociadas al enclosure
        windows = db.query(WindowEnclosure).filter(
            WindowEnclosure.enclosure_id == enclosure_id
        ).all()

        result = []
        for window in windows:
            window_data = window.model_dump()  # Serializa el objeto según corresponda
            window_element = db.query(Element).filter(
                Element.id == window_data.get("window_id"),
                Element.type == "window"
            ).first()
            housed_in = db.query(DetailPart.name_detail).filter(
                DetailPart.id == window.housed_in
            ).scalar()

            if window_element:
                window_data["window_name"] = window_element.name_element
            else:
                window_data["window_name"] = None

            window_data["alojado_en"] = housed_in
            result.append(window_data)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las ventanas enclosure: {str(e)}")
