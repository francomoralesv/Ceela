from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.entity.tabla_py import TablaPy
from src.models.schemas.elements_enclosure.wall_enclosure_create import WallEnclosureCreate
from src.models.entity.wall import WallEnclosure
from src.models.entity.constant import Constant
from src.models.entity.detail_part import DetailPart
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.project_table import Project
from src.models.entity.detail_part import DetailPart
from src.models.entity.thermal_bridges import ThermalBridgeWall
from src.services.po.po_services import thermal_bridges_wall
from src.services.base.caso_base import create_caso_base
from src.services.base.create_base.base import create_obj_base, delete_obj_base, update_obj_base
from src.utils.validation.wall_validation import validate_wall_orientation_characteristics


def create_wall_enclosure(enclosure_id: int, wall: WallEnclosureCreate, current_user: dict, db: Session):
    try:
        wall_angulo_azimut = wall.angulo_azimut

        angulos_azimut = db.query(Constant).filter(
            Constant.type == "orientation",
            Constant.name == "Azimut Table"
        ).first()

        if not angulos_azimut:
            raise HTTPException(status_code=404, detail="No se encontró la tabla de azimut en la base de datos.")

        orientation = None
        for angulo in angulos_azimut.atributs["orientations"]:
            if angulo["range_az"] == wall_angulo_azimut:
                orientation = angulo["orientation"]
                break

        if orientation is None:
            raise HTTPException(status_code=400, detail="Ángulo de azimut no encontrado en la tabla de orientación.")

        validate_wall_orientation_characteristics(orientation, wall.characteristics)

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

        wall_detail = db.query(DetailPart).filter(
            DetailPart.id == wall.wall_id,
            DetailPart.project_id == project_id
        ).first()

        if not wall_detail:
            raise HTTPException(status_code=404, detail="El wall_id no pertenece al proyecto.")

        if wall_detail.type != "Muro":
            raise HTTPException(status_code=400, detail="El wall_id debe corresponder a un registro de tipo 'muro'.")

        u = getattr(wall_detail, "value_u", None)

        # Creación del muro
        real_wall = WallEnclosure(
            **wall.model_dump(),  
            orientation=orientation,
            u=u,
            enclosure_id=enclosure_id
        )

        try:
            
            db.add(real_wall)
            db.commit()
            db.refresh(real_wall)
            my_wall = real_wall.model_dump()
            
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail="Ocurrió un error al crear muro en el recinto"
            )
        
        # Creación automática del puente térmico asociado, inicializando los campos de thermalbridge en 0
        try:
            thermal_bridge = ThermalBridgeWall(
                po1_length=0,
                po1_id_element=0,
                po2_length=0,
                po2_id_element=0,
                po3_length=0,
                po3_id_element=0,
                po4_length=0,
                po4_e_aislacion=0,
                po4_id_element=0,
                wall_id=real_wall.id,
                enclosure_id=enclosure_id
            )
            db.add(thermal_bridge)
            db.commit()
            db.refresh(thermal_bridge)
            thermal_bridges_wall(wall=real_wall, db=db)
            create_obj_base(enclosure_obj=real_wall, db=db)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail="Ocurrió un error al crear el puente térmico asociado al muro"
            )

        return my_wall

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error en la creación del muro: {str(e)}")

    
    
    
def get_wall_enclosures(enclosure_id: int, current_user: dict, db: Session, skip_permission_check: bool = False):
    try:
        # Obtenemos el project_id asociado al enclosure_id
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == enclosure_id
        ).scalar()

        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure_id.")

        # Si el usuario no es admin, se valida que sea el propietario del proyecto
        if not skip_permission_check and current_user.get("role_id") != 1:
            user_id = current_user["user_id"]
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()

            if not project:
                raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este proyecto.")

        # Se obtienen todos los wall enclosures que pertenezcan a ese enclosure
        walls = db.query(WallEnclosure).filter(
            WallEnclosure.enclosure_id == enclosure_id
        ).all()

        # Para cada wall, se consulta en la tabla DetailPart el nombre asociado usando el wall.wall_id
        walls_with_details = []
        for wall in walls:
            detail = db.query(DetailPart).filter(
                DetailPart.id == wall.wall_id
            ).first()
            wall_name = detail.name_detail if detail else None

            walls_with_details.append({
                **wall.model_dump(),  # Se incluye el objeto wall completo, según convenga
                "name": wall_name
            })

        return walls_with_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los muros: {str(e)}")




def update_wall_enclosure(wall_id: int, wall_update: WallEnclosureCreate, current_user: dict, db: Session):
    try:
        # Buscamos el muro a actualizar
        wall = db.query(WallEnclosure).filter(WallEnclosure.id == wall_id).first()
        if not wall:
            raise HTTPException(status_code=404, detail="Muro no encontrado.")

        # Verificar permisos: obtenemos el project_id del enclosure asociado al muro
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == wall.enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al muro.")

        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar este muro.")

        # Se obtienen los campos a actualizar
        wall_data = wall_update.model_dump(exclude_unset=True)
        area_updated = False
        # Recorrer cada campo para actualizar
        for key, value in wall_data.items():
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

                validate_wall_orientation_characteristics(new_orientation, wall.characteristics)

                setattr(wall, "angulo_azimut", value)
                setattr(wall, "orientation", new_orientation)

            elif key == "wall_id":
                wall_detail = db.query(DetailPart).filter(
                    DetailPart.id == value,
                    DetailPart.project_id == project_id
                ).first()
                if not wall_detail:
                    raise HTTPException(status_code=404, detail="El wall_id no pertenece al proyecto.")
                if wall_detail.type != "Muro":
                    raise HTTPException(status_code=400, detail="El wall_id debe corresponder a un registro de tipo 'muro'.")
                u = getattr(wall_detail, "value_u", None)
                setattr(wall, "wall_id", value)
                setattr(wall, "u", u)

            elif key == "area":
                area_updated = True
                setattr(wall, "area", value)

            elif key == "u":
                setattr(wall, "u", value)

            elif key == "characteristics":
                validate_wall_orientation_characteristics(wall.orientation, value)
                setattr(wall, key, value)

            else:
                setattr(wall, key, value)

        if area_updated:
            wall_detail = db.query(DetailPart).filter(
                DetailPart.id == wall.wall_id,
                DetailPart.project_id == project_id
            ).first()
            if wall_detail and wall_detail.type == "Muro":
                u = getattr(wall_detail, "value_u", None)
                setattr(wall, "u", u)

        db.commit()
        db.refresh(wall)
        my_wall = wall.model_dump()
        thermal_bridges_wall(wall=wall, db=db)
        update_obj_base(original_obj=wall, db=db)
        return my_wall

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el muro: {str(e)}")

    
    
def delete_wall_enclosure(wall_id: int, current_user: dict, db: Session):
    try:
        # Buscamos el muro a eliminar
        wall = db.query(WallEnclosure).filter(WallEnclosure.id == wall_id).first()
        if not wall:
            raise HTTPException(status_code=404, detail="Muro no encontrado.")

        # Verificar permisos: consultar el project_id asociado al enclosure del muro
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == wall.enclosure_id
        ).scalar()

        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al muro.")

        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este muro.")

        db.delete(wall)
        # Eliminar también el registro asociado en la tabla ThermalBridgeWall
        delete_obj_base(original_obj=wall, db=db)
        db.query(ThermalBridgeWall).filter(ThermalBridgeWall.wall_id == wall_id).delete()
        db.query(TablaPy).filter(TablaPy.item_id == wall_id).delete()
        db.commit()


        return {"mensaje": "Muro eliminado exitosamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el muro: {str(e)}")
