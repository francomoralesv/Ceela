from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import exists, select, case

from src.decorators import cache
from src.models.constant_base import ConstantBase
from src.models.entity.constant import Constant
from src.models.entity.formulas import Formulas
from src.models.entity.project_table import Project
from src.services.calculator.calculation_parameters import calculate_details_part, recalculate_position_insulation

from sqlalchemy import or_, func
from fastapi import HTTPException


def create_constant(section: str, current_user: dict, constant: ConstantBase, db: Session):
    """Crea una constante con código único (campo code_ifc) prefijado 'mat_'."""
    if section not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Sección no válida")

    new_name = str(constant.atributs["name"])

    # 1. Verificar duplicados por nombre
    filtros = [
        Constant.atributs["name"].astext == new_name,
        Constant.is_deleted.is_(False),
        Constant.type == "definition materials",
    ]
    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        filtros.append(Constant.user_id.is_(None))
    else:
        filtros.append(
            or_(
                Constant.user_id.is_(None),
                Constant.user_id == current_user["user_id"]
            )
        )
    if db.query(Constant).filter(*filtros).first():
        raise HTTPException(status_code=400, detail="El material ya existe")

    # 2. Generar código único en code_ifc
    #    Usamos raw string para no tener invalid escape sequence
    patrones = db.query(Constant.code_ifc).filter(
        Constant.type == "definition materials",
        or_(
            Constant.code_ifc.like(r"MATERIAL\_%"),
            Constant.code_ifc.like(r"mat\_%"),
        )
    ).all()
    nums = []
    for (code,) in patrones:
        partes = (code or "").split("_")
        if len(partes) == 2 and partes[1].isdigit():
            nums.append(int(partes[1]))
    siguiente = max(nums) + 1 if nums else 1
    generated_code = f"MATERIAL_{siguiente:03d}"

    # 3. Construir el nuevo Constant
    data = constant.model_dump()
    data.update({
        "code_ifc": generated_code,
        "type": "definition materials",
        "user_id": None if section == "admin" else current_user["user_id"]
    })
    if section == "admin":
        data["create_status"] = "global"

    new_constant = Constant(**data)

    # 4. Guardar en BD
    try:
        db.add(new_constant)
        db.commit()
        db.refresh(new_constant)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al crear material") from e

    return new_constant


