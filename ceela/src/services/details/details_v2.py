from typing import List, cast

from fastapi import HTTPException
from sqlalchemy import func, cast, or_
from sqlalchemy.types import Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models.entity.constant import Constant
from src.models.entity.detail_part import DetailPart
from src.models.entity.details import Detail
from src.models.entity.formulas import Formulas
from src.models.entity.project_table import Project
from src.models.schemas.details.detail_part_update import DetailPartCreate
from src.models.schemas.details.details_create import DetailBase
from src.services.calculator.calculation_parameters import (
    calculate_aislacion_bajo_piso, calculate_details_generals, calculate_details_part,
    calculate_km_op_acumulated)


from fastapi import HTTPException
from sqlalchemy import or_

def create_detail_part(
    db: Session,
    detail_create: DetailPartCreate,
    detail_type: str,
    project_id: int,
    current_user: dict,
    section: str
) -> DetailPart:
    """
    Crea un DetailPart y genera un code_ifc único por tipo:
    MURO_XXX, TECHO_XXX o PISO_XXX.
    """

    if section == "admin":
        project_id = None
    else:
        project = db.query(Project).filter(
            Project.user_id == current_user["user_id"],
            Project.id == project_id
        ).first()
        if not project:
            raise HTTPException(404, "Proyecto no encontrado")

    if db.query(DetailPart).filter(
        DetailPart.name_detail == detail_create.name_detail,
        DetailPart.type == detail_type,
        DetailPart.project_id == project_id
    ).first():
        raise HTTPException(400, f"Ya existe un detalle '{detail_create.name_detail}'")

    processed_info = {}
    if detail_type in ("Muro", "Techo"):
        sc = detail_create.info.get("surface_color") or {}
        int_name = sc.get("interior", {}).get("name", "Intermedio")
        ext_name = sc.get("exterior", {}).get("name", "Intermedio")
        consts = db.query(Constant).filter(
            Constant.type == "details",
            Constant.name == "generals"
        ).first()
        colors = consts.atributs.get("surface_color", {}) if consts else {}
        processed_info["surface_color"] = {
            "interior": {"name": int_name, "value": colors.get(int_name, 0.6)},
            "exterior": {"name": ext_name, "value": colors.get(ext_name, 0.6)}
        }
    elif detail_type == "Piso":
        # 1) Extraemos los refs originales (si vienen o usamos diccionarios vacíos)
        rv = detail_create.info.get("ref_aisl_vertical", {})
        rh = detail_create.info.get("ref_aisl_horizontal", {})

        # 2) Calculamos la aislación bajo piso
        lam, e_aisl = calculate_aislacion_bajo_piso(
            project_id,
            detail_create.name_detail,  # o el nombre que uses
            detail_type,
            db
        )
        print(f"Probar v2: {lam} {e_aisl}")
        # 3) Armamos processed_info empezando con lo mínimo
        processed_info = {
            "aislacion_bajo_piso": {"lambda": lam, "e_aisl": e_aisl},
            "ref_aisl_vertical": {
                "d":       rv.get("d"),
                "e_aisl":  rv.get("e_aisl"),
                "lambda":  rv.get("lambda")
            },
            "ref_aisl_horizontal": {
                "d":       rh.get("d"),
                "e_aisl":  rh.get("e_aisl"),
                "lambda":  rh.get("lambda")
            }
        }

        # 4) Fusionamos cualquier otro campo de detail_create.info
        #    (sin pisar las tres claves gestionadas arriba)
        for key, val in detail_create.info.items():
            if key not in processed_info:
                processed_info[key] = val
    else:
        raise HTTPException(400, "Tipo inválido. Debe ser 'Muro', 'Techo' o 'Piso'.")

    data = detail_create.model_dump()
    data["info"] = processed_info

    # Prefijos por tipo
    type_prefix_map = {
        "Muro": "MURO",
        "Techo": "TECHO",
        "Piso": "PISO"
    }

    prefix = type_prefix_map.get(detail_type)
    rows = db.query(DetailPart.code_ifc).filter(
        DetailPart.code_ifc.like(f"{prefix}_%")
    ).all()

    nums = []
    for (code_ifc,) in rows:
        partes = code_ifc.split("_")
        if len(partes) == 2 and partes[1].isdigit():
            nums.append(int(partes[1]))

    next_num = max(nums) + 1 if nums else 1
    data["code_ifc"] = f"{prefix}_{next_num:03d}"

    detail = DetailPart(
        **data,
        project_id=project_id,
        type=detail_type
    )
    try:
        db.add(detail)
        db.commit()
        db.refresh(detail)
        return detail

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error al crear el detalle: {e}")



