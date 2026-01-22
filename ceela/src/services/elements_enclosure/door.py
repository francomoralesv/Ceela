from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.schemas.elements_enclosure.window_enclosure_create import WindowEnclosureCreate
from src.models.schemas.elements_enclosure.door import DoorEnclosureCreate
from src.models.entity.constant import Constant
from src.models.entity.door import DoorEnclosure
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.project_table import Project
from src.models.entity.elements import Element
# Se asume que FavCreate y create_fav_enclosure están definidos e importados correctamente:
from src.models.schemas.elements_enclosure.fav_create import FavCreate
from src.services.elements_enclosure.fav import create_fav_enclosure
from src.services.tablas_py.tablas_py import calculate_tablas_py
from src.services.base.caso_base import create_caso_base
from src.services.base.create_base.base import create_obj_base, delete_obj_base, update_obj_base

def create_door_enclosure(enclosure_id: int, door: DoorEnclosureCreate, current_user: dict, db: Session):
    # Verificar que la puerta exista en la tabla Element con type "door"
    door_element = db.query(Element).filter(
        Element.id == door.door_id,
        Element.type == "door"
    ).first()
    
    if not door_element:
        raise HTTPException(status_code=404, detail="El id proporcionado no corresponde a una puerta.")
    
    # Obtener el nombre de la puerta desde el elemento
    door_name = door_element.name_element

    # Obtener el ángulo de azimut proveniente del objeto door
    door_angulo_azimut = door.angulo_azimut

    # Consultar la tabla de constantes para obtener la tabla de orientaciones
    angulos_azimut = db.query(Constant).filter(
        Constant.type == "orientation",
        Constant.name == "Azimut Table"
    ).first()

    if not angulos_azimut:
        raise HTTPException(status_code=404, detail="No se encontró la tabla de azimut en la base de datos.")

    # Buscar la orientación correspondiente al ángulo de azimut suministrado
    orientation = None
    for angulo in angulos_azimut.atributs["orientations"]:
        if angulo["range_az"] == door_angulo_azimut:
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

    # Validar que el proyecto pertenezca al usuario actual
    user_id = current_user["user_id"]
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id  
    ).first()

    if not project:
        raise HTTPException(status_code=403, detail="No se encontró el proyecto o no tienes permisos para modificarlo.")

    # Crear el nuevo door enclosure, añadiendo la orientación y el enclosure_id
    new_door_enclosure = DoorEnclosure(
        **door.model_dump(),
        orientation=orientation,
        enclosure_id=enclosure_id
    )

    db.add(new_door_enclosure)
    db.commit()
    db.refresh(new_door_enclosure)
    create_obj_base(enclosure_obj=new_door_enclosure, db=db)
    my_door = new_door_enclosure.model_dump()

    # Crear los datos de "fav" con valores por defecto (todos en 0)
    default_fav_data = {
        "fav1": {"d": 0, "l": 0},
        "fav2_izq": {"p": 0, "s": 0},
        "fav2_der": {"p": 0, "s": 0},
        "fav3": {"e": 0, "t": 0, "beta": 0, "alfa": 0}
    }
    
    # Se asume que FavCreate acepta este diccionario para inicializarse
    fav_create = FavCreate(**default_fav_data)
    
    # Llamar a la función para crear el registro en la tabla fav.
    # Se especifica el tipo "door" y se asocia el nuevo door enclosure mediante su id.
    new_fav = create_fav_enclosure(
        type="door",
        item_id=new_door_enclosure.id,
        enclosure_id=enclosure_id,
        fav_window=fav_create,
        current_user=current_user,
        db=db
    )
    calculate_tablas_py("door", new_door_enclosure.id, enclosure_id, db)
    # Retornar un diccionario con los datos del door enclosure, el registro fav y el nombre de la puerta
    return {
        **my_door,
        "fav": new_fav,
        "door_name": door_name
    }



def get_door_enclosures(enclosure_id: int, current_user: dict, db: Session):
    try:
        # Obtenemos el project_id asociado al enclosure_id
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == enclosure_id
        ).scalar()

        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure_id.")

        # Verificar permisos: si el usuario no es admin, el proyecto debe pertenecer al usuario actual
        if current_user.get("role_id") != 1:
            user_id = current_user["user_id"]
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()

            if not project:
                raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este proyecto.")

        # Se obtienen todos los door enclosures que pertenezcan a ese enclosure
        doors = db.query(DoorEnclosure).filter(
            DoorEnclosure.enclosure_id == enclosure_id
        ).all()

        return doors

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las puertas: {str(e)}")



def update_door_enclosure(door_id: int, door_update: DoorEnclosureCreate, current_user: dict, db: Session):
    try:
        # Buscamos el door enclosure a actualizar
        door_enclosure = db.query(DoorEnclosure).filter(
            DoorEnclosure.id == door_id
        ).first()

        if not door_enclosure:
            raise HTTPException(status_code=404, detail="Door enclosure no encontrado.")

        # Validar permisos: se obtiene el project_id a partir del enclosure_id asociado al door enclosure
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == door_enclosure.enclosure_id
        ).scalar()

        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al door enclosure.")

        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()

        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar este door enclosure.")

        # Obtener los campos a actualizar
        door_data = door_update.model_dump(exclude_unset=True)
        
        for key, value in door_data.items():
            # Si se envía un nuevo angulo_azimut, se recalcula la orientation
            if key == "angulo_azimut":
                angulos_azimut = db.query(Constant).filter(
                    Constant.type == "orientation",
                    Constant.name == "Azimut Table"
                ).first()
                if not angulos_azimut:
                    raise HTTPException(status_code=404, detail="No se encontró la tabla de azimut en la base de datos.")
                new_orientation = None
                for angulo in angulos_azimut.atributs["orientations"]:
                    if angulo["range_az"] == value:
                        new_orientation = angulo["orientation"]
                        break
                if new_orientation is None:
                    raise HTTPException(status_code=400, detail="Ángulo de azimut no encontrado en la tabla de orientación.")
                setattr(door_enclosure, "angulo_azimut", value)
                setattr(door_enclosure, "orientation", new_orientation)
            else:
                setattr(door_enclosure, key, value)

        db.commit()
        db.refresh(door_enclosure)
        my_door = door_enclosure.model_dump()
        calculate_tablas_py("door", door_enclosure.id, door_enclosure.enclosure_id, db)
        update_obj_base(original_obj=door_enclosure, db=db)
        return my_door

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar la puerta: {str(e)}")


def delete_door_enclosure(door_id: int, current_user: dict, db: Session):
    try:
        # Buscamos el door enclosure a eliminar
        door_enclosure = db.query(DoorEnclosure).filter(
            DoorEnclosure.id == door_id
        ).first()

        if not door_enclosure:
            raise HTTPException(status_code=404, detail="Door enclosure no encontrado.")

        # Validar permisos: obtenemos el project_id a partir del enclosure asociado al door enclosure
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == door_enclosure.enclosure_id
        ).scalar()

        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al door enclosure.")

        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()

        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este door enclosure.")

        db.delete(door_enclosure)
        db.commit() 
        delete_obj_base(original_obj=door_enclosure, db=db)

        return {"mensaje": "Door enclosure eliminado exitosamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar la puerta: {str(e)}")


