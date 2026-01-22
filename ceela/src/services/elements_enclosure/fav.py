from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from src.models.entity.fav import Fav
from src.models.schemas.elements_enclosure.fav_create import FavCreate
from src.models.entity.window import WindowEnclosure 
from src.models.entity.door import DoorEnclosure
from src.models.entity.project_table import Project
from src.models.entity.enclosure_general import EnclosureGenerals
from src.services.po.po_services import thermal_bridges_window

def create_fav_enclosure(
    type: str, 
    item_id: int, 
    enclosure_id: int, 
    fav_window: FavCreate, 
    current_user: dict, 
    db: Session
):
    # Validar que el tipo sea "window" o "door"
    if type not in ["window", "door"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Solo se permiten 'window' o 'door'.")

    # Buscar el enclosure asociado al item_id
    if type == "window":
        enclosure_relation = db.query(WindowEnclosure).filter(
            WindowEnclosure.id == item_id,
            WindowEnclosure.enclosure_id == enclosure_id
        ).first()
    else:  # type == "door"
        enclosure_relation = db.query(DoorEnclosure).filter(
            DoorEnclosure.id == item_id,
            DoorEnclosure.enclosure_id == enclosure_id
        ).first()

    if not enclosure_relation:
        raise HTTPException(status_code=404, detail=f"No se encontró un enclosure de {type} con el item_id especificado.")

    # Buscar el project_id a través de la tabla EnclosureGenerals
    enclosure_general = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.id == enclosure_id
    ).first()

    if not enclosure_general:
        raise HTTPException(status_code=404, detail="El enclosure no está asociado a un proyecto válido.")

    # Verificar que el proyecto pertenece al usuario actual
    project = db.query(Project).filter(
        Project.id == enclosure_general.project_id,
        Project.user_id == current_user["user_id"]
    ).first()

    if not project:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este proyecto o no existe.")

    # Verificar si ya existe un favorito con los mismos parámetros
    exist_fav = db.query(Fav).filter(
        Fav.item_id == item_id,
        Fav.type == type
    ).first()
    
    if exist_fav:
        raise HTTPException(status_code=400, detail="Este fav ya existe.")

    # Crear la instancia de Fav
    new_fav = Fav(**fav_window.model_dump(), item_id=item_id, type=type)

    try:
        # Agregar y confirmar la transacción en la base de datos
        db.add(new_fav)
        db.commit()
        db.refresh(new_fav)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar el favorito: {str(e)}")

    return new_fav