@cache.sync_cache(300)
def get_constants(section: str, current_user: dict, db: Session, name: str = None, type: str = None, page: int = 1, per_page: int = 10):
    """Obtiene constantes con filtros opcionales y paginación.
       - Para "admin": se obtienen sólo las constantes globales (user_id == None).
       - Para "user": se obtienen las constantes globales o las propias.
       - Se ordena por created_status (default > global > created) y luego por id ascendente.
    """
    if section not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Sección no válida")

    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        query = db.query(Constant).filter(
            Constant.user_id == None,
            Constant.is_deleted == False,
            Constant.type == "definition materials"
        )
    else:
        query = db.query(Constant).filter(
            or_(
                Constant.user_id == None,
                Constant.user_id == current_user["user_id"]
            ),
            Constant.is_deleted == False,
            Constant.type == "definition materials"
        )

    if name:
        query = query.filter(Constant.name.ilike(f"%{name}%"))
    if type:
        query = query.filter(Constant.type.ilike(f"%{type}%"))

    # Orden personalizado: primero "default", luego "global", luego "created", y finalmente ordenado por id ascendente
    query = query.order_by(
        case(
            (Constant.create_status == "default", 1),
            (Constant.create_status == "global", 2),
            (Constant.create_status == "created", 3),
            else_=4
        ).asc(),
        Constant.id.asc()
    )

    total_constants = query.count()
    total_pages = (total_constants + per_page - 1) // per_page
    if page < 1 or (total_pages > 0 and page > total_pages):
        raise HTTPException(status_code=404, detail="Página fuera de rango")

    offset = (page - 1) * per_page
    constants = query.offset(offset).limit(per_page).all()

    if not constants:
        raise HTTPException(
            status_code=404, detail="No se encontraron materiales con los criterios especificados")

    return {
        "constants": constants,
        "total_constants": total_constants,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@cache.sync_cache(300)
def get_constant(db: Session, name: str = None, type: str = None):
    """Gets constants with optional filters without pagination.
       Returns both global constants and user-specific ones.
    """
    try:
        print(f"[INFO] Buscando constantes con nombre: {name} y tipo: {type}")
        query = db.query(Constant).filter(
            Constant.is_deleted == False
        )

        if name:
            query = query.filter(Constant.name.like(f"%{name}%"))
        if type:
            query = query.filter(Constant.type.like(f"%{type}%"))

        # Use a simpler query to avoid potential database issues
        if name and type:
            # Exact match for both name and type
            constant = query.filter(
                Constant.name == name,
                Constant.type == type
            ).first()

            if not constant:
                # Try with like operator if exact match fails
                constant = query.filter(
                    Constant.name.like(f"%{name}%"),
                    Constant.type.like(f"%{type}%")
                ).first()
        else:
            constant = query.order_by(
                case(
                    (Constant.create_status == "default", 1),
                    (Constant.create_status == "global", 2),
                    (Constant.create_status == "created", 3),
                    else_=4
                ).asc(),
                Constant.id.asc()
            ).first()

        if not constant:
            raise HTTPException(
                status_code=404, detail="No materials found with the specified criteria")

        return constant
    except Exception as e:
        # If there's any database error, log and re-raise
        print(f"[ERROR] Error getting constant: {str(e)}")
        raise


def get_project_constants(section: str, current_user: dict, project_id: int, db: Session):
    """Obtiene las constantes de un proyecto.
       - Para "admin": se muestran todas las constantes usadas en el proyecto.
       - Para "user": se muestran solo las que sean globales o propias.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Se obtienen los IDs de las constantes utilizadas en fórmulas del proyecto
    formula_constants_ids = db.query(Formulas.item_id).filter(
        Formulas.project_id == project_id,
        Formulas.type == "materials",
        Formulas.is_deleted == False
    ).subquery()

    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        constants = db.query(Constant).filter(
            Constant.id.in_(formula_constants_ids),
            Constant.is_deleted == False,
            Constant.type == "definition materials"
        ).all()
    else:
        constants = db.query(Constant).filter(
            Constant.id.in_(formula_constants_ids),
            or_(
                Constant.user_id == None,
                Constant.user_id == current_user["user_id"]
            ),
            Constant.is_deleted == False,
            Constant.type == "definition materials"
        ).all()

    if not constants:
        raise HTTPException(
            status_code=404, detail="No se encontraron constantes para este proyecto")

    return constants


@cache.sync_cache(300)
def get_constant_by_id(section: str, current_user: dict, constant_id: int, db: Session):
    """Obtiene una constante por su ID según la sección.
       - Para "admin": se buscan las constantes globales (user_id == None).
       - Para "user": se buscan las constantes globales o propias.
    """
    if section not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Sección no válida")

    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        constant = db.query(Constant).filter(
            Constant.id == constant_id,
            Constant.user_id == None,
            Constant.is_deleted == False,
            Constant.type == "definition materials"
        ).first()
    else:
        constant = db.query(Constant).filter(
            Constant.id == constant_id,
            Constant.is_deleted == False,
            or_(
                Constant.user_id == None,
                Constant.user_id == current_user["user_id"]
            ),
            Constant.type == "definition materials"
        ).first()

    if not constant:
        raise HTTPException(status_code=404, detail="Material no encontrada")

    return constant


def update_constant(section: str, current_user: dict, constant_id: int, updated_constant: ConstantBase, db: Session):
    """Actualiza una constante según la sección:
       - Para "admin": el administrador puede editar cualquier constante.
       - Para "user": solo puede editar sus propias constantes y no las de tipo default.
       Además, se verifica que el nuevo nombre (tomado de updated_constant.atributs["name"]) no se repita en otro material.
       Si el nombre enviado es el mismo que el actual, se permite la actualización.
    """
    print(
        f"[INFO] Iniciando actualización de constante (id: {constant_id}, sección: {section})")

    if section not in ["user", "admin"]:
        print(f"[ERROR] Sección no válida: {section}")
        raise HTTPException(status_code=400, detail="Sección no válida")

    # Obtener la constante según el rol del usuario.
    if section == "admin":
        if current_user.get("role_id") != 1:
            print(
                f"[ERROR] Acceso denegado para usuario sin permisos de admin: {current_user}")
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        constant = db.query(Constant).filter(
            Constant.id == constant_id,
            Constant.is_deleted == False,
            Constant.user_id == None,
            Constant.type == "definition materials"
        ).first()
    else:
        constant = db.query(Constant).filter(
            Constant.id == constant_id,
            or_(
                Constant.user_id == None,
                Constant.user_id == current_user.get("user_id")
            ),
            Constant.is_deleted == False,
            Constant.type == "definition materials"
        ).first()

    if not constant:
        print(f"[ERROR] Material no encontrado para id: {constant_id}")
        raise HTTPException(status_code=404, detail="Material no encontrado")

    if section == "user" and constant.create_status == "default":
        print(
            f"[ERROR] Intento de actualizar material por defecto para usuario: {current_user.get('user_id')}")
        raise HTTPException(
            status_code=400, detail="No se puede actualizar un material por defecto")

    # Extraer el nuevo nombre desde updated_constant.atributs["name"]
    updated_data = updated_constant.model_dump()
    new_atributs = updated_data.get("atributs", {})
    new_name = new_atributs.get("name")
    current_name = constant.atributs.get("name") if constant.atributs else None
    print(
        f"[INFO] Nuevo nombre recibido: '{new_name}' - nombre actual: '{current_name}'")

    # Si se cambia el nombre, se verifica la existencia de otros registros con el mismo nombre

    if section == "admin":
        query = db.query(exists().where(
            Constant.atributs["name"].astext == new_name,
            Constant.user_id == None,
            Constant.is_deleted == False,
            Constant.type == "definition materials",
            Constant.id != constant_id
        ))
    else:
        query = db.query(exists().where(
            Constant.atributs["name"].astext == new_name,
            Constant.is_deleted == False,
            Constant.type == "definition materials",
            or_(
                Constant.user_id == None,
                Constant.user_id == current_user.get("user_id")
            ),
            Constant.id != constant_id
        ))

    if query.scalar():
        print(f"[ERROR] El material con el nombre '{new_name}' ya existe")
        raise HTTPException(status_code=400, detail="El material ya existe")

    # Actualizar los campos de la constante
    for key, value in updated_data.items():
        print(f"[INFO] Actualizando campo '{key}' a '{value}'")
        setattr(constant, key, value)

    try:
        db.commit()
        db.refresh(constant)
        print(
            f"[INFO] Actualización completada para el material con id: {constant_id}")
    except Exception as e:
        db.rollback()
        print(
            f"[ERROR] Error al actualizar la constante con id: {constant_id}. Detalle: {e}")
        raise HTTPException(
            status_code=500, detail="Error al actualizar constante") from e


def update_energy_systems_consumos_por_fuente_de_energia(
    db: Session,
    consumos_por_fuente_de_energia: list,
    current_user: dict = None
):
    """
    Actualiza solo el campo 'consumos_por_fuente_de_energia' en la constante de tipo 'energy_systems' con nombre 'general'.
    
    Args:
        db: Sesión de base de datos
        consumos_por_fuente_de_energia: Diccionario con los nuevos valores de consumos por fuente de energía
        current_user: Usuario actual (opcional, para logging)
    
    Returns:
        La constante actualizada
    """
    if current_user:
        print(f"[INFO] Usuario {current_user.get('user_id')} actualizando consumos_por_fuente_de_energia")
    
    # Obtener la constante de sistemas de energía
    constant = db.query(Constant).filter_by(
        type="energy_systems",
        name="general",
        is_deleted=False
    ).first()
    
    if not constant:
        print("[ERROR] No se encontró la constante de sistemas de energía")
        raise HTTPException(status_code=404, detail="Constante de sistemas de energía no encontrada")
    
    if not constant.atributs:
        constant.atributs = {}
    old_value = constant.atributs.get('consumos_por_fuente_de_energia')
    atributs_copy = dict(constant.atributs or {})
    atributs_copy['consumos_por_fuente_de_energia'] = consumos_por_fuente_de_energia
    constant.atributs = atributs_copy
    try:
        db.commit()
        db.refresh(constant)

        return constant
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error al actualizar consumos_por_fuente_de_energia: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error al actualizar los consumos por fuente de energía"
        ) from e

    return constant


def delete_constant(section: str, current_user: dict, constant_id: int, db: Session):
    """Elimina una constante según la sección:
       - Para "admin": se permite eliminar cualquier constante.
       - Para "user": solo se permite eliminar sus propias constantes y no las de tipo default.
    """
    if section not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Sección no válida")

    if section == "admin":
        if current_user["role_id"] != 1:
            raise HTTPException(
                status_code=403, detail="Acceso denegado para usuarios normales")
        constant = db.query(Constant).filter(
            Constant.id == constant_id,
            Constant.is_deleted == False,
            Constant.type == "definition materials"
        ).first()
    else:
        constant = db.query(Constant).filter(
            Constant.id == constant_id,
            or_(
                Constant.user_id == None,
                Constant.user_id == current_user["user_id"]
            ),
            Constant.is_deleted == False,
            Constant.type == "definition materials"
        ).first()

    if not constant:
        raise HTTPException(
            status_code=404, detail="Material no encontrada o ya eliminada")

    if section == "user" and constant.create_status == "default":
        raise HTTPException(
            status_code=400, detail="No se puede eliminar un material por defecto")

    try:
        constant.is_deleted = True
        db.commit()
        return {"message": "Material eliminada exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al eliminar constante") from e


def delete_parameter_in_project(project_id: int, reference_id: int, type: str, current_user: dict, db: Session):
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == current_user["user_id"]).first()
    if not project:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para modificar este proyecto")

    formula = db.query(Formulas).filter(
        Formulas.project_id == project_id,
        Formulas.item_id == reference_id,
        Formulas.type == type
    ).first()

    if not formula:
        raise HTTPException(status_code=404, detail="Objeto no encontrado")

    try:
        db.delete(formula)
        db.commit()

        if type == "details":
            constant = db.query(Constant).filter(
                Constant.name == "generals",
                Constant.type == "details"
            ).first()

            limit_cp_bordes = constant.atributs.get(
                "light_for_edge_layer", 0.0) if constant else 0.0

            calculate_details_part(project_id, db)

        return {"message": "Objeto eliminado correctamente"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar objeto: {str(e)}")


def get_material_by_code_ifc(
    current_user: dict,
    db: Session,
    code_ifc: str
):
    """Obtiene un material por su code_if único.
       - Usuarios normales: pueden ver constantes propias o globales.
       - Admin (role_id == 1): solo ve constantes globales.
    """
    if not code_ifc:
        raise HTTPException(
            status_code=400, detail="Debe proporcionar un code_if válido")

    if current_user["role_id"] == 1:
        # Admin solo puede ver constantes globales
        constant = db.query(Constant).filter(
            Constant.user_id == None,
            Constant.is_deleted == False,
            Constant.type == "definition materials",
            Constant.code_ifc == code_ifc
        ).first()
    else:
        # Usuario común: propias o globales
        constant = db.query(Constant).filter(
            or_(
                Constant.user_id == None,
                Constant.user_id == current_user["user_id"]
            ),
            Constant.is_deleted == False,
            Constant.type == "definition materials",
            Constant.code_ifc == code_ifc
        ).first()

    if not constant:
        raise HTTPException(
            status_code=404, detail="No se encontró un material con ese code_if")

    return constant
