import re
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import Any, Dict, List, Optional
import json
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
from src.models.entity.enclosure import Enclosure
from src.models.entity.building_conditions import BuildingCondition
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.floor import FloorEnclosure
from src.models.schemas.elements_enclosure.floor import FloorEnclosureCreate
from src.models.schemas.enclosures.enclosure_create import EnclosureCreate
from src.models.schemas.building_conditions.building_conditions_create import BuildingConditionCreate
from src.services.calculator.calculator_enclosures import calculate_potencia_propuesta, calculate_r_pers
from src.models.entity.formulas import Formulas
from src.models.entity.project_table import Project
from src.models.entity.schedule import DailySchedule
from fastapi.encoders import jsonable_encoder
from src.services.schedule.schedule import create_daily_schedule
from fastapi import HTTPException

def generate_default_building_conditions(enclosure_id: int, current_user: dict, db: Session):
    """
    Genera las building_conditions por defecto para un recinto.
    Si el usuario es admin (role_id == 1), se asigna created_status = "global",
    de lo contrario se asigna "created".
    """
    default_status = "global" if current_user.get("role_id") == 1 else "created"
    section_mapping = {
        "ventilation_flows": {
            "cauldal_min_salubridad": {
                "ida": "IDA2",
                "ocupacion": "Sedentario",
                "r_pers": calculate_r_pers("ida2", "Sedentario", db)
            },
            "caudal_impuesto": {"vent_noct": 0.0},
            "infiltraciones": 0.0,
            "recuperador_calor": 0
        },
        "lightning": {
            "potencia_base": 8.0,
            "estrategia": "Sin estrategia",
            "potencia_propuesta": calculate_potencia_propuesta(8.0, "Sin estrategia", db)
        },
        "internal_loads": {
            "usuarios": 0.0,
            "calor_latente": 0.0,
            "calor_sensible": 0.0,
            "equipos": 0.0,
            "horario": {
                "funcionamiento_semanal": "5x2",
                "laboral": {
                    "inicio": 8,
                    "fin": 18
                }
            }
        },
        "schedule_weather": {
            "recinto": {
                "climatizado": "No",
                "desfase_clima": 0
            }
        }
    }
    
    conditions = []
    for section, attributes in section_mapping.items():
        conditions.append({
            "enclosure_id": enclosure_id,
            "type": section,
            "attributes": attributes,
            "created_status": default_status
        })
    
    return conditions



def get_enclosures(section: str, type: Optional[str], current_user: dict, db: Session):
    """
    Obtiene los recintos con sus building_conditions:
      - Si section es "admin": se devuelven solo los recintos globales (user_id == None).
      - Si section es "user": se devuelven los recintos globales y los que pertenecen al usuario.
      Además, se filtra para que si existe un clon para un recinto global, no se muestre el original.
      Se ordenan los resultados para que, en caso de clonación, el clon (con original_id) aparezca justo después del original.
      Finalmente, de los clones, si hay varios con el mismo nombre, solo se devuelve uno.
    """
    query = (
        db.query(Enclosure)
        .outerjoin(BuildingCondition, Enclosure.id == BuildingCondition.enclosure_id)
        .options(joinedload(Enclosure.building_conditions))
        .filter(Enclosure.is_deleted == False)
    )

    if section == "admin":
        query = query.filter(Enclosure.user_id == None)
    elif section == "user":
        # Se incluyen los recintos globales y los del usuario
        query = query.filter(
            or_(
                Enclosure.user_id == None,
                Enclosure.user_id == current_user["user_id"]
            )
        )
    else:
        raise HTTPException(status_code=400, detail="El parámetro section debe ser 'admin' o 'user'.")

    if type:
        query = query.filter(BuildingCondition.type == type)
    
    # Ordenamos usando coalesce para agrupar clones con su original:
    query = query.order_by(
        func.coalesce(Enclosure.original_id, Enclosure.id),
        Enclosure.id
    )
    enclosures = query.all()

    # Para la sección "user", se filtra: si existe un clon para un recinto global,
    # se muestra solo el clon y se omite el original.
    if section == "user":
        # Obtenemos los IDs originales que tienen un clon del usuario
        cloned_ids = {enclosure.original_id for enclosure in enclosures if enclosure.user_id == current_user["user_id"] and enclosure.original_id}
        # Filtramos: si un recinto es global (user_id is None) y su id está en cloned_ids, se omite.
        enclosures = [enclosure for enclosure in enclosures if not (enclosure.user_id is None and enclosure.id in cloned_ids)]
    
    # Ahora se arma la lista final:
    # Se incluyen todos los enclosures que no sean clones.
    # Para los clones, se agrupan por nombre y solo se incluye el primero encontrado para cada uno.
    final_enclosures = []
    seen_clone_names = set()
    for enclosure in enclosures:
        if enclosure.original_id is None:
            final_enclosures.append(enclosure)
        else:
            if enclosure.name not in seen_clone_names:
                final_enclosures.append(enclosure)
                seen_clone_names.add(enclosure.name)

    result = []
    for enclosure in final_enclosures:
        result.append({
            "id": enclosure.id,
            "code": enclosure.code,
            "name": enclosure.name,
            "created_status": enclosure.created_status,
            "is_deleted": enclosure.is_deleted,
            "original_id": getattr(enclosure, "original_id", None),
            "code_ifc": enclosure.code_ifc,
            "building_conditions": [
                {
                    "id": bc.id,
                    "enclosure_id": bc.enclosure_id,
                    "type": bc.type,
                    "created_status": bc.created_status,
                    "details": bc.attributes if hasattr(bc, 'attributes') else None 
                } for bc in enclosure.building_conditions if not type or bc.type == type
            ]
        })

    return result


