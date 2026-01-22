from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.entity.thermal_bridges import ThermalBridgeWall
from src.models.entity.wall import WallEnclosure
from src.models.schemas.thermal_bridges.thermal_bridges_create import ThermalBridgeWallCreate
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.project_table import Project
from src.models.entity.detail_part import DetailPart
from src.services.po.po_services import thermal_bridges_wall
from src.services.base.caso_base import create_caso_base

def create_thermal_bridge_wall(enclosure_id: int, bridge_wall: ThermalBridgeWallCreate, current_user: dict, db: Session):
    try:
        # 1. Obtener el project_id a partir del enclosure_id
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure_id.")

        # 2. Verificar que el proyecto pertenezca al usuario actual
        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar este proyecto.")

        # 3. Validar cada id_element (aceptando None o 0)
        if bridge_wall.po1_id_element is not None and bridge_wall.po1_id_element != 0:
            detail = db.query(DetailPart).filter(
                DetailPart.id == bridge_wall.po1_id_element,
                DetailPart.project_id == project_id
            ).first()
            if not detail:
                raise HTTPException(status_code=400, detail="El po1_id_element no pertenece al proyecto actual.")

        if bridge_wall.po2_id_element is not None and bridge_wall.po2_id_element != 0:
            detail = db.query(DetailPart).filter(
                DetailPart.id == bridge_wall.po2_id_element,
                DetailPart.project_id == project_id
            ).first()
            if not detail:
                raise HTTPException(status_code=400, detail="El po2_id_element no pertenece al proyecto actual.")

        if bridge_wall.po3_id_element is not None and bridge_wall.po3_id_element != 0:
            detail = db.query(DetailPart).filter(
                DetailPart.id == bridge_wall.po3_id_element,
                DetailPart.project_id == project_id
            ).first()
            if not detail:
                raise HTTPException(status_code=400, detail="El po3_id_element no pertenece al proyecto actual.")

        if bridge_wall.po4_id_element is not None and bridge_wall.po4_id_element != 0:
            detail = db.query(DetailPart).filter(
                DetailPart.id == bridge_wall.po4_id_element,
                DetailPart.project_id == project_id
            ).first()
            if not detail:
                raise HTTPException(status_code=400, detail="El po4_id_element no pertenece al proyecto actual.")

        # 4. Crear el registro de ThermalBridgeWall (se asume que el modelo incluye un campo 'enclosure_id')
        new_bridge = ThermalBridgeWall(
            **bridge_wall.model_dump(),
            enclosure_id=enclosure_id
        )

        real_wall = db.query(WallEnclosure).filter_(
            WallEnclosure.id == new_bridge.wall_id
        )
        
        db.add(new_bridge)
        db.commit()
        db.refresh(new_bridge)
        
        return new_bridge

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el ThermalBridgeWall: {str(e)}")




def get_thermal_bridge_walls(enclosure_id: int, current_user: dict, db: Session):
    try:
        # 1. Obtener el project_id a partir del enclosure_id
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure_id.")

        # 2. Verificar que el usuario tenga acceso al proyecto, a menos que sea administrador (role_id == 1)
        if current_user.get("role_id") != 1:
            user_id = current_user["user_id"]
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            if not project:
                raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este proyecto.")

        # 3. Obtener los registros ThermalBridgeWall asociados al enclosure_id
        walls = db.query(ThermalBridgeWall).filter(
            ThermalBridgeWall.enclosure_id == enclosure_id
        ).all()

        # 4. Construir la respuesta incluyendo el nombre de cada elemento de cada po
        walls_response = []
        for wall in walls:
            # Convertir el objeto en diccionario y eliminar la clave interna de SQLAlchemy
            wall_dict = wall.__dict__.copy()
            wall_dict.pop("_sa_instance_state", None)

            # Iterar dinámicamente sobre los campos po1, po2, po3, po4
            for i in range(1, 5):
                id_key = f"po{i}_id_element"
                name_key = f"po{i}_element_name"
                po_id = getattr(wall, id_key, 0)
                if po_id and po_id != 0:
                    detail = db.query(DetailPart).filter(
                        DetailPart.id == po_id
                    ).first()
                    wall_dict[name_key] = detail.name_detail if detail else None
                else:
                    wall_dict[name_key] = None

            walls_response.append(wall_dict)

        return walls_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ThermalBridgeWall: {str(e)}")