def get_detail_part_by_id(
    db: Session,
    detail_id: str,
    current_user: dict,
    section: str
) -> DetailPart:
    """
    Obtiene un registro de DetailPart por su ID, validando según la sección y el rol del usuario:
      - Para la sección "user":
            - Se requiere project_id.
            - Se valida que el proyecto exista y que pertenezca al current_user.
            - Se busca el detalle asociado al project_id indicado.
      - Para la sección "admin":
            - Si current_user["role_id"] == 1, se omiten restricciones adicionales y se busca el detalle por su ID.
            - En caso contrario, se busca el detalle global (project_id == None).

    Parámetros:
      - db: Sesión de la base de datos (SQLModel Session).
      - detail_id: ID del registro de DetailPart a obtener.
      - project_id: ID del proyecto (obligatorio para usuarios).
      - current_user: Diccionario con los datos del usuario actual (para validar propiedad del proyecto).
      - section: Cadena que indica la sección ("user" o "admin").

    Retorna:
      - La instancia de DetailPart obtenida.

    Lanza HTTPException si:
      - La sección no es válida.
      - No se encuentra el proyecto (para la sección "user").
      - No se encuentra el detalle.
    """
    if section not in ["user", "admin"]:
        raise HTTPException(
            status_code=400, detail="Sección inválida. Use 'user' o 'admin'.")

    # Si la sección es "user", se valida la existencia del proyecto y la propiedad.
    if section == "user":
        project = db.query(Project).filter(
            Project.user_id == current_user["user_id"]
        ).first()
        if not project:
            raise HTTPException(
                status_code=404, detail="Proyecto no encontrado.")

        detail = db.query(DetailPart).filter(
            DetailPart.id == detail_id
        ).first()

    else:  # section == "admin"
        # Si el rol del usuario es 1, no se aplican restricciones para obtener el detalle.
        if current_user.get("role_id") == 1:
            detail = db.query(DetailPart).filter(
                DetailPart.id == detail_id
            ).first()
        else:
            # De lo contrario, se asume que se buscan detalles globales (project_id == None).
            detail = db.query(DetailPart).filter(
                DetailPart.id == detail_id,
                DetailPart.project_id.is_(None)
            ).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Detalle no encontrado.")

    return detail


