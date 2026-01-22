from typing import Dict, Any
from src.models.entity.elements import Element
from src.models.schemas.details.detail_part_update import DetailPartCreate
from src.services.constants.constants_service import get_material_by_code_ifc
from src.services.enclosures.enclosures_services import create_enclosure_typology
from src.services.elements.elements import create_elements, get_element_by_code_ifc
from src.models.schemas.enclosures.enclosure_create import EnclosureCreate
from src.services.details.detail_service import create_detail
from src.services.details.details_v2 import create_detail_part, create_detail_v2
from src.services.elements_enclosure.wall_service import create_wall_enclosure
from fastapi import HTTPException
import logging
from src.models.detail_base import DetailBase
from src.models.schemas.elements_enclosure.wall_enclosure_create import WallEnclosureCreate
from src.services.details.details_v2 import DetailPart
from src.services.elements.elements import get_element_by_code_ifc
def crear_pisos_para_recinto(enclosure_id, floor_groups, project_id, db, current_user):
    logger = logging.getLogger("process_structured_payload")
    for floor_group in floor_groups:
        for element in floor_group.get("elements", []):
            material_code = element.get("material")
            material_id = None
            if material_code and material_code.lower() != "unknown":
                try:
                    material = get_material_by_code_ifc(current_user, db, material_code)
                    material_id = material.id
                except Exception:
                    material_id = None
            detail = DetailBase(
                scantilon_location="Piso",
                name_detail=element.get("name", "Detalle"),
                material_id=material_id,
                layer_thickness=element.get("thickness", 0)
            )
            try:
                create_detail(detail, current_user, db)
                logger.info("Detalle de piso creado para %s", element.get("name"))
            except Exception as e:
                logger.error(f"Error creando detalle de piso: {e}")


def crear_techos_para_recinto(enclosure_id, ceiling_groups, project_id, db, current_user):
    logger = logging.getLogger("process_structured_payload")
    for ceiling_group in ceiling_groups:
        for element in ceiling_group.get("elements", []):
            material_code = element.get("material")
            material_id = None
            if material_code and material_code.lower() != "unknown":
                try:
                    material = get_material_by_code_ifc(current_user, db, material_code)
                    material_id = material.id
                except Exception:
                    material_id = None
            detail = DetailBase(
                scantilon_location="Techo",
                name_detail=element.get("name", "Detalle"),
                material_id=material_id,
                layer_thickness=element.get("thickness", 0)
            )
            try:
                create_detail(detail, current_user, db)
                logger.info("Detalle de techo creado para %s", element.get("name"))
            except Exception as e:
                logger.error(f"Error creando detalle de techo: {e}")


def crear_puertas_para_recinto(enclosure_id, door_groups, project_id, db, current_user):
    logger = logging.getLogger("process_structured_payload")
    for door_group in door_groups:
        for element in door_group.get("elements", []):
            code_ifc = element.get("id")
            section = "door"
            try:
                found_element = get_element_by_code_ifc(section, code_ifc, db)
                logger.info("Puerta encontrada: %s", element.get("name"))
            except Exception:
                logger.info("Puerta NO encontrada, se creará: %s", element.get("name"))
                element_data = Element(
                    name_element=element["name"],
                    type=section,
                    atributs=element,
                    u_marco=element.get("u_marco", 1.0),
                    fm=element.get("fm", 1.0)
                )
                try:
                    create_elements(section, element_data, current_user, db)
                    logger.info("Puerta creada: %s", element.get("name"))
                except Exception as e:
                    logger.error(f"Error creando puerta: {e}")