def get_enclosure_by_id(enclosure_id: int, section: str, current_user: dict, db: Session):
    """
    Obtiene un recinto por su ID con sus building_conditions, filtrando según section:
      - "admin": permite acceder sólo a recintos globales (user_id == None).
      - "user": permite acceder a recintos globales o a los propios del usuario.
      Además, para la sección "user", si existe un clon para ese recinto, se retorna el clon en lugar del original.
    """
    if section == "user":
        # Primero, buscar si ya existe un clon para este recinto para el usuario
        cloned = db.query(Enclosure).filter(
            Enclosure.original_id == enclosure_id,
            Enclosure.user_id == current_user["user_id"],
            Enclosure.is_deleted == False
        ).options(joinedload(Enclosure.building_conditions)).first()
        if cloned:
            enclosure = cloned
        else:
            enclosure = db.query(Enclosure).filter(
                Enclosure.id == enclosure_id,
                Enclosure.is_deleted == False,
                or_(
                    Enclosure.user_id == None,
                    Enclosure.user_id == current_user["user_id"]
                )
            ).options(joinedload(Enclosure.building_conditions)).first()
    elif section == "admin":
        enclosure = db.query(Enclosure).filter(
            Enclosure.id == enclosure_id,
            Enclosure.is_deleted == False,
            Enclosure.user_id == None
        ).options(joinedload(Enclosure.building_conditions)).first()
    else:
        raise HTTPException(status_code=400, detail="El parámetro section debe ser 'admin' o 'user'.")

    if not enclosure:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")

    return {
        "id": enclosure.id,
        "code": enclosure.code,
        "name": enclosure.name,
        "created_status": enclosure.created_status,
        "is_deleted": enclosure.is_deleted,
        "building_conditions": [
            {
                "id": bc.id,
                "enclosure_id": bc.enclosure_id,
                "type": bc.type,
                "created_status": bc.created_status,
                "details": bc.attributes if hasattr(bc, 'attributes') else None
            }
            for bc in enclosure.building_conditions
        ]
    }

