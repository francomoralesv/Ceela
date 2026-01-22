
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, case
from sqlalchemy.orm.attributes import flag_modified
from src.models.entity.elements import Element
from src.models.element_base import ElementBase
from src.models.entity.formulas import Formulas
from src.models.entity.project_table import Project
from src.models.entity.constant import Constant
from src.services.calculator.calculation_parameters import calculate_element_door
from typing import Dict, Any
import re


def create_elements(section: str, elements: 'ElementBase', current_user: Dict[str, Any], db: Session):
    """
    Crea un elemento (puerta o ventana) y asigna un code_ifc único.

    - Admin: puede crear elementos globales; usuario normal: sólo propios.
    - Genera code_ifc como:
        * pt_### para puertas
        * vt_### para ventanas
      Cada tipo lleva su numeración independiente, aun si existen códigos
      antiguos como PUERT_001 o VENTANA_001.
    """
    # ------------------------------------------------------------------ #
    # 1) Validar la sección
    # ------------------------------------------------------------------ #
    if section not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Sección no válida")

    # ------------------------------------------------------------------ #
    # 2) Validar unicidad de nombre
    # ------------------------------------------------------------------ #
    if section == "admin":
        exist_element = db.query(Element).filter(
            Element.name_element == elements.name_element,
            Element.type == elements.type,
            Element.is_deleted.is_(False),
            Element.user_id.is_(None)
        ).first()
    else:
        exist_element = db.query(Element).filter(
            Element.name_element == elements.name_element,
            Element.type == elements.type,
            Element.is_deleted.is_(False),
            or_(
                Element.user_id.is_(None),
                Element.user_id == current_user["user_id"]
            )
        ).first()

    if exist_element:
        raise HTTPException(
            status_code=400,
            detail=f"El nombre del elemento ya existe dentro del tipo {elements.type}"
        )

    # ------------------------------------------------------------------ #
    # 3) Prefijos y regex por tipo (cada tipo con contador separado)
    # ------------------------------------------------------------------ #
    if elements.type == "door":
        canonical_prefix = "PUERTA"              # nuevo prefijo estándar
        legacy_prefixes = ["PUERTA", "PUERT"]   # variantes ya existentes
    elif elements.type == "window":
        canonical_prefix = "VENTANA"
        legacy_prefixes = ["VENTANA", "VENTANA"]
    else:                                    # “el_” como genérico
        canonical_prefix = "el"
        legacy_prefixes = ["el"]

    #   Regex: ^(pt|PUERT)_[0-9]{3}$   ,   ^(vt|VENTANA)_[0-9]{3}$
    regex = rf"^({'|'.join(legacy_prefixes)})_[0-9]{{3}}$"

    existing_codes = db.query(Element.code_ifc).filter(
        Element.code_ifc.op("~")(regex)      # operador regex de PostgreSQL
    ).all()

    nums = []
    for (code,) in existing_codes:
        if code:
            m = re.match(r".*_([0-9]{3})$", code)
            if m:
                nums.append(int(m.group(1)))

    next_num = max(nums) + 1 if nums else 1
    generated_code = f"{canonical_prefix}_{next_num:03d}"

    # ------------------------------------------------------------------ #
    # 4) Validación especial para puertas (ventana_id)
    # ------------------------------------------------------------------ #
    if elements.type == "door":
        ventana_id = elements.atributs.get("ventana_id")
        if ventana_id and ventana_id > 0:
            valid_windows = {
                id_tuple[0]
                for id_tuple in db.query(Element.id).filter(Element.type == "window").all()
            }
            if ventana_id not in valid_windows:
                raise HTTPException(
                    status_code=400,
                    detail="El id proporcionado no pertenece a una ventana existente"
                )

    # ------------------------------------------------------------------ #
    # 5) Ajuste de fm y preparación de datos
    # ------------------------------------------------------------------ #
    if elements.fm is not None:
        elements.fm = elements.fm / 100      # de % a fracción

    data = elements.model_dump()
    data.update({
        "code_ifc": generated_code,
        "user_id": None if section == "admin" else current_user["user_id"]
    })

    if section == "admin":
        if current_user.get("role_id") != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        data["created_status"] = "global"

    # ------------------------------------------------------------------ #
    # 6) Crear y guardar
    # ------------------------------------------------------------------ #
    new_element = Element(**data)
    try:
        db.add(new_element)
        db.commit()
        db.refresh(new_element)

        # -------------------------------------------------------------- #
        # 7) Cálculo extra para puertas
        # -------------------------------------------------------------- #
        if new_element.type == "door" and "porcentaje_vidrio" in new_element.atributs:
            new_element.atributs["porcentaje_vidrio"] /= 100
            flag_modified(new_element, "atributs")

            constant = db.query(Constant).filter(
                Constant.name == "generals",
                Constant.type == "elements"
            ).first()

            rsi_m = constant.atributs["thermal_resistances"]["rsi_wall"]
            rse_m = constant.atributs["thermal_resistances"]["rse_wall"]

            calculate_element_door(rsi_m, rse_m, new_element, db)
            db.commit()

        return {
            "success": "Elemento creado correctamente",
            "element": new_element.model_dump()
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al crear el elemento: {str(e)}")


def get_elements(section: str, type: str, current_user: dict, db: Session):
    """Obtiene los elementos según el rol del usuario y la sección seleccionada, con orden personalizado."""
    if section not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Sección no válida")

    query = db.query(Element).filter(Element.is_deleted == False)

    if type:
        query = query.filter(Element.type == type)

    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        # Solo elementos globales
        query = query.filter(Element.user_id == None)
    else:
        query = query.filter(
            or_(
                Element.user_id == None,
                Element.user_id == current_user["user_id"]
            )
        )

    # Orden personalizado
    query = query.order_by(
        case(
            (Element.created_status == "default", 1),
            (Element.created_status == "global", 2),
            (Element.created_status == "created", 3),
            else_=4
        ).asc(),
        Element.id.asc()
    )

    return query.all()


def get_element_by_id(section: str, element_id: int, current_user: dict, db: Session):
    """Obtiene un elemento por su ID, asegurando permisos según la sección."""
    if section not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Sección no válida")

    query = db.query(Element).filter(
        Element.id == element_id,
        Element.is_deleted == False
    )

    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        query = query.filter(Element.user_id == None)
    else:
        query = query.filter(
            or_(
                Element.user_id == None,
                Element.user_id == current_user["user_id"]
            )
        )

    element = query.first()
    if not element:
        raise HTTPException(status_code=404, detail="Elemento no encontrado")

    return element


def get_project_elements(section: str, type: str, project_id: int, current_user: dict, db: Session):
    """Obtiene los elementos de un proyecto específico."""
    if section not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Sección no válida")

    # Validación del proyecto según la sección
    project_query = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False
    )
    if section == "user":
        project_query = project_query.filter(
            Project.user_id == current_user["user_id"])
    else:
        if current_user["role_id"] != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")

    project = project_query.first()
    if not project:
        raise HTTPException(
            status_code=404, detail="No se encontró el proyecto")

    # Se obtienen los IDs de los elementos utilizados en fórmulas del proyecto
    formula_element_ids = db.query(Formulas.item_id).filter(
        Formulas.project_id == project_id,
        Formulas.type == "elements",
        Formulas.is_deleted == False
    ).scalar_subquery()

    query = db.query(Element).filter(
        Element.id.in_(formula_element_ids),
        Element.is_deleted == False
    )

    if type:
        query = query.filter(Element.type == type)

    if section == "admin":
        query = query.filter(Element.user_id == None)
    else:
        query = query.filter(
            or_(
                Element.user_id == None,
                Element.user_id == current_user["user_id"]
            )
        )

    elements = query.all()
    if not elements:
        raise HTTPException(
            status_code=404, detail="No se encontraron elementos para este proyecto")

    return elements