def crear_ventanas_para_recinto(enclosure_id, window_groups, project_id, db, current_user):
    logger = logging.getLogger("process_structured_payload")
    for window_group in window_groups:
        for element in window_group.get("elements", []):
            code_ifc = element.get("id")
            section = "window"
            try:
                found_element = get_element_by_code_ifc(section, code_ifc, db)
                logger.info("Ventana encontrada: %s", element.get("name"))
            except Exception:
                logger.info("Ventana NO encontrada, se creará: %s", element.get("name"))
                element_data = Element(
                    name_element=element["name"],
                    type=section,
                    atributs=element,
                    u_marco=element.get("u_marco", 1.0),
                    fm=element.get("fm", 1.0)
                )
                try:
                    create_elements(section, element_data, current_user, db)
                    logger.info("Ventana creada: %s", element.get("name"))
                except Exception as e:
                    logger.error(f"Error creando ventana: {e}")


def crear_muros_para_recinto(enclosure_id, wall_groups, project_id, db, current_user):
    logger = logging.getLogger("process_structured_payload")
    for wall_group in wall_groups:
        for element in wall_group.get("elements", []):
            # 1. Material
            material_code = element.get("material")
            material_id = None
            if material_code and material_code.lower() != "unknown":
                try:
                    material = get_material_by_code_ifc(current_user, db, material_code)
                    material_id = material.id
                except Exception:
                    logger.error(f"Material de muro no encontrado: {material_code}")
                    continue

            # 2. Busca o crea DetailPart
            detail_part = None
            try:
                # Busca por nombre y material
                existing = db.query(DetailPart).filter_by(
                    name_detail=element.get("name", "Detalle Muro"),
                    project_id=project_id
                ).first()
                if existing:
                    detail_part = existing
                else:
                    detail_part_obj = DetailPartCreate(
                        name_detail=element.get("name", "Detalle Muro"),
                        material_id=material_id,
                        thickness=element.get("thickness", 0),
                        info=element.get("info", {})
                    )
                    detail_part = create_detail_part(
                        db=db,
                        detail_create=detail_part_obj,
                        detail_type="Muro",
                        project_id=project_id,
                        current_user=current_user,
                        section="user"
                    )
                    
            except Exception as e:
                logger.error(f"Error obteniendo o creando detail_part de muro: {e}")
                continue  # No sigas con este muro

            # 3. Crea Detail v2 solo si hay detail_part
            detail_v2 = None
            try:
                detail_base_obj = DetailBase(
                    scantilon_location="Muro",
                    name_detail=element.get("name", "Detalle Muro"),
                    material_id=material_id,
                    layer_thickness=element.get("thickness", 0)
                )
                detail_v2 = create_detail_v2(
                    detail=detail_base_obj,
                    current_user=current_user,
                    db=db,
                    section="user",
                    detail_part_id=detail_part.id
                )
            except Exception as e:
                logger.error(f"Error creando detail_v2 de muro: {e}")
                # Puedes continuar, pero reportar

            # 4. wall_id seguro
            wall_id = element.get("wall_id")
            if wall_id is None:
                # Intenta buscar el elemento muro por code_ifc si existe en el payload
                code_ifc = element.get("code_ifc")
                if code_ifc:
                    try:
                        wall_elem = get_element_by_code_ifc("user", code_ifc, db)
                        wall_id = wall_elem.id
                    except Exception:
                        logger.error(f"No se encontró wall_id para el muro (code_ifc: {code_ifc}), saltando...")
                        continue
                else:
                    logger.error("No se encontró wall_id ni code_ifc para el muro, saltando...")
                    continue

            # 5. Crear WallEnclosureCreate solo si hay wall_id válido
            try:
                wall_obj = WallEnclosureCreate(
                    wall_id=wall_id,
                    characteristics=element.get("characteristics", ""),
                    angulo_azimut=element.get("angulo_azimut", ""),
                    area=element.get("area", 0)
                )
                create_wall_enclosure(
                    enclosure_id=enclosure_id,
                    wall=wall_obj,
                    current_user=current_user,
                    db=db
                )
                logger.info(f"Muro asociado al recinto {enclosure_id}: {element.get('name')}")
            except Exception as e:
                logger.error(f"Error asociando muro a recinto: {e}")