def get_enclosure_type_from_project(type: str, project_id: int, current_user: dict, db: Session):
    """Obtiene los tipos de recintos de un proyecto desde la tabla Formulas."""
    project = db.query(Project).filter(
        Project.user_id == current_user["user_id"],
        Project.id == project_id,
        Project.is_deleted == False
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    enclosures_data = db.query(Formulas).filter(
        Formulas.project_id == project_id,
        Formulas.type == "enclosures",
        Formulas.is_deleted == False
    ).all()

    if not enclosures_data:
        raise HTTPException(status_code=404, detail="No se encontraron tipos de recintos para este proyecto")

    enclosures_list = []
    for enclosure in enclosures_data:
        building_conditions = [
            {
                "id": bc.id,
                "enclosure_id": bc.enclosure_id,
                "type": bc.type,
                "created_status": bc.created_status,
                "details": bc.attributes if hasattr(bc, 'attributes') else None
            } for bc in db.query(BuildingCondition).filter(BuildingCondition.enclosure_id == enclosure.item_id).all()
            if not type or bc.type == type  # Filtrado de building_conditions
        ]

        if type and not building_conditions:
            continue  

        enclosure_info = {
            "id": enclosure.item_id,
            "code": enclosure.atributs.get("enclosure_code", "") if isinstance(enclosure.atributs, dict) else "",  
            "name": enclosure.atributs.get("enclosure_name", "") if isinstance(enclosure.atributs, dict) else "",  
            "is_deleted": enclosure.is_deleted,
            "building_conditions": building_conditions
        }
        enclosures_list.append(enclosure_info)

    return jsonable_encoder(enclosures_list)



from sqlalchemy import or_, func
from fastapi import HTTPException


def create_enclosure_typology(
    enclosure: 'EnclosureCreate',
    section: str,
    current_user: Dict[str, Any],
    db: Session
):
    """
    Crea un recinto en la tabla `enclosures`:

      1. Genera `code` usando `generate_code`.
      2. Genera `code_ifc` secuencial con prefijo 'pl_'.
         - Toma en cuenta *cualquier* código existente que termine en _###,
           p. ej. RECINTO_001, pl_007, etc., pero la numeración resultante
           es propia de recintos y siempre se genera como 'pl_###'.
      3. Maneja `section` ('admin' → global, 'user' → propio).
      4. Crea BuildingCondition y DailySchedule por defecto.
    """

    # ------------------------------------------------------------------ #
    # 1) Preparar datos básicos y validar sección
    # ------------------------------------------------------------------ #
    data = enclosure.model_dump()
    if section == "admin":
        data["created_status"] = "global"
        data["user_id"] = None
    elif section == "user":
        data["user_id"] = current_user["user_id"]
    else:
        raise HTTPException(400, "El parámetro section debe ser 'admin' o 'user'.")

    # ------------------------------------------------------------------ #
    # 2) Comprobar duplicado por nombre
    # ------------------------------------------------------------------ #
    dup_filter = [
        Enclosure.name == data["name"],
        Enclosure.is_deleted.is_(False),
    ]
    if section == "admin":
        dup_filter.append(Enclosure.user_id.is_(None))
    else:
        dup_filter.append(
            or_(
                Enclosure.user_id.is_(None),
                Enclosure.user_id == data["user_id"]
            )
        )

    # ------------------------------------------------------------------ #
    # 3) Crear la instancia y generar `code`
    # ------------------------------------------------------------------ #
    enclosure_typology = Enclosure(**data)
    code = enclosure_typology.generate_code(db)
    if not code:
        raise HTTPException(400, "No se pudo generar un código válido para el recinto.")
    enclosure_typology.code = code

    db.add(enclosure_typology)
    db.commit()
    db.refresh(enclosure_typology)

    # ------------------------------------------------------------------ #
    # 4) Generar `code_ifc` con numeración propia (pl_###)
    # ------------------------------------------------------------------ #
    canonical_prefix = "OCP"
    legacy_prefixes  = ["pl", "OCP", "PLANT"]   # cualquier variante válida

    # Regex: ^(pl|RECINTO|PLANT)_[0-9]{3}$
    regex = rf"^({'|'.join(legacy_prefixes)})_[0-9]{{3}}$"

    existing_codes = db.query(Enclosure.code_ifc).filter(
        Enclosure.code_ifc.op("~")(regex)
    ).all()

    nums = []
    for (code_ifc,) in existing_codes:
        if code_ifc:
            m = re.match(r".*_([0-9]{3})$", code_ifc)
            if m:
                nums.append(int(m.group(1)))

    next_num = max(nums) + 1 if nums else 1
    enclosure_typology.code_ifc = f"{canonical_prefix}_{next_num:03d}"

    db.commit()
    db.refresh(enclosure_typology)

    # ------------------------------------------------------------------ #
    # 5) Crear condiciones y horarios por defecto
    # ------------------------------------------------------------------ #
    default_conditions = generate_default_building_conditions(
        enclosure_typology.id, current_user, db
    )
    if default_conditions:
        db.bulk_save_objects(
            [BuildingCondition(**cond) for cond in default_conditions]
        )
        db.commit()

    create_daily_schedule(
        user_id=data["user_id"],
        perfil_id=enclosure_typology.id,
        db=db
    )

    # ------------------------------------------------------------------ #
    # 6) Respuesta
    # ------------------------------------------------------------------ #
    return {
        "message": "Tipo de Recinto creado exitosamente",
        "id": enclosure_typology.id,
        "code": enclosure_typology.code,
        "code_ifc": enclosure_typology.code_ifc
    }


    
    

def deep_update(target: dict, updates: dict):
    """
    Actualiza un diccionario de manera recursiva sin sobrescribir estructuras completas.
    """
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_update(target[key], value)
        else:
            target[key] = value

def clone_enclosure(enclosure: Enclosure, current_user: dict, db: Session) -> Enclosure:
    """
    Clona un recinto global y sus building_conditions (así como los DailySchedule).
    Si el usuario es admin, las building_conditions clonadas tendrán created_status = "global",
    de lo contrario se asignarán como "cloned".
    """
    # Clonar el recinto
    cloned_enclosure = Enclosure(
        name = enclosure.name,
        code = enclosure.code,
        created_status = "cloned",
        user_id = current_user["user_id"],
        is_deleted = enclosure.is_deleted,
        original_id = enclosure.id,
        code_ifc = enclosure.code_ifc
        # Copia otros campos necesarios...
    )
    
    db.add(cloned_enclosure)
    db.commit()
    db.refresh(cloned_enclosure)
    
    # Clonar las building_conditions
    for bc in enclosure.building_conditions:
        cloned_bc = BuildingCondition(
            enclosure_id = cloned_enclosure.id,
            type = bc.type,
            created_status = "global" if current_user.get("role_id") == 1 else "cloned",
            attributes = bc.attributes
            # Clonar otros campos si es necesario
        )
        db.add(cloned_bc)
    db.commit()
    
    # Clonar los registros de DailySchedule asociados al recinto original
    original_schedules = db.query(DailySchedule).filter(DailySchedule.perfil_id == enclosure.id).all()
    for schedule in original_schedules:
        schedule_data = schedule.__dict__.copy()
        schedule_data.pop("id", None)
        schedule_data.pop("_sa_instance_state", None)
        schedule_data["perfil_id"] = cloned_enclosure.id
        schedule_data["user_id"] = current_user["user_id"]
        new_schedule = DailySchedule(**schedule_data)
        db.add(new_schedule)
    db.commit()
    
    db.refresh(cloned_enclosure)
    return cloned_enclosure


def update_building_condition(
    updates: BuildingConditionCreate,
    enclosure_id: int,
    section: str,  # "admin" o "user"
    current_user: dict,
    db: Session
):
    """
    Actualiza una condición de construcción.
      - Si section es "admin": solo el admin (role_id == 1) puede editar y se actualiza el registro global.
      - Si section es "user": 
          * Si el recinto es global (user_id es None) y su created_status es "default" o "global", se clona el recinto 
            (y sus building_conditions y schedules) para que el usuario trabaje sobre su copia.
          * Si el recinto ya es propio o ya fue clonado (created_status distinto de "default"/"global"), se actualiza directamente.
    """
    # Buscar el recinto con sus building_conditions
    enclosure = (
        db.query(Enclosure)
        .filter(Enclosure.id == enclosure_id, Enclosure.is_deleted == False)
        .options(joinedload(Enclosure.building_conditions))
        .first()
    )
    
    if not enclosure:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")
    
    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(status_code=403, detail="No tienes permisos para actualizar condiciones de construcción como admin")
        # En modo admin se actualiza el recinto global directamente.
    elif section == "user":
        # Si el recinto es global (user_id is None) y su created_status es "default" o "global", clonarlo para que el usuario trabaje sobre su copia.
        if enclosure.user_id is None and enclosure.created_status in ["default", "global"]:
            enclosure = clone_enclosure(enclosure, current_user, db)
        else:
            # Si ya es propio o fue clonado, se debe validar que el recinto pertenece al usuario
            if enclosure.user_id != current_user["user_id"]:
                raise HTTPException(status_code=403, detail="No tienes permisos para actualizar este recinto")
    else:
        raise HTTPException(status_code=400, detail="El parámetro section debe ser 'admin' o 'user'.")
    
    # Buscar la building condition a actualizar en el recinto (global, clonado o propio)
    condition = None
    for bc in enclosure.building_conditions:
        if bc.type == updates.type:
            condition = bc
            break

    if not condition:
        raise HTTPException(status_code=404, detail="Condición de construcción no encontrada")
    
    # Convertir los atributos a diccionario si es que vienen como string
    attributes = condition.attributes
    if isinstance(attributes, str):
        attributes = json.loads(attributes)
    
    print("ANTES DE ACTUALIZAR:", attributes)
    
    recalculate_ventilation = False
    recalculate_lightning = False
    
    deep_update(attributes, updates.attributes)
    
    if updates.type == "ventilation_flows":
        if "cauldal_min_salubridad" in updates.attributes and any(
            k in updates.attributes["cauldal_min_salubridad"] for k in ["ida", "ocupacion"]
        ):
            recalculate_ventilation = True
    
    if updates.type == "lightning":
        if any(k in updates.attributes for k in ["potencia_base", "estrategia"]):
            recalculate_lightning = True
    
    if recalculate_ventilation:
        attributes.setdefault("cauldal_min_salubridad", {})
        attributes["cauldal_min_salubridad"]["r_pers"] = calculate_r_pers(
            attributes["cauldal_min_salubridad"].get("ida", "").lower(),
            attributes["cauldal_min_salubridad"].get("ocupacion", 0),
            db
        )
    
    if recalculate_lightning:
        attributes["potencia_propuesta"] = calculate_potencia_propuesta(
            attributes.get("potencia_base", 0),
            attributes.get("estrategia", ""),
            db
        )
    
    print("DESPUÉS DE ACTUALIZAR:", attributes)
    
    condition.attributes = attributes
    flag_modified(condition, "attributes")
    db.commit()
    
    # Si se actualiza el building condition de tipo "internal_loads" y se han cambiado los valores de inicio o fin,
    # se deben actualizar también los horarios de DailySchedule asociados al recinto.
    if updates.type == "internal_loads" and "horario" in updates.attributes:
        horario = updates.attributes.get("horario", {})
        laboral = horario.get("laboral", {})
        inicio_raw = laboral.get("inicio")
        fin_raw = laboral.get("fin")

        if inicio_raw is not None and fin_raw is not None:
            try:
                inicio = int(inicio_raw.split(":")[0])
                fin = int(fin_raw.split(":")[0])
            except Exception:
                raise ValueError("Los valores de inicio y fin deben estar en formato HH:MM")
            schedules = db.query(DailySchedule).filter(DailySchedule.perfil_id == enclosure.id).all()
            for schedule in schedules:
                # 1. Rellenar desde el inicio hacia adelante
                for h in range(inicio, 25):
                    key = f"hour_{h}"
                    valor = getattr(schedule, key)
                    if valor == 0:
                        setattr(schedule, key, 100)
                    else:
                        break  # Detener al encontrar una barra ya llena
                # 2. Rellenar desde el fin hacia atrás
                for h in range(fin, 0, -1):
                    key = f"hour_{h}"
                    valor = getattr(schedule, key)
                    if valor == 0:
                        setattr(schedule, key, 100)
                    else:
                        break  # Detener al encontrar una barra ya llena

            db.commit()



def delete_enclosure_typing(enclosure_id: int, section: str, current_user: dict, db: Session):
    """
    Elimina un recinto:
      - Si section es "admin": se permite borrar únicamente recintos globales (user_id == None) 
        que tengan created_status igual a "created".
      - Si section es "user": se permite borrar únicamente recintos propios (user_id == current_user["user_id"])
        que tengan created_status igual a "created".
      
      Esto garantiza que solo se puedan borrar recintos clonados o default (con created_status="created"),
      impidiendo eliminar aquellos que no cumplan esta condición.
    """
    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar recintos como admin")
        # Buscar solo recintos globales con created_status "created"
        enclosure = db.query(Enclosure).filter(
            Enclosure.id == enclosure_id,
            Enclosure.is_deleted == False,
            Enclosure.user_id == None,
        ).first()
        if not enclosure:
            raise HTTPException(status_code=404, detail="No se encontró la tipología de recinto")
    elif section == "user":
        # Para el usuario, solo se pueden borrar los recintos propios con created_status "created"
        enclosure = db.query(Enclosure).filter(
            Enclosure.id == enclosure_id,
            Enclosure.is_deleted == False,
            Enclosure.user_id == current_user["user_id"],
            Enclosure.created_status == "created"
        ).first()
        if not enclosure:
            raise HTTPException(status_code=404, detail="No se encontró la tipología de recinto")
    else:
        raise HTTPException(status_code=400, detail="El parámetro section debe ser 'admin' o 'user'.")

    # Marcar el recinto como eliminado
    enclosure.is_deleted = True

    try:
        db.commit()
        db.refresh(enclosure)
        return {"message": "Tipología de recinto eliminada correctamente"}
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar recinto: {str(e)}")


def clone_enclosures_for_user(
    db: Session,
    current_user: dict
):
    """
    Clona todos los recintos globales (user_id == None) que tengan created_status igual a 'default' o 'global'
    para el usuario actual. Si para un recinto ya existe un clon (con original_id == id del original) para el usuario,
    se omite su clonación.
    """
    # Se obtienen los recintos globales con created_status 'default' o 'global'
    enclosures_to_clone: List[Enclosure] = (
        db.query(Enclosure)
        .filter(
            Enclosure.is_deleted == False,
            Enclosure.user_id.is_(None),
            Enclosure.created_status.in_(["default", "global"])
        )
        .all()
    )

    cloned_results = []
    for enclosure in enclosures_to_clone:
        # Verificar si ya existe un clon para este recinto en el usuario actual
        existing_clone = (
            db.query(Enclosure)
            .filter(
                Enclosure.original_id == enclosure.id,
                Enclosure.user_id == current_user["user_id"],
                Enclosure.is_deleted == False
            )
            .first()
        )
        if existing_clone:
            # Omitir si ya se clonó
            continue
        
        # Clonar el recinto (junto con sus building_conditions y horarios)
        cloned_enclosure = clone_enclosure(enclosure, current_user, db)
        cloned_results.append({
            "original_id": enclosure.id,
            "cloned_id": cloned_enclosure.id,
            "code": cloned_enclosure.code,
            "name": cloned_enclosure.name,
            "code_ifc": cloned_enclosure.code_ifc
        })

    if not cloned_results:
        return {"message": "No se clonaron recintos, ya existen copias para el usuario"}
    
    return {
        "message": "Clonación completada exitosamente",
        "cloned_enclosures": cloned_results
    }
    
    
    
    
def get_building_conditions_week_details(
    enclosure_id: int,
    section: str,  # "admin" o "user"
    db: Session,
    current_user: dict
):
    """
    Devuelve, para un recinto, la información por días y horas, de la siguiente forma:
      - Los días se definen manualmente: "Lunes", "Martes", …, "Domingo".
      - Para cada día se generan 24 horas (hour_1 .. hour_24).
      - Se consulta la tabla DailySchedule filtrando por perfil_id (enclosure_id).
      - Se asume que cada registro de DailySchedule tiene un atributo "week_day" (ajústalo según tu modelo)
        que identifica el día (por ejemplo: "Lunes").
      - Por cada hora:
            Si el valor en DailySchedule es 0 o no existe registro, se asigna 0.
            Si es distinto de 0, se asigna el objeto BuildingCondition (por ejemplo, el de tipo "lightning")
            con sus datos.
    """

    # 1. Validar existencia del recinto y permisos
    enclosure = (
        db.query(Enclosure)
          .filter(Enclosure.id == enclosure_id, Enclosure.is_deleted == False)
          .options(joinedload(Enclosure.building_conditions))
          .first()
    )
    if not enclosure:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")

    if section == "admin":
        if enclosure.user_id is not None:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para ver este recinto como admin"
            )
        if current_user.get("role_id") != 1:
            raise HTTPException(
                status_code=403,
                detail="No tienes privilegios de administrador"
            )
    elif section == "user":
        if enclosure.user_id not in [None, current_user.get("user_id")]:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para ver este recinto"
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="El parámetro section debe ser 'admin' o 'user'."
        )

    # 2. Definir manualmente los días de la semana
    days_of_week = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    # 3. Consultar los DailySchedule asociados al recinto (filtrando por perfil_id)
    schedules = db.query(DailySchedule).filter(
        DailySchedule.perfil_id == enclosure_id
    ).all()
    # Se crea un diccionario usando como clave el atributo "week_day" (ajústalo según tu modelo)
    schedule_by_day = {}
    for sched in schedules:
        # Usamos 'week_day' en lugar de 'day'
        if hasattr(sched, "week_day") and sched.week_day in days_of_week:
            schedule_by_day[sched.week_day] = sched

    # 4. Consultar el BuildingCondition de interés; en este ejemplo se usa el de tipo "lightning"
    lightning_condition = (
        db.query(BuildingCondition)
          .filter(
              BuildingCondition.enclosure_id == enclosure_id,
              BuildingCondition.type == "lightning"
          )
          .first()
    )
    if not lightning_condition:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el BuildingCondition de tipo 'lightning' para este recinto"
        )
    # Objeto con detalle a asignar si el valor en la hora es distinto de 0
    bc_detail = {
        "id": lightning_condition.id,
        "enclosure_id": lightning_condition.enclosure_id,
        "type": lightning_condition.type,
        "created_status": lightning_condition.created_status,
        "attributes": lightning_condition.attributes,
    }

    # 5. Construir la estructura final: por cada día manual y por cada hora, asignar 0 o el objeto bc_detail
    days_data = {}
    for day in days_of_week:
        hours_map = {}
        # Obtenemos el DailySchedule para el día si existe, usando "week_day"
        sched = schedule_by_day.get(day)
        for h in range(1, 25):
            column = f"hour_{h}"
            # Si existe el registro para el día, obtenemos el valor; de lo contrario, se asume 0
            hour_value = (getattr(sched, column, None) if sched else 0) or 0
            if hour_value == 0:
                hours_map[column] = 0
            else:
                hours_map[column] = bc_detail
        days_data[day] = hours_map

    # 6. Retornar la respuesta final
    return {
        "enclosure_id": enclosure.id,
        "code": enclosure.code,
        "name": enclosure.name,
        "days": days_data
    }