def update_element(section: str, element_id: int, element_data: ElementBase, current_user: dict, db: Session):
    """
    Actualiza los datos de un elemento.
    - Para "admin": el administrador (role_id==1) puede actualizar cualquier elemento.
    - Para "user": solo puede actualizar sus propios elementos y no se permite actualizar elementos predeterminados.
    """
    if section not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Sección no válida")

    query = db.query(Element).filter(
        Element.id == element_id,
        Element.is_deleted == False
    )

    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        element = query.first()
    else:
        element = query.filter(
            Element.user_id == current_user["user_id"]).first()

    if not element:
        raise HTTPException(status_code=404, detail="Elemento no encontrado")

    if section == "user" and element.created_status == "default":
        raise HTTPException(
            status_code=403,
            detail="No se puede actualizar un elemento predeterminado."
        )

    # Obtención de los nuevos valores a actualizar
    update_data = element_data.model_dump()
    # Si se está actualizando el nombre o el tipo, se debe validar que no exista conflicto
    new_name = update_data.get("name_element", element.name_element)
    new_type = update_data.get("type", element.type)

    # Validación de existencia de nombre para actualización (excluyendo el propio elemento)
    if section == "admin":
        exist_element = db.query(Element).filter(
            Element.id != element_id,
            Element.name_element == new_name,
            Element.type == new_type,
            Element.is_deleted == False,
            Element.user_id == None
        ).first()
    else:  # section == "user"
        exist_element = db.query(Element).filter(
            Element.id != element_id,
            Element.name_element == new_name,
            Element.type == new_type,
            Element.is_deleted == False,
            or_(Element.user_id == None,
                Element.user_id == current_user["user_id"])
        ).first()

    if exist_element:
        raise HTTPException(
            status_code=400,
            detail=f"El nombre del elemento ya existe dentro del tipo {new_type}"
        )

    # Actualización de los atributos del elemento
    for key, value in update_data.items():
        setattr(element, key, value)

    try:
        db.commit()
        db.refresh(element)
        return {"message": "Elemento actualizado correctamente", "element": element}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al actualizar el elemento") from e


def delete_element(section: str, current_user: dict, element_id: int, db: Session):
    """
    Elimina un elemento.
    - Para "admin": el administrador (role_id==1) puede eliminar cualquier elemento.
    - Para "user": solo puede eliminar sus propios elementos y no se permite eliminar elementos predeterminados.
    """
    if section not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Sección no válida")

    query = db.query(Element).filter(
        Element.id == element_id,
        Element.is_deleted == False
    )

    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        element = query.first()
    else:
        element = query.filter(
            Element.user_id == current_user["user_id"]).first()

    if not element:
        raise HTTPException(status_code=404, detail="Elemento no encontrado")

    if section == "user" and element.created_status == "default":
        raise HTTPException(
            status_code=403,
            detail="No se puede eliminar un elemento predeterminado."
        )

    try:
        element.is_deleted = True
        db.commit()
        return {"message": "Elemento eliminado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al eliminar el elemento") from e


def get_element_by_code_ifc(section: str, code_ifc: str,  db: Session):
    query = db.query(Element).filter(
        Element.code_ifc == code_ifc,
        Element.is_deleted == False
    )
    element = query.first()
    if not element:
        raise HTTPException(status_code=404, detail="Elemento no encontrado")
    return element
