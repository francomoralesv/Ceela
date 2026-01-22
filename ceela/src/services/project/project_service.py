import json
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from src.decorators import cache
from src.models.entity.project_table import Project
from src.models.schemas.projects.project_create import ProjectCreate
from src.models.entity.constant import Constant
from src.models.schemas.projects.projects_update import ProjectStatus, ProjectUpdate
from src.models.entity.formulas import Formulas
from src.models.entity.details import Detail
from src.models.entity.elements import Element
from src.services.calculator.calculation_parameters import calculate_details_part
from src.models.entity.enclosure import Enclosure
from src.models.entity.building_conditions import BuildingCondition
from src.services.calculator.calculation_parameters import calculate_km_op_acumulated, calculate_position_insulation, recalculate_position_insulation
from src.services.details.detail_service import clone_global_details_optimized, clone_default_details_optimized

def create_project(current_user: dict, project_data: ProjectCreate, db: Session):
    if current_user.get("role_id") == 1:
        raise HTTPException(status_code=403, detail="El administrador no puede crear proyectos.")

    """Crea un proyecto con nombre, propietario y tipo de edificación"""

    existing_project = db.query(Project).filter(
        Project.name_project == project_data.name_project,
        Project.user_id == current_user["user_id"],
        Project.is_deleted == False
    ).first()

    if existing_project:
        raise HTTPException(status_code=400, detail=f"El Nombre del Proyecto ({existing_project.name_project}) ya existe")

    new_project = Project(
        **project_data.model_dump(),
        user_id=current_user["user_id"]
    )

    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        clone_global_details_optimized(new_project.id, db)
        clone_default_details_optimized(new_project.id, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el proyecto: {str(e)}")

    return {
        "project_id": new_project.id,
        "name": new_project.name_project,
        "owner": new_project.owner_name,
        "building_type": new_project.building_type,
        "message": "Proyecto creado exitosamente"
    }


def add_material_to_project(project_id: int, constants_ids: list[int], current_user: dict, db: Session):
    """Añade materiales a un proyecto copiando sus atributos usando bulk_insert_mappings"""

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"],
        Project.is_deleted == False
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    valid_constants = db.query(Constant).filter(
        Constant.id.in_(constants_ids),
        Constant.is_deleted == False
    ).all()

    valid_constant_ids = {const.id for const in valid_constants}

    invalid_materials = [mat_id for mat_id in constants_ids if mat_id not in valid_constant_ids]
    if invalid_materials:
        raise HTTPException(status_code=400, detail=f"Materiales no válidos: {invalid_materials}")

    existing_materials = db.query(Formulas.item_id).filter(
        Formulas.project_id == project_id,
        Formulas.item_id.in_(valid_constant_ids),
        Formulas.type == "materials",
        Formulas.is_deleted == False
    ).all()

    existing_material_ids = {formula.item_id for formula in existing_materials}
    
    new_materials = [
        {
            "project_id": project_id,
            "item_id": const.id,
            "type": "materials",
            "name": "materials",
            "atributs": const.atributs,
            "is_deleted": False
        }
        for const in valid_constants if const.id not in existing_material_ids
    ]

    if new_materials:
        try:
            db.bulk_insert_mappings(Formulas, new_materials)
            db.commit()
            return {"message": "Materiales agregados correctamente"}
        except IntegrityError:
            db.rollback()
            return {"message": "Todos los materiales ya estaban en el proyecto"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al agregar materiales: {str(e)}")

    return {"message": "Todos los materiales ya estaban en el proyecto"}


def add_details_to_project(project_id: int, details_ids: list[int], current_user: dict, db: Session):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"]
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    valid_details = db.query(Detail).filter(
        Detail.id.in_(details_ids),
        Detail.is_deleted == False
    ).all()
    
    if not valid_details:
        raise HTTPException(status_code=400, detail="Ningún detalle válido encontrado")
    
    valid_detail_ids = []
    detail_info = {}

    limit_cp_bordes = db.query(Constant.atributs["light_for_edge_layer"].as_float()).filter(
        Constant.name == "generals",
        Constant.type == "details"
    ).scalar() or 0.0
    
    for detail in valid_details:
        valid_detail_ids.append(detail.id)
        detail_info[detail.id] = {
            "scantilon_location": detail.scantilon_location,
            "name_detail": detail.name_detail,
            "material_id": detail.material_id,
            "layer_thickness": detail.layer_thickness,
            "km_op_acumulated": calculate_km_op_acumulated(db, detail), 
            "position_insulation": 0 
        }

    existing_detail_ids = {
        det.item_id for det in db.query(Formulas.item_id).filter(
            Formulas.project_id == project_id,
            Formulas.item_id.in_(valid_detail_ids),
            Formulas.type == "details",
            Formulas.is_deleted == False
        ).all()
    }

    new_formulas = [
        {
            "project_id": project_id,
            "item_id": det_id,
            "type": "details",
            "name": detail_info[det_id]["name_detail"],
            "atributs": detail_info[det_id],  
            "is_deleted": False
        }
        for det_id in valid_detail_ids if det_id not in existing_detail_ids
    ]
    
    if new_formulas:
        try:
            db.bulk_insert_mappings(Formulas, new_formulas)
            db.commit()  
            
            calculate_details_part(project_id, db)

            return {"message": "Detalles agregados correctamente"}
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400, 
                detail="Todos los detalles ya estaban en el proyecto"
            )
    
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al agregar detalles: {str(e)}")
    
    raise HTTPException(
        status_code=400, 
        detail="Todos los detalles ya estaban en el proyecto"
    )
    
    
def add_elements_windows_to_project(project_id: int, windows_ids: list[int], current_user: dict, db: Session):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"]
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    valid_windows = db.query(Element).filter(
        Element.id.in_(windows_ids),
        Element.type == "window",
        Element.is_deleted == False
    ).all()

    if not valid_windows:
        raise HTTPException(status_code=400, detail="No se encontraron ventanas válidas")

    valid_window_data = {
        win.id: {
            "name_element": win.name_element,
            "type": win.type,
            "u_marco": win.u_marco,
            "fm": win.fm,
            "atributs": win.atributs if isinstance(win.atributs, dict) else {}  
        }
        for win in valid_windows
    }

    existing_window_ids = {
        elem.item_id for elem in db.query(Formulas.item_id).filter(
            Formulas.project_id == project_id,
            Formulas.type == "elements",
            Formulas.name == "window",
            Formulas.is_deleted == False
        ).all()
    }

    new_formulas = [
        Formulas(
            project_id=project_id,
            item_id=win_id,
            type="elements",
            name="window",
            atributs=valid_window_data[win_id],  # Se almacena directamente como diccionario
            is_deleted=False
        )
        for win_id in valid_window_data if win_id not in existing_window_ids
    ]

    if new_formulas:
        try:
            db.add_all(new_formulas)
            db.commit()
            return {"message": "Ventanas agregadas correctamente"}
        except IntegrityError:
            db.rollback()
            return {"message": "Todas las ventanas ya estaban en el proyecto"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al agregar ventanas: {str(e)}")

    return {"message": "Todas las ventanas ya estaban en el proyecto"}


def add_elements_door_to_project(project_id: int, doors_ids: list[int], current_user: dict, db: Session):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"]
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    valid_doors = db.query(Element).filter(
        Element.id.in_(doors_ids),
        Element.type == "door",
        Element.is_deleted == False
    ).all()

    if not valid_doors:
        raise HTTPException(status_code=400, detail="No se encontraron puertas válidas")

    # Obtener todas las ventanas del proyecto con sus nombres en un diccionario
    window_name_map = {
        window.id: window.name_element
        for window in db.query(Element.id, Element.name_element).filter(
            Element.type == "window",
            Element.is_deleted == False
        ).all()
    }

    # Obtener todas las ventanas ya asociadas al proyecto
    existing_project_windows = {
        formula.item_id for formula in db.query(Formulas.item_id).filter(
            Formulas.project_id == project_id,
            Formulas.type == "elements",
            Formulas.name == "window",
            Formulas.is_deleted == False
        ).all()
    }

    valid_door_data = {}
    invalid_doors = []

    for door in valid_doors:
        attributes = door.atributs if isinstance(door.atributs, dict) else {}  # Evita json.loads()
        ventana_id = attributes.get("ventana_id")

        # Permitir puertas sin ventana asignada (ventana_id es "" o 0)
        if ventana_id not in ("", 0, None) and ventana_id not in existing_project_windows:
            invalid_doors.append({
                "door_name": door.name_element,
                "ventana_name": window_name_map.get(ventana_id, "Ventana desconocida")
            })
        else:
            valid_door_data[door.id] = {
                "name_element": door.name_element,
                "type": door.type,
                "u_marco": door.u_marco,
                "fm": door.fm,
                "atributs": attributes  # Se almacena directamente como diccionario
            }

    if invalid_doors:
        error_message = "Las siguientes puertas tienen ventanas no asociadas al proyecto:\n"
        error_message += "\n".join(
            f"- {door['door_name']} (Ventana: {door['ventana_name']})"
            for door in invalid_doors
        )
        
        raise HTTPException(status_code=400, detail=error_message)

    existing_door_ids = {
        formula.item_id for formula in db.query(Formulas.item_id).filter(
            Formulas.project_id == project_id,
            Formulas.type == "elements",
            Formulas.name == "door",
            Formulas.is_deleted == False
        ).all()
    }

    new_formulas = [
        Formulas(
            project_id=project_id,
            item_id=door_id,
            type="elements",
            name="door",
            atributs=valid_door_data[door_id],  # Se almacena directamente como diccionario
            is_deleted=False
        )
        for door_id in valid_door_data if door_id not in existing_door_ids
    ]

    if new_formulas:
        try:
            db.add_all(new_formulas)
            db.commit()
            return {"message": "Puertas agregadas correctamente"}
        except IntegrityError:
            db.rollback()
            return {"message": "Todas las puertas ya estaban en el proyecto"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al agregar puertas: {str(e)}")

    return {"message": "Todas las puertas ya estaban en el proyecto"}



   
   
def add_enclosure_type_to_project(project_id: int, enclosure_ids: list[int], current_user: dict, db: Session):
    """Añade tipos de recintos a un proyecto copiando sus atributos desde Enclosure y BuildingConditions"""

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"],
        Project.is_deleted == False
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    valid_enclosures = db.query(Enclosure).filter(
        Enclosure.id.in_(enclosure_ids),
        Enclosure.is_deleted == False
    ).all()

    valid_enclosure_ids = {enc.id for enc in valid_enclosures}

    invalid_enclosures = [enc_id for enc_id in enclosure_ids if enc_id not in valid_enclosure_ids]
    if invalid_enclosures:
        raise HTTPException(status_code=400, detail=f"Tipos de recintos no válidos: {invalid_enclosures}")

    building_conditions = db.query(BuildingCondition).filter(
        BuildingCondition.enclosure_id.in_(valid_enclosure_ids)
    ).all()

    conditions_by_enclosure = {}
    for condition in building_conditions:
        if condition.enclosure_id not in conditions_by_enclosure:
            conditions_by_enclosure[condition.enclosure_id] = {}

        conditions_by_enclosure[condition.enclosure_id][condition.type] = condition.attributes

    existing_enclosures = db.query(Formulas.item_id).filter(
        Formulas.project_id == project_id,
        Formulas.item_id.in_(valid_enclosure_ids),
        Formulas.type == "enclosures",
        Formulas.is_deleted == False
    ).all()

    existing_enclosure_ids = {formula.item_id for formula in existing_enclosures}

    new_enclosures = [
        {
            "project_id": project_id,
            "item_id": enc.id,
            "type": "enclosures",
            "name": "enclosures", 
            "atributs": {
                "enclosure_name": enc.name,
                "enclosure_code": enc.code,
                "building_conditions": conditions_by_enclosure.get(enc.id, {})
            },
            "is_deleted": False
        }
        for enc in valid_enclosures if enc.id not in existing_enclosure_ids
    ]

    if new_enclosures:
        try:
            db.bulk_insert_mappings(Formulas, new_enclosures)
            db.commit()
            return {"message": "Tipos de recintos agregados correctamente"}
        except IntegrityError:
            db.rollback()
            return {"message": "Todos los tipos de recintos ya estaban en el proyecto"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al agregar tipos de recintos: {str(e)}")

    return {"message": "Todos los tipos de recintos ya estaban en el proyecto"}

        

def list_projects(section: str, value: str, limit: int, num_pag: int, current_user: dict, db: Session):
    # Bloquea completamente a los usuarios con role_id == 2
    if section == "admin" and current_user["role_id"] == 2:
        return {
            "total_results": 0,
            "total_pages": 0,
            "current_page": num_pag,
            "per_page": limit,
            "projects": []
        }

    if section == "admin":  
        filtered_query = db.query(Project).filter(Project.is_deleted == False)
    elif section == "user":  
        filtered_query = db.query(Project).filter(
            Project.user_id == current_user["user_id"],
            Project.is_deleted == False
        )
    else:
        return {"error": "Sección inválida"}

    if value:
        filtered_query = filtered_query.filter(
            or_(
                Project.country.ilike(f"%{value}%"),
                Project.owner_name.ilike(f"%{value}%"),
                Project.owner_lastname.ilike(f"%{value}%"),
                Project.name_project.ilike(f"%{value}%"),
                func.concat(Project.owner_name, ' ', Project.owner_lastname).ilike(f"%{value}%")
            )
        )

    total_results = filtered_query.count()
    
    # Ordenar de forma ascendente por id
    filtered_query = filtered_query.order_by(Project.id.asc())

    offset = (num_pag - 1) * limit
    paginated_projects = filtered_query.offset(offset).limit(limit).all()

    projects_json = [jsonable_encoder(project, exclude={"user_id", "is_deleted"}) for project in paginated_projects]

    return {
        "total_results": total_results,
        "total_pages": (total_results // limit) + (1 if total_results % limit != 0 else 0),
        "current_page": num_pag,
        "per_page": limit,
        "projects": projects_json
    }


def get_project_by_id(current_user: dict, project_id: int, db: Session):
    exist_project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False
    ).first()
    
    if not exist_project:
        raise HTTPException(
            status_code=400,
            detail="No se encontro el proyecto"
        )

    print(f"exist_project.user: {current_user}")
    user_id = current_user.get('user_id', None) or current_user.get('id',None)
    if current_user["role_id"] == 2 and exist_project.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver este proyecto"
        )
    
    return exist_project

def get_project_by_id_only(project_id: int, db: Session):
    """Obtiene un proyecto por su ID sin verificar permisos de usuario"""

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return project
    
def update_project_status(project_id: int, new_status: ProjectStatus, current_user: dict, db: Session):
    project = db.get(Project, project_id)
    
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    is_admin = current_user.get("role_id") == 1
    
    if not is_admin and project.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para actualizar este proyecto")

    project.status = new_status.status

    try:
        db.commit()
        db.refresh(project)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el proyecto")
    
    return {
        "message": "Proyecto actualizado correctamente",
        "project": project
    }




def update_current_user_project(project_id: int, project_update: ProjectUpdate, current_user: dict, db: Session):
    # Bloquear a admin (role_id == 1) para actualizar proyectos
    if current_user.get("role_id") == 1:
        raise HTTPException(status_code=403, detail="El administrador no puede actualizar proyectos.")

    user_id = current_user["user_id"]
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id,
    ).first()

    if not project or project.is_deleted:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado o no tienes permisos para modificarlo."
        )

    update_data = project_update.model_dump(exclude_unset=True)  
    for key, value in update_data.items():
        setattr(project, key, value)

    try:
        db.add(project)
        db.commit()
        db.refresh(project)  
        return {"message": "Proyecto actualizado correctamente.", "project": project}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error al actualizar el proyecto: {str(e)}"
        )
    
def update_project(project_id: int, project_update: ProjectUpdate, db: Session):
    project = db.execute(
        db.query(Project).filter(
            Project.id == project_id,
            Project.is_deleted == False
        )
    )
    project = project.scalars().first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado."
        )

    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    try:
        db.add(project)
        db.commit()
        db.refresh(project)
        return {"message": "Proyecto actualizado correctamente.", "project": project}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error al actualizar el proyecto: {str(e)}"
        )

def delete_project(project_id: int, current_user: dict, db: Session):
    project = db.get(Project, project_id)
    
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    if project.user_id != current_user["user_id"] and current_user["role_id"] != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este proyecto")
    
    project.is_deleted = True
    
    try:
        db.commit()
        db.refresh(project)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar el proyecto")
    
    return {
        "message": "Proyecto eliminado exitosamente",
        "project": project
    }