def get_enclosure_by_code(code: str, current_user: dict, db: Session):
    """
    Busca un recinto (enclosure) por su código.
    
    Args:
        code (str): Código del recinto a buscar.
        section (str): Sección donde se encuentra el recinto.
        current_user (dict): Información del usuario actual.
        db (Session): Sesión de base de datos.
        
    Returns:
        dict: Información del recinto y sus condiciones de construcción asociadas.
        
    Raises:
        HTTPException: Si el recinto no existe o ha sido eliminado.
    """
    
    # Buscar el recinto por código
    enclosure = db.query(Enclosure).filter(
        Enclosure.code == code,
        Enclosure.created_status == "cloned",
        Enclosure.is_deleted == False,
        Enclosure.user_id == current_user["user_id"]
    ).first()
    
    if not enclosure:
        raise HTTPException(status_code=404, detail=f"Recinto con código {code} no encontrado")
    
    
    # Construir la respuesta
    result = {
        "id": enclosure.id,
        "code": enclosure.code,
        "created_status": enclosure.created_status,
        "is_deleted": enclosure.is_deleted,
        "code_ifc": enclosure.code_ifc,
        "name": enclosure.name,
    }
    
    return result


def get_enclosure_ventilation_flows_by_id(enclosure_id: int, key: str, db: Session) -> dict:
    """
    Devuelve el valor de un campo específico dentro de ventilation_flows para un recinto dado su ID.
    Args:
        enclosure_id (int): ID del recinto.
        key (str): Clave a buscar dentro de attributes (por ejemplo, "infiltraciones", "cauldal_min_salubridad").
        db (Session): Sesión de base de datos.
    Returns:
        dict: Valor correspondiente a la clave solicitada.
    """

    enclosure = (
        db.query(EnclosureGenerals)
        .filter(
            EnclosureGenerals.id == enclosure_id,
            EnclosureGenerals.is_deleted == False
        )
        .first()
    )
    if not enclosure:
        raise HTTPException(status_code=404, detail="Recinto global no encontrado")

    occupation_profile_id = enclosure.occupation_profile_id
    if not occupation_profile_id:
        raise HTTPException(status_code=404, detail="No se encontró occupation_profile_id en ventilation_flows")

    occupation_profile = db.query(BuildingCondition).filter(
        BuildingCondition.enclosure_id == occupation_profile_id,
        BuildingCondition.type == "ventilation_flows"
    ).first()
    if not occupation_profile:
        raise HTTPException(status_code=404, detail="No se encontró el perfil de ocupación asociado")

    attributes = occupation_profile.attributes
    if isinstance(attributes, str):
        attributes = json.loads(attributes)

    if key not in attributes:
        raise HTTPException(status_code=404, detail=f"No se encontró la clave '{key}' en ventilation_flows")
    return {"value": attributes.get(key, None)}