def create_detail_v2(
    detail: DetailBase,
    current_user: dict,
    db: Session,
    section: str,
    detail_part_id: int
):
    """
    Crea un nuevo detalle en la base de datos y, además, inserta un registro en la tabla Formulas.

    Para la sección "user":
      - Se requiere project_id.
      - El detalle se asigna al proyecto indicado.
      - El registro en Formulas tendrá ese project_id.
      - Se ejecutan funciones adicionales de recálculo (posición de aislamiento y parte de detalles).

    Para la sección "admin":
      - Se crea el detalle sin vincularlo a ningún proyecto (project_id se asigna como None).
      - Se crea también el registro en Formulas, conservando el type y el name_detail, pero con project_id == None.
      - Se ejecuta el cálculo general (calculate_details_generals).

    Parameters:
        detail: DetailBase
            Datos del detalle a crear.
        current_user: dict
            Datos del usuario actual.
        db: Session
            Sesión de la base de datos.
        section: str
            Indica si la operación es para "user" o "admin".
        project_id: Optional[int]
            ID del proyecto (requerido si section == "user").

    Returns:
        dict: Resultado de la operación, que incluye el detalle creado y el registro en Formulas.
    """
    # Validar que la sección sea válida
    if section not in ["user", "admin"]:
        return {"error": "Sección inválida. Use 'user' o 'admin'."}

    # 0) Cargar DetailPart
    detail_part = db.query(DetailPart).filter(DetailPart.id == detail_part_id).first()
    if not detail_part:
        raise HTTPException(status_code=404, detail="DetailPart no encontrado")

    # 1) Forzar coherencia de (name_detail, scantilon) desde DetailPart
    detail.name_detail = detail_part.name_detail
    detail.scantilon_location = detail_part.type

    # 2) Armar payload del nuevo Detail
    detail_data = {
        "scantilon_location": detail.scantilon_location,
        "name_detail": detail.name_detail,
        "material_id": detail.material_id,
        "layer_thickness": detail.layer_thickness,
        "detail_part_id": detail_part_id,
    }

    if section == "user":
        if detail_part.project_id is None:
            return {"error": "Para la sección 'user' se requiere un project_id en el DetailPart"}
        detail_data["project_id"] = detail_part.project_id
    else:  # admin
        detail_data["project_id"] = None
        # Ojo: solo añade created_status si existe esa columna en tu modelo
        # detail_data["created_status"] = "global"

    # 3) Crear Detail
    try:
        new_detail = Detail(**detail_data)
        db.add(new_detail)
        db.commit()
        db.refresh(new_detail)
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    # 4) Crear/actualizar Calculation (details/generals) para que exista km_op
    try:
        calc_project = detail_part.project_id if section == "user" else None
        calculate_details_generals(new_detail.id, db, calc_project)
    except HTTPException as e:
        db.rollback()
        return {"error": f"Error al calcular generales: {e.detail}"}
    except Exception as e:
        db.rollback()
        return {"error": f"Error inesperado al calcular generales: {str(e)}"}

    # 5) Recalcular km_op_acumulated ya con el Calculation creado
    try:
        km_op_acumulated = calculate_km_op_acumulated(
            db=db,
            detail=new_detail,  # usa el Detail real creado
            project_id=detail_part.project_id if section == "user" else None
        )
    except Exception as e:
        db.rollback()
        return {"error": f"Error al calcular km_op_acumulated: {str(e)}"}

    # 6) Crear Formulas con km_op_acumulated correcto
    detail_atributs = {
        "scantilon_location": new_detail.scantilon_location,
        "name_detail": new_detail.name_detail,
        "material_id": new_detail.material_id,
        "layer_thickness": new_detail.layer_thickness,
        "position_insulation": 0,
        "km_op_acumulated": km_op_acumulated,
    }
    formula_project_id = detail_part.project_id if section == "user" else None

    try:
        new_formula = Formulas(
            project_id=formula_project_id,
            item_id=new_detail.id,
            type="details",
            name=new_detail.name_detail,
            atributs=detail_atributs,
            is_deleted=False,
        )
        db.add(new_formula)
        db.commit()
        db.refresh(new_formula)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear fórmula: {str(e)}")

    # 7) Recalcular agregados del DetailPart / posición de aislación
    calculate_details_part(db, section, project_id=detail_part.project_id)

    # 8) Serializar Detail sin model_dump (SQLAlchemy)
    detail_dict = {c.name: getattr(new_detail, c.name) for c in new_detail.__table__.columns}

    return {
        "success": "Detalle y fórmula creados",
        "detail": detail_dict
    }