def crear_elementos_para_recinto(enclosure_id, construction, project_id, db, current_user):
    if construction.get("walls"):
        crear_muros_para_recinto(enclosure_id, construction.get("walls"), project_id, db, current_user)
    if construction.get("floors"):
        crear_pisos_para_recinto(enclosure_id, construction.get("floors"), project_id, db, current_user)
    if construction.get("ceilings"):
        crear_techos_para_recinto(enclosure_id, construction.get("ceilings"), project_id, db, current_user)
    if construction.get("doors"):
        crear_puertas_para_recinto(enclosure_id, construction.get("doors"), project_id, db, current_user)
    if construction.get("windows"):
        crear_ventanas_para_recinto(enclosure_id, construction.get("windows"), project_id, db, current_user)


def process_structured_payload(payload: Dict[str, Any], current_user: dict, db, project_id: int) -> Dict[str, Any]:
    logger = logging.getLogger("process_structured_payload")
    results = []
    errors = []
    if "buildingStructure" not in payload or not isinstance(payload["buildingStructure"], list):
        return {
            "success": False,
            "error": "El payload debe contener una lista 'buildingStructure' con los recintos a crear."
        }
    rooms = payload.get("buildingStructure", [])
    logger.info("Procesando %d recintos del payload", len(rooms))

    results = []
    errors = []
 
    missing_materials = []
    missing_elements = []
    material_cache = {}
    for room in rooms:
        construction = room.get("constructionDetails", {})
        for group_name in ["walls", "floors", "ceilings", "doors", "windows"]:
            for group in construction.get(group_name, []):
                for element in group.get("elements", []):
                    material_code = element.get("material")
                    if material_code and material_code.lower() != "unknown":
                        try:
                            if material_code in material_cache:
                                material = material_cache[material_code]
                            else:
                                material = get_material_by_code_ifc(current_user, db, material_code)
                                material_cache[material_code] = material
                            _ = material.id
                        except Exception:
                            logger.error(f"Falta material '{material_code}' en el recinto '{room.get('name')}', elemento '{element.get('name', '')}'")
                            missing_materials.append({
                                "material": material_code,
                                "room": room.get("name"),
                                "element": element.get("name", "")
                            })
    if missing_materials or missing_elements:
        return {
            "success": False,
            "missing_materials": missing_materials,
            "missing_elements": missing_elements
        }

    # 2. Crear recinto y detalles si todo está validado
    for room in rooms:
        try:
            construction = room.get("constructionDetails", {})
            logger.info("Creando recinto: %s", room.get('name'))
            enclosure_data = EnclosureCreate(name=room.get(
                "name", "Recinto"), project_id=project_id)
            enclosure_result = create_enclosure_typology(
                enclosure_data, "user", current_user, db)
            enclosure_id = enclosure_result["id"]
            logger.info("Recinto creado con ID: %s", enclosure_id)
            # Crear todos los elementos usando la función orquestadora
            crear_elementos_para_recinto(enclosure_id, construction, project_id, db, current_user)
            results.append({"room": room.get("name", "Recinto"),
                           "enclosure_id": enclosure_id})
            logger.info("Recinto procesado: %s", room.get('name'))
        except Exception as e:
            logger.error("Error procesando recinto %s: %s",
                         room.get('name'), str(e))
            errors.append({"room": room.get("name"), "error": str(e)})
    logger.info("Proceso finalizado. Recintos creados: %d", len(results))
    return {
        "success": True,
        "created_rooms": results,
        "errors": errors
    }
    return {"created": results, "errors": errors, "success": len(errors) == 0}


def validate_material_exists(material_code_ifc: str, current_user: dict, db) -> int:
    material = get_material_by_code_ifc(current_user, db, material_code_ifc)
    if not material:
        raise HTTPException(
            400, f"Material '{material_code_ifc}' no encontrado en la base de datos.")
    return material.id
