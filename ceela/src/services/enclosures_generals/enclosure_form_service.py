from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from src.models.entity.door import DoorEnclosure
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.floor import FloorEnclosure
from src.models.entity.obstruction import Division, Orientation
from src.models.entity.po.po import FloorPO, WallPO, WindowPO
from src.models.entity.roof import RoofEnclosure
from src.models.entity.thermal_bridges import ThermalBridgeWall
from src.models.entity.wall import WallEnclosure
from src.models.entity.window import WindowEnclosure
from src.models.schemas.enclosures_generals.enclosure_create import EnclosureGeneralsCreate
from src.models.entity.project_table import Project
from src.models.entity.regiones_comunas import Comuna, Region
from src.models.entity.enclosure import Enclosure
from src.models.schemas.projects.projects_update import ProjectStatus
from src.services.project.project_service import update_project_status  
from src.services.base.create_base.base import create_enclosure_base, delete_enclosures_bases, sync_enclosure_bases_debug

def create_enclosure_general(
    project_id: int, 
    enclosure: EnclosureGeneralsCreate, 
    current_user: dict, 
    db: Session
):

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"]
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=400,
            detail="El id del proyecto no pertenece al usuario actual"
        )
        
    # Se verifica que no exista otro recinto con el mismo nombre y que no esté eliminado
    exist_enclosure = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.name_enclosure == enclosure.name_enclosure,
        EnclosureGenerals.project_id == project_id,
        EnclosureGenerals.is_deleted == False
    ).first()
    
    if exist_enclosure:
        raise HTTPException(
            status_code=400,
           detail=f"El Nombre del Recinto '{exist_enclosure.name_enclosure}' ya existe en este proyecto"
        )
    
    # Se elimina la validación de comuna, región y zona térmica
    
    usage_profile = db.query(Enclosure).filter(
        Enclosure.id == enclosure.occupation_profile_id,
        or_(
            Enclosure.user_id == current_user["user_id"],
            Enclosure.user_id == None
        )
    ).first()
    
    if not usage_profile:
        raise HTTPException(
            status_code=400,
            detail="El perfil de uso seleccionado no existe o no pertenece al usuario"
        )
  
    enclosure_create = EnclosureGenerals(
        **enclosure.model_dump(), 
        project_id=project_id
    )
    
    
    
    update_project_status(
        project_id=project_id,
        new_status=ProjectStatus(status="en proceso"),
        current_user=current_user,
        db=db
    )
    
    try:
        db.add(enclosure_create)
        db.commit()
        db.refresh(enclosure_create)
        
        enclosure_original = enclosure_create.model_copy()
        create_enclosure_base(original_enclosure_id=enclosure_create.id, db=db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el recinto: {str(e)}")
    
    return enclosure_original


def get_enclosures_general(
    project_id: int,
    current_user: dict,
    db: Session
):
    # Si el usuario es admin (role_id == 1), no se aplica filtro por usuario
    project_query = db.query(Project).filter(Project.id == project_id)
    
    if current_user["role_id"] != 1:
        project_query = project_query.filter(Project.user_id == current_user["user_id"])
    
    project = project_query.first()

    if not project:
        raise HTTPException(
            status_code=400,
            detail="El id del proyecto no pertenece al usuario actual" 
                    if current_user["role_id"] != 1 
                    else "El proyecto no existe"
        )
    
    # Se consulta solamente la tabla de EnclosureGenerals y se une para obtener el perfil de uso
    enclosures_query = db.query(
        EnclosureGenerals,
        Enclosure.name.label("usage_profile_name")
    ).outerjoin(
        Enclosure, EnclosureGenerals.occupation_profile_id == Enclosure.id
    ).filter(
        EnclosureGenerals.project_id == project_id,
        EnclosureGenerals.is_deleted == False,
        or_(
            EnclosureGenerals.is_base == False,
            EnclosureGenerals.is_base == None
        )
    )
    
    enclosures = enclosures_query.all()
    
    if not enclosures:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron recintos para el proyecto"
        )
    
    # Se obtienen los valores zone y department del proyecto
    zone_department = db.query(
        Project.project_metadata["zone"],
        Project.divisions["department"],
        Project.divisions["province"],
        Project.divisions["district"]
    ).filter(
        Project.id == project_id    
    ).first()
    
    if not zone_department:
        raise HTTPException(
            status_code=400,
            detail="No se pudo obtener la zona termica ni el departamento del proyecto"
        )
    
    zone, department, province, district = zone_department
    
    # Se formatea el resultado sobrescribiendo los valores originales que pudiera tener "zona_termica" y "nombre_region"
    # con los valores obtenidos: zone y department, respectivamente.
    result = []
    for enclosure, usage_profile_name in enclosures:
        data = {
            **enclosure.model_dump(exclude={"zona_termica", "nombre_region"}),
            "id": enclosure.id,
            "name_enclosure": enclosure.name_enclosure,
            "nombre_region": department, 
            "nombre_comuna": province,# Se asigna el departamento obtenido
            "zona_termica": zone,           # Se asigna la zona obtenida
            "usage_profile_name": usage_profile_name,
            "district": district
        }
        result.append(data)
    
    return result