# fdsf
def update_thermal_bridge_wall(wall_id: int, wall_update: ThermalBridgeWallCreate, current_user: dict, db: Session):
    try:
        # 1. Buscar el registro a actualizar
        wall_record = db.query(ThermalBridgeWall).filter(ThermalBridgeWall.id == wall_id).first()
        if not wall_record:
            raise HTTPException(status_code=404, detail="ThermalBridgeWall no encontrado.")

        # 2. Obtener el project_id a partir del enclosure_id del registro
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == wall_record.enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al enclosure_id.")

        # 3. Verificar permisos del usuario
        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar este ThermalBridgeWall.")

        # 4. Validar los id_element que se quieran actualizar
        wall_data = wall_update.model_dump(exclude_unset=True)
        
        if "po1_id_element" in wall_data and wall_data["po1_id_element"] is not None and wall_data["po1_id_element"] != 0:
            detail = db.query(DetailPart).filter(
                DetailPart.id == wall_data["po1_id_element"],
                DetailPart.project_id == project_id
            ).first()
            if not detail:
                raise HTTPException(status_code=400, detail="El po1_id_element no pertenece al proyecto actual.")

        if "po2_id_element" in wall_data and wall_data["po2_id_element"] is not None and wall_data["po2_id_element"] != 0:
            detail = db.query(DetailPart).filter(
                DetailPart.id == wall_data["po2_id_element"],
                DetailPart.project_id == project_id
            ).first()
            if not detail:
                raise HTTPException(status_code=400, detail="El po2_id_element no pertenece al proyecto actual.")

        if "po3_id_element" in wall_data and wall_data["po3_id_element"] is not None and wall_data["po3_id_element"] != 0:
            detail = db.query(DetailPart).filter(
                DetailPart.id == wall_data["po3_id_element"],
                DetailPart.project_id == project_id
            ).first()
            if not detail:
                raise HTTPException(status_code=400, detail="El po3_id_element no pertenece al proyecto actual.")

        if "po4_id_element" in wall_data and wall_data["po4_id_element"] is not None and wall_data["po4_id_element"] != 0:
            detail = db.query(DetailPart).filter(
                DetailPart.id == wall_data["po4_id_element"],
                DetailPart.project_id == project_id
            ).first()
            if not detail:
                raise HTTPException(status_code=400, detail="El po4_id_element no pertenece al proyecto actual.")

        # 5. Actualizar los campos del registro
        for key, value in wall_data.items():
            setattr(wall_record, key, value)
        
        db.commit()
        db.refresh(wall_record)
        my_wall_record = wall_record.model_dump()
        
        wall = db.query(WallEnclosure).filter(WallEnclosure.id == wall_record.wall_id).first()
        thermal_bridges_wall(wall=wall, db=db)
        create_caso_base(wall, db)
        return my_wall_record

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar ThermalBridgeWall: {str(e)}")



def delete_thermal_bridge_wall(wall_id: int, current_user: dict, db: Session):
    try:
        # 1. Buscar el registro a eliminar
        wall_record = db.query(ThermalBridgeWall).filter(ThermalBridgeWall.id == wall_id).first()
        if not wall_record:
            raise HTTPException(status_code=404, detail="ThermalBridgeWall no encontrado.")

        # 2. Obtener el project_id a partir del enclosure_id asociado
        project_id = db.query(EnclosureGenerals.project_id).filter(
            EnclosureGenerals.id == wall_record.enclosure_id
        ).scalar()
        if not project_id:
            raise HTTPException(status_code=404, detail="No se encontró el proyecto asociado al ThermalBridgeWall.")

        # 3. Verificar permisos del usuario
        user_id = current_user["user_id"]
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este ThermalBridgeWall.")

        # 4. Eliminar el registrfdsfadsfo
        db.delete(wall_record)
        db.commit()
        return {"mensaje": "ThermalBridgeWall eliminado exitosamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar ThermalBridgeWall: {str(e)}")