def get_enclosure_internal_loads(enclosure_id: int, db: Session) -> dict:
    """
    Devuelve el valor de un campo específico dentro de internal_loads para un recinto dado su ID.
    Args:
        enclosure_id (int): ID del recinto.
        key (str): Clave a buscar dentro de attributes (por ejemplo, "usuarios", "equipos", "horario").
        db (Session): Sesión de base de datos.
    Returns:
        dict: Valor correspondiente a la clave solicitada.
    """

    enclosure = (
        db.query(EnclosureGenerals)
        .filter(
            EnclosureGenerals.id == enclosure_id,
            EnclosureGenerals.is_deleted == False
        )
        .first()
    )
    if not enclosure:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")
    occupation_profile_id = enclosure.occupation_profile_id
    if not occupation_profile_id:
        raise HTTPException(status_code=404, detail="No se encontró perfil de ocupacion del recinto")

    occupation_profile = db.query(BuildingCondition).filter(
        BuildingCondition.enclosure_id == occupation_profile_id,
        BuildingCondition.type == "internal_loads"
    ).first()
    if not occupation_profile:
        raise HTTPException(status_code=404, detail="No se encontró el perfil de ocupación asociado a cargas internas")

    print("Internal loads occupation profile:", occupation_profile)
    return occupation_profile.attributes