def delete_enclosure_general(
    project_id: int,
    enclosure_id: int,
    current_user: dict,
    db: Session
):
    # Verificar que el proyecto exista y pertenezca al usuario actual
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"]
    ).first()
    if not project:
        raise HTTPException(
            status_code=400,
            detail="El id del proyecto no pertenece al usuario actual"
        )

    # Obtener el recinto a eliminar
    enclosure = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.project_id == project_id,
        EnclosureGenerals.id == enclosure_id
    ).first()

    if not enclosure:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el recinto"
        )

    db.query(WallEnclosure).filter(WallEnclosure.enclosure_id == enclosure_id).delete()
    db.query(WindowEnclosure).filter(WindowEnclosure.enclosure_id == enclosure_id).delete()
    db.query(DoorEnclosure).filter(DoorEnclosure.enclosure_id == enclosure_id).delete()
    db.query(RoofEnclosure).filter(RoofEnclosure.enclosure_id == enclosure_id).delete()
    db.query(FloorEnclosure).filter(FloorEnclosure.enclosure_id == enclosure_id).delete() 
    orientations = db.query(Orientation).filter(Orientation.enclosure_id == enclosure_id).all()
    orientation_ids = [o.id for o in orientations]

    # 2. Eliminar las divisiones relacionadas a esas orientaciones
    db.query(Division).filter(Division.orientation_id.in_(orientation_ids)).delete(synchronize_session=False)

    # 3. Eliminar las orientaciones
    db.query(Orientation).filter(Orientation.enclosure_id == enclosure_id).delete()
    db.query(ThermalBridgeWall).filter(ThermalBridgeWall.enclosure_id == enclosure_id).delete()
    db.query(WallPO).filter(WallPO.enclosure_id == enclosure_id).delete()
    db.query(WindowPO).filter(WindowPO.enclosure_id == enclosure_id).delete()
    db.query(FloorPO).filter(FloorPO.enclosure_id == enclosure_id).delete()
        # Eliminar físicamente el recinto
    try:
        db.delete(enclosure)
        db.commit()
        remaining_enclosures = db.query(EnclosureGenerals).filter(
            EnclosureGenerals.project_id == project_id,
            EnclosureGenerals.is_deleted == False
        ).count()

        delete_enclosures_bases(original_id=enclosure.id, db=db)
        if remaining_enclosures == 0:
            update_project_status(
                project_id=project_id,
                new_status=ProjectStatus(status="registrado"),
                current_user=current_user,
                db=db
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar el recinto: {str(e)}")

    return {"detail": "Recinto eliminado permanentemente"}



def update_enclosure_general(
    project_id: int,
    enclosure_id: int,
    update_schema: EnclosureGeneralsCreate,
    current_user: dict,
    db: Session
):
    # Verificar que el proyecto exista y pertenezca al usuario actual
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"]
    ).first()
    if not project:
        raise HTTPException(
            status_code=400,
            detail="El id del proyecto no pertenece al usuario actual"
        )
    
    # Obtener el recinto general a actualizar, asegurándose que no esté eliminado
    enclosure = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.project_id == project_id,
        EnclosureGenerals.id == enclosure_id,
        EnclosureGenerals.is_deleted == False
    ).first()
    
    if not enclosure:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el recinto"
        )
    
    # Convertir el esquema a diccionario excluyendo campos no enviados
    update_data = update_schema.dict(exclude_unset=True)
    
    # Validar que no exista otro recinto con el mismo nombre en el mismo proyecto
    if "name_enclosure" in update_data:
        exist_enclosure = db.query(EnclosureGenerals).filter(
            EnclosureGenerals.name_enclosure == update_data["name_enclosure"],
            EnclosureGenerals.project_id == project_id,
            EnclosureGenerals.id != enclosure_id,
            EnclosureGenerals.is_deleted == False
        ).first()
        if exist_enclosure:
            raise HTTPException(
                status_code=400,
                detail=f"El Nombre del Recinto '{exist_enclosure.name_enclosure}' ya existe en este proyecto"
            )
    
    # Se eliminan las validaciones de comuna, región y zona térmica
    
    # Validar el perfil de uso sigue siendo necesario
    if "occupation_profile_id" in update_data:
        usage_profile = db.query(Enclosure).filter(
            Enclosure.id == update_data["occupation_profile_id"],
            or_(
                Enclosure.user_id == current_user["user_id"],
                Enclosure.user_id == None
            )
        ).first()
        
        if not usage_profile:
            raise HTTPException(
                status_code=400,
                detail="El perfil de uso seleccionado no existe o no pertenece al usuario"
            )
    
    # Actualizar los campos del recinto con los datos proporcionados sin las validaciones de comuna, región y zona térmica
    for key, value in update_data.items():
        setattr(enclosure, key, value)
    
    try:
        db.commit()
        db.refresh(enclosure)
        
        enclosure_return = enclosure.model_copy()
        sync_enclosure_bases_debug(original_enclosure_id=enclosure.id, db=db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el recinto: {str(e)}")
    
    return enclosure_return