def update_detail(
    detail_id: int,
    updated_data: DetailBase,
    current_user: dict,
    db: Session,
    section: str,           # "admin" o "user"
):
    """
    Actualiza un detalle y recalcula los valores en todos los proyectos relacionados.

    - En modo "admin": se permite actualizar detalles globales.
      Se requiere que current_user sea administrador (por ejemplo, role_id != 2) y se usará el project_id pasado.
    - En modo "user": se permite actualizar solo los detalles propios, es decir, aquellos cuyo project_id es None.
      En este caso, si el detalle tiene un project_id (global), se rechaza la operación.
    """
    detail = db.query(Detail).filter(
        Detail.id == detail_id,
        Detail.is_deleted == False
    ).first()

    project_id = detail.project_id

    if not detail:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado"
        )

    name_detail_if_update = detail.name_detail
    scantilon_if_update = detail.scantilon_location

    if section == "admin":
        # Solo administradores pueden usar la sección admin
        if current_user["role_id"] == 2:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para editar detalles globales"
            )
        # Para modo admin, se puede esperar que project_id sea proporcionado (para cálculos, si es necesario)
    elif section == "user":
        # El usuario solo puede editar sus propios detalles; se asume que los detalles propios tienen project_id == None
        if detail.project_id == None:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para editar detalles globales"
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="El parámetro section debe ser 'admin' o 'user'."
        )

    my_detail = detail.model_dump()
    # Actualizar los atributos del detalle
    for key, value in updated_data.model_dump().items():
        setattr(detail, key, value)

    try:
        db.commit()
        db.refresh(detail)

        # Definir el project_id para la recalculación:
        # En modo admin se utiliza el project_id pasado; en modo user se usa None (ya que es detalle propio)

        # Actualizar el registro en Formulas asociado a este detalle usando la misma sesión
        formula = db.query(Formulas).filter(
            Formulas.item_id == detail.id,
            Formulas.type == "details",
            Formulas.is_deleted == False
        ).first()
        if formula:
            # Se asigna project_id dependiendo de la sección
            formula.project_id = project_id if section == "user" else None
            # Se actualiza el name de la fórmula con el name_detail actualizado
            formula.name = detail.name_detail
            print("DETALLE: ", detail)
            # Calcular km_op_acumulated usando el detalle actualizado
            km_op_acumulated_value = calculate_km_op_acumulated(
                db, detail, project_id)
            print("HOLA: ", km_op_acumulated_value)
            # Se actualizan los atributos; se recalcula "km_op_acumulated" y se asigna el valor de "position_insulation"
            formula.atributs = {
                "scantilon_location": detail.scantilon_location,
                "name_detail": detail.name_detail,
                "material_id": detail.material_id,
                "layer_thickness": detail.layer_thickness,
                "km_op_acumulated": km_op_acumulated_value,
                "position_insulation": 0  # o el valor que corresponda según la lógica del negocio
            }

        print("ProjectID: ", project_id)
        # Ejecutar cálculos generales y parciales usando el detalle actualizado
        calculate_details_generals(detail.id, db, project_id)
        calculate_details_part(db, section, project_id,
                               detail.id, name_detail_if_update, scantilon_if_update)
        db.commit()

        return {"success": "Detalle actualizado", "detail": my_detail}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error en la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar detalle: {str(e)}"
        )


def get_details_by_detail_part(
    db: Session,
    detail_part_id: int,
    current_user: dict,
) -> list:
    """
    Obtiene todos los hijos (Detail) asociados a un DetailPart específico.

    Realiza una búsqueda de registros donde Detail.detail_part_id coincide con el parámetro recibido.
    Los resultados se ordenan de la siguiente manera:
      - Primero los detalles con created_status == "default".
      - Luego los detalles con created_status == "global".
      - Finalmente, el resto, ordenados ascendentemente por id.

    Parámetros:
      - db: Sesión de base de datos.
      - detail_part_id: ID del DetailPart padre.
      - current_user: Diccionario con info del usuario actual.

    Retorna:
      - Una lista de diccionarios, donde cada diccionario representa un Detail 
        enriquecido con el campo "material" (nombre del material).

    Lanza HTTPException si:
      - No se encuentra el DetailPart.
      - No se hallan detalles hijos.
    """
    # Obtener el DetailPart
    detail_part = db.query(DetailPart).filter(DetailPart.id == detail_part_id).first()
    if not detail_part:
        raise HTTPException(status_code=404, detail="Detalle padre no encontrado.")

    # Búsqueda: registros cuyo detail_part_id coincide
    details = (
        db.query(Detail)
        .filter(Detail.detail_part_id == detail_part_id)
        .order_by(Detail.id.asc())
        .all()
    )

    # Función para asignar una prioridad para el ordenamiento
    def sort_key(detail: Detail):
        # Determina el ranking:
        # 0 => "default", 1 => "global", 2 => otros
        if getattr(detail, "created_status", None) == "default":
            rank = 0
        elif getattr(detail, "created_status", None) == "global":
            rank = 1
        else:
            rank = 2
        return (rank, detail.id)

    # Ordenar los detalles usando la prioridad y luego por id ascendente
    sorted_details = sorted(details, key=sort_key)

    # Construir la lista de resultados enriquecidos con el nombre del material
    result_list = []
    for detail in sorted_details:
        material_name = db.query(Constant.atributs['name']).filter(
            Constant.id == detail.material_id
        ).scalar()
        result_list.append({
            **detail.model_dump(),
            "material": material_name
        })

    return result_list