def get_enclosure_internal_loads_by_id(enclosure_id: int, key: str, db: Session) -> dict:
    """
    Devuelve el valor de un campo específico dentro de internal_loads para un recinto dado su ID.
    Args:
        enclosure_id (int): ID del recinto.
        key (str): Clave a buscar dentro de attributes (por ejemplo, "usuarios", "equipos", "horario").
        db (Session): Sesión de base de datos.
    Returns:
        dict: Valor correspondiente a la clave solicitada.
    """

    enclosure = (
        db.query(EnclosureGenerals)
        .filter(
            EnclosureGenerals.id == enclosure_id,
            EnclosureGenerals.is_deleted == False
        )
        .first()
    )
    if not enclosure:
        raise HTTPException(status_code=404, detail="Recinto global no encontrado")
    occupation_profile_id = enclosure.occupation_profile_id
    if not occupation_profile_id:
        raise HTTPException(status_code=404, detail="No se encontró occupation_profile_id")

    occupation_profile = db.query(BuildingCondition).filter(
        BuildingCondition.enclosure_id == occupation_profile_id,
        BuildingCondition.type == "internal_loads"
    ).first()
    if not occupation_profile:
        raise HTTPException(status_code=404, detail="No se encontró el perfil de ocupación asociado internal loads")

    print("Internal loads occupation profile:", occupation_profile)
    attributes = occupation_profile.attributes
    if isinstance(attributes, str):
        attributes = json.loads(attributes)

    if key not in attributes:
        raise HTTPException(status_code=404, detail=f"No se encontró la clave '{key}' en ventilation_flows")
    return {"value": attributes.get(key, None)}

