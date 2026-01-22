from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.schemas.elements_enclosure.floor import FloorEnclosureCreate  # Se asume que tiene: floor_id, characteristic, area, is_ventilated, etc.
from src.models.entity.floor import FloorEnclosure
from src.models.entity.detail_part import DetailPart
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.project_table import Project
from sqlalchemy.orm.attributes import flag_modified
from src.services.po.po_services import thermal_bridge_floor
from src.services.po.calculate_piso import calculate_termitancia_piso
from src.services.base.caso_base import create_caso_base
from src.services.base.create_base.base import create_obj_base, delete_obj_base, update_obj_base

def create_floor_enclosure(enclosure_id: int, floor: FloorEnclosureCreate, current_user: dict, db: Session):
    try:
        # Obtener el project_id a partir del enclosure_id
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure_id.")

        user_id = current_user["user_id"]
        # Verificar que el proyecto pertenezca al usuario actual
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id  
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No se encontró el proyecto o no tienes permisos para modificarlo.")

        # Validar el detail del piso usando floor.floor_id
        floor_detail = db.query(DetailPart).filter(
            DetailPart.id == floor.floor_id,
            DetailPart.project_id == project_id
        ).first()
        if not floor_detail:
            raise HTTPException(status_code=404, detail="El floor_id no pertenece al proyecto.")
        if floor_detail.type != "Piso":
            raise HTTPException(status_code=400, detail="El floor_id debe corresponder a un registro de tipo 'Piso'.")

        # Obtener el value_u del detail
        u = getattr(floor_detail, "value_u", None)

        # Determinar el valor de po6_l según la ventilación
        if floor.is_ventilated == "Ventilado":
            po6_l = floor.parameter  # Valor fijo; modifica según tu lógica de negocio
        else:
            po6_l = 0.0

        # Crear la instancia de FloorEnclosure con los valores calculados
        new_floor = FloorEnclosure(
            **floor.model_dump(),
            u=u,
            po6_l=po6_l,
            enclosure_id=enclosure_id
        )

        try:
            db.add(new_floor)
            db.commit()
            db.refresh(new_floor)
            my_floor = new_floor.model_dump()
            thermal_bridge_floor(floor=new_floor, db=db)
            calculate_termitancia_piso(new_floor, db)
            create_obj_base(enclosure_obj=new_floor, db=db)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=404, detail="Ocurrió un error al crear el piso en el recinto")
            
        return my_floor

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la creación del piso: {str(e)}")
    

def update_floor_enclosure(floor_id: int, floor_update: FloorEnclosureCreate, current_user: dict, db: Session):
    try:
        # Buscar el piso a actualizar
        floor = db.query(FloorEnclosure).filter(FloorEnclosure.id == floor_id).first()
        if not floor:
            raise HTTPException(status_code=404, detail="Piso no encontrado.")

        # Verificar permisos: obtener el project_id del enclosure asociado al piso
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == floor.enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al piso.")

        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar este piso.")

        # Obtener los campos a actualizar
        floor_data = floor_update.model_dump(exclude_unset=True)

        # Si se actualiza el floor_id, recalcular el value_u
        if "floor_id" in floor_data:
            new_detail = db.query(DetailPart).filter(
                DetailPart.id == floor_data["floor_id"],
                DetailPart.project_id == project_id
            ).first()
            if not new_detail:
                raise HTTPException(status_code=404, detail="El floor_id no pertenece al proyecto.")
            if new_detail.type != "Piso":
                raise HTTPException(status_code=400, detail="El floor_id debe corresponder a un registro de tipo 'Piso'.")
            floor.u = getattr(new_detail, "value_u", None)
            floor.floor_id = floor_data["floor_id"]

        # Si se actualiza la sección is_ventilated, recalcular po6_l
        if "is_ventilated" in floor_data:
            if floor_data["is_ventilated"] == "Ventilado":
                floor.po6_l = floor_update.parameter # Valor fijo; mofdsfdifica según tu lógica de negocio
            else:
                floor.po6_l = 0.0

            floor.is_ventilated = floor_data["is_ventilated"]
            
        # Actualizar otros campos
        for key, value in floor_data.items():
            if key not in ["floor_id", "is_ventilated"]:
                setattr(floor, key, value)
                
                
        flag_modified(floor, "is_ventilated")
        db.commit()
        db.refresh(floor)
        my_floor = floor.model_dump()
        thermal_bridge_floor(floor=floor, db=db)
        calculate_termitancia_piso(floor, db)
        update_obj_base(original_obj=floor, db=db)
        return my_floor

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el piso: {str(e)}")


def delete_floor_enclosure(floor_id: int, current_user: dict, db: Session):
    try:
        # Buscar el piso a eliminar
        floor = db.query(FloorEnclosure).filter(FloorEnclosure.id == floor_id).first()
        if not floor:
            raise HTTPException(status_code=404, detail="Piso no encontrado.")

        # Verificar permisos: obtener el project_id asociado al enclosure del piso
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == floor.enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al piso.")

        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este piso.")

        db.delete(floor)
        db.commit()
        delete_obj_base(original_obj=floor, db=db)
        return {"mensaje": "Piso eliminado exitosamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el piso: {str(e)}")
    
    
def get_floor_enclosures(enclosure_id: int, current_user: dict, db: Session, skip_permission_check: bool = False):
    try:
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

        # Obtener todos los pisos asociados al enclosure
        floors = db.query(FloorEnclosure).filter(
            FloorEnclosure.enclosure_id == enclosure_id
        ).all()

        floors_with_details = []
        for floor in floors:
            detail = db.query(DetailPart).filter(
                DetailPart.id == floor.floor_id,
                DetailPart.type == "Piso"
            ).first()
            floor_name = detail.name_detail if detail else None

            floors_with_details.append({
                **floor.model_dump(),
                "name": floor_name
            })

        return floors_with_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los pisos: {str(e)}")