def get_favs_by_enclosure(enclosure_id: int, fav_type: str, current_user: dict, db: Session):
    """
    Retorna todos los favoritos asociados al enclosure_id indicado filtrados por fav_type,
    verificando que el enclosure pertenezca a un proyecto del usuario actual,
    salvo que el usuario sea administrador.
    """
    # Verificar que el enclosure exista y obtener el enclosure general
    enclosure_general = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.id == enclosure_id
    ).first()
    if not enclosure_general:
        raise HTTPException(status_code=404, detail="El enclosure no existe.")

    # Verificar que el proyecto asociado al enclosure pertenece al usuario actual,
    # a menos que el usuario sea administrador (role_id == 1)
    if current_user.get("role_id") != 1:
        project = db.query(Project).filter(
            Project.id == enclosure_general.project_id,
            Project.user_id == current_user["user_id"]
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes permiso para acceder a este enclosure.")

    # Según el tipo de favorito, realizar la consulta correspondiente
    if fav_type == "window":
        favs = db.query(Fav).join(
            WindowEnclosure, WindowEnclosure.id == Fav.item_id
        ).filter(
            Fav.type == "window",
            WindowEnclosure.enclosure_id == enclosure_id
        ).all()
    elif fav_type == "door":
        favs = db.query(Fav).join(
            DoorEnclosure, DoorEnclosure.id == Fav.item_id
        ).filter(
            Fav.type == "door",
            DoorEnclosure.enclosure_id == enclosure_id
        ).all()
    else:
        raise HTTPException(status_code=400, detail="Tipo de favorito inválido. Solo se permiten 'window' o 'door'.")

    return favs






# UPDATE: Actualizar un favorito usando flag_modified para campos JSON
def update_fav(fav_id: int, fav_type: str, fav_update: FavCreate, current_user: dict, db: Session):
    """
    Actualiza un favorito identificado por fav_id, utilizando flag_modified
    para notificar cambios en campos de tipo JSON. Se valida que el favorito esté
    relacionado a un enclosure que pertenezca al usuario actual y que el tipo
    proporcionado coincida con el del favorito.
    """
    # Validar que el tipo proporcionado sea correcto
    if fav_type not in ["window", "door"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Solo se permiten 'window' o 'door'.")
    
    fav = db.query(Fav).filter(Fav.id == fav_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Fav no encontrado.")

    # Verificar que el tipo del favorito en la BD coincide con el tipo recibido
    if fav.type != fav_type:
        raise HTTPException(status_code=400, detail="El tipo del fav no coincide con el tipo proporcionado.")

    # Obtener la relación con el enclosure según el tipo
    if fav_type == "window":
        enclosure_relation = db.query(WindowEnclosure).filter(
            WindowEnclosure.id == fav.item_id
        ).first()
    else:  # fav_type == "door"
        enclosure_relation = db.query(DoorEnclosure).filter(
            DoorEnclosure.id == fav.item_id
        ).first()

    if not enclosure_relation:
        raise HTTPException(status_code=404, detail="El enclosure relacionado no existe.")

    # Validar que el enclosure esté asociado a un proyecto del usuario actual
    enclosure_general = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.id == enclosure_relation.enclosure_id
    ).first()
    if not enclosure_general:
        raise HTTPException(status_code=404, detail="El enclosure no está asociado a un proyecto válido.")
    project = db.query(Project).filter(
        Project.id == enclosure_general.project_id,
        Project.user_id == current_user["user_id"]
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este fav.")

    # Actualizar los campos enviados en la request y notificar cambios en campos JSON
    update_data = fav_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(fav, key, value)
        flag_modified(fav, key)

    try:
        db.commit()
        db.refresh(fav)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el favorito: {str(e)}")

    return fav



def delete_fav(fav_id: int, fav_type: str, current_user: dict, db: Session):
    """
    Elimina un favorito identificado por fav_id, luego de validar que el
    enclosure asociado pertenezca a un proyecto del usuario actual y que
    el tipo proporcionado coincida con el del favorito.
    """
    if fav_type not in ["window", "door"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Solo se permiten 'window' o 'door'.")
    
    fav = db.query(Fav).filter(Fav.id == fav_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorito no encontrado.")

    # Verificar que el tipo del favorito coincide con el tipo proporcionado
    if fav.type != fav_type:
        raise HTTPException(status_code=400, detail="El tipo del favorito no coincide con el tipo proporcionado.")

    # Obtener la relación del enclosure según el tipo
    if fav_type == "window":
        enclosure_relation = db.query(WindowEnclosure).filter(
            WindowEnclosure.id == fav.item_id
        ).first()
    else:  # fav_type == "door"
        enclosure_relation = db.query(DoorEnclosure).filter(
            DoorEnclosure.id == fav.item_id
        ).first()

    if not enclosure_relation:
        raise HTTPException(status_code=404, detail="El enclosure relacionado no existe.")

    # Validar que el enclosure esté asociado a un proyecto del usuario actual
    enclosure_general = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.id == enclosure_relation.enclosure_id
    ).first()
    if not enclosure_general:
        raise HTTPException(status_code=404, detail="El enclosure no está asociado a un proyecto válido.")
    project = db.query(Project).filter(
        Project.id == enclosure_general.project_id,
        Project.user_id == current_user["user_id"]
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este favorito.")

    try:
        db.delete(fav)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar el favorito: {str(e)}")

    return {"detail": "Favorito eliminado correctamente."}