def get_enclosure_lightning_by_id(enclosure_id: int, key: str, db: Session) -> dict:
    """
    Devuelve el valor de un campo específico dentro de internal_loads para un recinto dado su ID.
    Args:
        enclosure_id (int): ID del recinto.
        key (str): Clave a buscar dentro de attributes (por ejemplo, "usuarios", "equipos", "horario").
        db (Session): Sesión de base de datos.
    Returns:
        dict: Valor correspondiente a la clave solicitada.
    """

    enclosure = (
        db.query(EnclosureGenerals)
        .filter(
            EnclosureGenerals.id == enclosure_id,
            EnclosureGenerals.is_deleted == False
        )
        .first()
    )
    if not enclosure:
        raise HTTPException(status_code=404, detail="Recinto global no encontrado")
    occupation_profile_id = enclosure.occupation_profile_id
    if not occupation_profile_id:
        raise HTTPException(status_code=404, detail="No se encontró occupation_profile_id")

    occupation_profile = db.query(BuildingCondition).filter(
        BuildingCondition.enclosure_id == occupation_profile_id,
        BuildingCondition.type == "lightning"
    ).first()
    if not occupation_profile:
        raise HTTPException(status_code=404, detail="No se encontró el perfil de ocupación asociado internal loads")

    print("lightning occupation profile:", occupation_profile)
    attributes = occupation_profile.attributes
    if isinstance(attributes, str):
        attributes = json.loads(attributes)

    if key not in attributes:
        raise HTTPException(status_code=404, detail=f"No se encontró la clave '{key}' en ventilation_flows")
    return {"value": attributes.get(key, None)}
def get_total_floor_area_by_enclosure_id(enclosure_id, db):
    result = db.query(func.sum(FloorEnclosure.area)).filter(
        FloorEnclosure.enclosure_id == enclosure_id
    ).scalar()
    return result or 0

def get_typing_enclosure_by_id(enclosure_id: int, db: Session):
    conditions = db.query(BuildingCondition).filter(
        BuildingCondition.enclosure_id == enclosure_id
    ).all()
    result = {}
    for cond in conditions:
        attrs = cond.attributes
        if isinstance(attrs, str):
            attrs = json.loads(attrs)
        result[cond.type] = attrs
    return result