def get_detail_part_by_name(
    db: Session,
    name: str,
    current_user: dict,
    section: str,
    project_id: int = None
) -> DetailPart:
    """
    Obtiene un registro de DetailPart por su nombre, validando según la sección y el rol del usuario:
      - Para la sección "user":
            - Se valida que el proyecto exista y que pertenezca al current_user.
            - Se busca el detalle asociado al project_id indicado.
      - Para la sección "admin":
            - Si current_user["role_id"] == 1, se omiten restricciones adicionales y se busca el detalle por su nombre.
            - En caso contrario, se busca el detalle global (project_id == None).

    Parámetros:
      - db: Sesión de la base de datos (SQLModel Session).
      - name: Nombre del registro de DetailPart a obtener.
      - current_user: Diccionario con los datos del usuario actual (para validar propiedad del proyecto).
      - section: Cadena que indica la sección ("user" o "admin").
      - project_id: ID del proyecto (opcional).

    Retorna:
      - La instancia de DetailPart obtenida.

    Lanza HTTPException si:
      - La sección no es válida.
      - No se encuentra el proyecto (para la sección "user").
      - No se encuentra el detalle.
    """
    if section not in ["user", "admin"]:
        raise HTTPException(
            status_code=400, detail="Sección inválida. Use 'user' o 'admin'.")

    # Si la sección es "user", se valida la existencia del proyecto y la propiedad.
    if section == "user":
        # Si se proporciona project_id, lo usamos directamente
        if project_id is not None:
            # Verificar que el proyecto pertenezca al usuario
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == current_user["user_id"]
            ).first()
            if not project:
                raise HTTPException(
                    status_code=404, detail="Proyecto no encontrado o no tienes acceso a él.")
        else:
            # Si no se proporciona project_id, buscamos cualquier proyecto del usuario
            project = db.query(Project).filter(
                Project.user_id == current_user["user_id"]
            ).first()
            if not project:
                raise HTTPException(
                    status_code=404, detail="Proyecto no encontrado.")

        # Construir la consulta base
        query = db.query(DetailPart).filter(DetailPart.name_detail == name)

        # Si se proporciona project_id, filtrar por ese proyecto
        if project_id is not None:
            query = query.filter(DetailPart.project_id == project_id)

        detail = query.first()

    else:  # section == "admin"
        # Si el rol del usuario es 1, no se aplican restricciones para obtener el detalle.
        if current_user.get("role_id") == 1:
            # Construir la consulta base
            query = db.query(DetailPart).filter(DetailPart.name_detail == name)

            # Si se proporciona project_id, filtrar por ese proyecto
            if project_id is not None:
                query = query.filter(DetailPart.project_id == project_id)

            detail = query.first()
        else:
            # De lo contrario, se asume que se buscan detalles globales (project_id == None).
            detail = db.query(DetailPart).filter(
                DetailPart.name_detail == name,
                DetailPart.project_id.is_(None)
            ).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Detalle no encontrado.")

    return detail


def delete_details(id: int, is_layer: bool, db: Session, current_user: dict):
    try:
        if is_layer:
            detail = db.query(DetailPart).filter(DetailPart.id == id).first()
            if not detail:
                raise HTTPException(status_code=400, detail="Detalle no encontrado")

            # Eliminar detalles hijos
            db.query(Detail).filter(Detail.detail_part_id == detail.id).delete()
            # Eliminar fórmulas relacionadas
            db.query(Formulas).filter(
                Formulas.name == detail.name_detail,
                Formulas.project_id == detail.project_id,
                Formulas.type == "details"
            ).delete()
            db.delete(detail)

        else:
            detail = db.query(Detail).filter(Detail.id == id).first()
            if not detail:
                raise HTTPException(status_code=400, detail="Capa no encontrada")

            # Eliminar fórmulas relacionadas
            db.query(Formulas).filter(
                Formulas.item_id == detail.id,
                Formulas.type == "details"
            ).delete()
            db.delete(detail)

            # Determinar sección para recálculo
            section = "user" if current_user["role_id"] == 2 else "admin"

        db.commit()

        if not is_layer:
            calculate_details_part(db, section, detail.project_id, id, detail.name_detail, detail.scantilon_location)

        return {"deleted": True, "id": id}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar el detalle: {str(e)}")
