from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_, insert, select, literal, case
from sqlalchemy.orm.attributes import flag_modified
from src.models.entity.constant import Constant
from src.models.entity.details import Detail
from src.models.detail_base import DetailBase
from src.models.entity.formulas import Formulas
from src.models.entity.detail_part import DetailPart
from src.models.entity.project_table import Project
from src.models.schemas.details.detail_part_update import DetailPartUpdate
from src.services.calculator.calculation_parameters import calculate_details_part, calculate_details_generals, delete_calculations_for_detail, recalculate_position_insulation, calculate_km_op_acumulated


def clone_global_details_optimized(project_id: int, db: Session):
    stmt = insert(DetailPart).from_select(
        [
            "project_id",
            "type",
            "name_detail",
            "value_u",
            "calculations",
            "info",
            "created_status",
            "code_ifc"
        ],
        select(
            literal(project_id),         # Se asignafdsf el nuevo projfdsfdfdect_id
            DetailPart.type,
            DetailPart.name_detail,
            DetailPart.value_u,
            DetailPart.calculations,
            DetailPart.info,
            literal("default"),
            DetailPart.code_ifc
        ).where(DetailPart.project_id.is_(None))
    )
    
    db.execute(stmt)
    db.commit()



def clone_default_details_optimized(project_id: int, db: Session):
    """
    Clona los detalles (Detail) globales (project_id=None) al proyecto dado,
    y enlaza cada detalle con el nuevo ID de DetailPart clonado que tenga el mismo name_detail.
    También clona los registros correspondientes en la tabla Formulas.
    """
    # 1. Obtener un dict con {name_detail: id} de DetailPart nuevos clonados con project_id = X
    detail_part_subq = (
        select(DetailPart.name_detail, DetailPart.id)
        .where(DetailPart.project_id == project_id)
        .subquery()
    )

    # 2. Seleccionar los Detail globales (project_id is NULL), unir con DetailPart clonados
    select_stmt = (
        select(
            Detail.scantilon_location,
            Detail.name_detail,
            Detail.material_id,
            Detail.layer_thickness,
            literal("default"),
            literal(project_id),
            detail_part_subq.c.id  # nuevo detail_part_id
        )
        .join(
            detail_part_subq,
            detail_part_subq.c.name_detail == Detail.name_detail
        )
        .where(Detail.project_id.is_(None))
    )

    # 3. Insertar en tabla Detail con los campos necesarios
    stmt = insert(Detail).from_select(
        [
            "scantilon_location",
            "name_detail",
            "material_id",
            "layer_thickness",
            "created_status",
            "project_id",
            "detail_part_id"
        ],
        select_stmt
    )

    # Ejecutar la inserción de Details y obtener los nuevos registros
    db.execute(stmt)
    
    # 4. Obtener los detalles recién insertados
    new_details = db.query(Detail).filter(Detail.project_id == project_id).all()
    
    # 5. Clonar los registros en Formulas
    for detail in new_details:
        formula_data = {
            "type": "details",
            "name": detail.name_detail,
            "item_id": detail.id,
            "project_id": project_id,
            "is_deleted": False,
            "atributs": {
                "scantilon_location": detail.scantilon_location,
                "name_detail": detail.name_detail,
                "material_id": detail.material_id,
                "layer_thickness": detail.layer_thickness,
                "km_op_acumulated": calculate_km_op_acumulated(db, detail, project_id),
                "position_insulation": 0  # Valor por defecto
            }
        }
        
        formula = Formulas(**formula_data)
        db.add(formula)
        
        # Calcular datos generales para cada detalle
        calculate_details_generals(detail.id, db, project_id)

    db.commit()



def create_detail_v2(
    detail: DetailBase,
    current_user: dict,
    db: Session,
    section: str,
    project_id: int
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

    # Armar los datos del detalle
    detail_data = {
        "scantilon_location": detail.scantilon_location,
        "name_detail": detail.name_detail,
        "material_id": detail.material_id,
        "layer_thickness": detail.layer_thickness,
    }
    
    if section == "user":
        if project_id is None:
            return {"error": "Para la sección 'user' se requiere un project_id"}
        detail_data["project_id"] = project_id
    else:  # section == "admin"
        detail_data["created_status"] = "global"
        detail_data["project_id"] = None

    new_detail = Detail(**detail_data)

    try:
        db.add(new_detail)
        db.commit()
        db.refresh(new_detail)
        
        my_detail = new_detail.model_dump()
        # Ejecutar cálculo general asociado al detalle (se ejecuta en ambas secciones)
        if section == "user":
            calculate_details_generals(new_detail.id, db, project_id)
        elif section == "admin":
            calculate_details_generals(new_detail.id, db, project_id)
            
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    # Preparar los atributos para la entrada en Formulas
    detail_atributs = {
        "scantilon_location": new_detail.scantilon_location,
        "name_detail": new_detail.name_detail,
        "material_id": new_detail.material_id,
        "layer_thickness": new_detail.layer_thickness,
        "position_insulation": 0,
        
    }
    
    # En caso de que la sección sea "user", usamos el project_id recibido;
    # para "admin" se asigna None.
    formula_project_id = project_id if section == "user" else None

    try:
        new_formula = Formulas(
            project_id=formula_project_id,
            item_id=new_detail.id,
            type="details",  # Se conserva el type
            name=new_detail.name_detail,  # Se conserva el name_detail
            atributs=detail_atributs,
            is_deleted=False
        )
        db.add(new_formula)
        db.commit()
        db.refresh(new_formula)
        
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear fórmula: {str(e)}")

    
    limit_cp_bordes = (
        db.query(Constant.atributs["light_for_edge_layer"].as_float())
            .filter(Constant.name == "generals", Constant.type == "details")
            .scalar() or 0.0
    )
    
    calculate_details_part(db, section, project_id=project_id)
    
    return {
        "success": "Detalle y fórmula creados",
        "detail": my_detail
    }
    
    
    
def create_detail(detail: DetailBase, current_user: dict, db: Session):
    """Crea un nuevo detalle en la base de datos, validando permisos de usuario o administrador"""

    new_detail = Detail(
        scantilon_location=detail.scantilon_location,
        name_detail=detail.name_detail,
        material_id=detail.material_id,
        layer_thickness=detail.layer_thickness,
    )

    try:
        db.add(new_detail)
        db.commit()
        db.refresh(new_detail)

        my_detail = new_detail.model_dump()
        
        calculate_details_generals(new_detail.id, db)

        return {"success": "Detalle creado", "detail": my_detail}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}




def get_details(type: str, current_user: dict, db: Session): 
    """Obtiene los detalles filtrados por tipo y con información de materiales."""

    query = db.query(Detail).filter(Detail.is_deleted == False)
    
    if type:
        query = query.filter(Detail.scantilon_location == type)

    details = query.all()

    if not details:
        return []

    # Ordenar los detalles: los que tengan created_status "default" y project_id None primero
    details = sorted(
        details, 
        key=lambda d: 0 if (d.created_status == "default" and d.project_id is None) else 1
    )

    material_ids = {detail.material_id for detail in details if detail.material_id}
    
    materials = {m.id: m for m in db.query(Constant).filter(Constant.id.in_(material_ids)).all()}

    list_details = [
        {
            "id_detail": detail.id,
            "scantilon_location": detail.scantilon_location,
            "name_detail": detail.name_detail,
            "id_material": detail.material_id if detail.material_id in materials else None,
            "material": materials[detail.material_id].atributs.get("name") if detail.material_id in materials else "N/A",
            "layer_thickness": detail.layer_thickness
        }
        for detail in details
    ]

    return list_details



def get_details_v2(type: str, current_user: dict, section: str, project_id: int, db: Session):
    """
    Obtiene los detalles filtrados por tipo y con información de materiales.
    
    - Para section "admin": 
        Si se proporciona un project_id:
            Retorna los detalles sin asignación a un proyecto (project_id == None)
            y los detalles asociados a ese project_id.
        Si no se proporciona project_id:
            Retorna solo los detalles sin asignación.
    
    - Para section "user":
        Si se proporciona un project_id:
            1. Si current_user["role_id"] != 1, se verifica que el proyecto exista y pertenezca al usuario actual (current_user["user_id"]).
            2. Se retorna la unión de los detalles sin asignación (project_id == None)
               y los detalles asociados a ese proyecto.
        Si no se proporciona project_id:
            Se retornan los detalles sin asignación o los que pertenecen a cualquiera de los proyectos del usuario.
    """
    query = db.query(Detail).filter(Detail.is_deleted == False)
    
    if type:
        query = query.filter(Detail.scantilon_location == type)
    
    if section.lower() == "admin":
        if project_id is not None:
            query = query.filter(
                or_(
                    Detail.project_id == project_id
                )
            )
        else:
            query = query.filter(Detail.project_id == None)
    elif section.lower() == "user":
        if project_id is not None:
            # Solo se realiza la verificación de proyecto si el usuario no es de rol 1.
            if current_user["role_id"] != 1:
                project = db.query(Project).filter(Project.id == project_id).first()
                if not project or project.user_id != current_user["user_id"]:
                    return []
            query = query.filter(
                or_(
                    Detail.project_id == project_id
                )
            )
        else:
            user_projects = db.query(Project.id).filter(Project.user_id == current_user["user_id"]).all()
            user_project_ids = [proj_id for (proj_id,) in user_projects]
            query = query.filter(
                or_(
                    Detail.project_id == None,
                    Detail.project_id.in_(user_project_ids)
                )
            )

    # Orden personalizado
    query = query.order_by(
        case(
            (Detail.created_status == "default", 1),
            (Detail.created_status == "global", 2),
            (Detail.created_status == "created", 3),
            else_=4
        ).asc(),
        case(
            (Detail.project_id == None, 1),
            else_=2
        ).asc(),
        Detail.id.asc()
    )

    details = query.all()
    
    if not details:
        return []

    # Extraer los IDs de materiales presentes en los detalles.
    material_ids = {detail.material_id for detail in details if detail.material_id}
    
    # Consultar los materiales correspondientes.
    materials = {m.id: m for m in db.query(Constant).filter(Constant.id.in_(material_ids)).all()}
    
    # Armar la lista de detalles enriquecidos con la información de materiales.
    list_details = [
        {
            "id_detail": detail.id,
            "scantilon_location": detail.scantilon_location,
            "name_detail": detail.name_detail,
            "id_material": detail.material_id if detail.material_id in materials else None,
            "material": materials[detail.material_id].atributs.get("name")
                        if detail.material_id in materials else "N/A",
            "layer_thickness": detail.layer_thickness,
            "created_status": detail.created_status
        }
        for detail in details
    ]
    
    return list_details






def get_detail_by_id(detail_id: int, current_user: dict, db: Session):
    """Obtiene un detalle por su ID, asegurándose de que no esté eliminado."""

    detail = db.query(Detail).filter_by(id=detail_id, is_deleted=False).first()

    if not detail:
        raise HTTPException(status_code=404, detail=f"Detalle con ID {detail_id} no encontrado o eliminado.")

    return detail



def get_project_detail(type: str, project_id: int, current_user: dict, db: Session):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user["user_id"],
        Project.is_deleted == False
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )
        
    formula_detail_ids = db.query(Formulas.item_id).filter(
        Formulas.project_id == project_id,
        Formulas.type == "details",
        Formulas.is_deleted == False  
    ).subquery()

    query = db.query(Detail).filter(
        Detail.id.in_(formula_detail_ids),
        Detail.is_deleted == False
    )

    if type:
        query = query.filter(Detail.scantilon_location == type)

    # Orden personalizado
    query = query.order_by(
        case(
            (Detail.created_status == "default", 1),
            (Detail.created_status == "global", 2),
            (Detail.created_status == "created", 3),
            else_=4
        ).asc(),
        case(
            (Detail.project_id == None, 1),
            else_=2
        ).asc(),
        Detail.id.asc()
    )

    details = query.all()

    if not details:
        raise HTTPException(status_code=404, detail="No se encontraron detalles para este proyecto")

    return details


def get_project_detail_by_admin(type: str, project_id: int, current_user: dict, db: Session):
    # Solo los administradores (role_id == 1) pueden acceder
    if current_user.get("role_id") != 1:
        raise HTTPException(
            status_code=403,
            detail="No tiene permisos para acceder a este recurso"
        )
    
    # No se verifica que el proyecto pertenezca al usuario actual, solo se revisa que no esté eliminado.
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_deleted == False
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )
        
    formula_detail_ids = db.query(Formulas.item_id).filter(
        Formulas.project_id == project_id,
        Formulas.type == "details",
        Formulas.is_deleted == False  
    ).subquery()

    query = db.query(Detail).filter(
        Detail.id.in_(formula_detail_ids),
        Detail.is_deleted == False
    )

    if type:
        query = query.filter(Detail.scantilon_location == type)

    details = query.all()

    if not details:
        raise HTTPException(status_code=404, detail="No se encontraron detalles para este proyecto")

    # Ordenar solo por id de forma ascendente
    details = sorted(details, key=lambda d: d.id)

    return details



def get_all_details_part_project(project_id: int, current_user: dict, db: Session):
    try:
        # Si el usuario es administrador (role_id == 1), puede ver todos los proyectos
        if current_user["role_id"] == 1:
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.is_deleted == False
            ).first()
        else:  # Si es un usuario normal (role_id == 2), solo puede ver los suyos
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == current_user["user_id"],
                Project.is_deleted == False
            ).first()

        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado o no autorizado.")

        # Se obtienen todos los detalles del proyecto sin filtrar por type
        results = db.query(DetailPart).filter(
            DetailPart.project_id == project_id,
            DetailPart.type.in_(["Muro", "Techo", "Piso"])
        ).all()

        if not results:
            raise HTTPException(status_code=404, detail="No se encontraron detalles para este proyecto.")

        # Ordenar primero por created_status y luego por id ascendente
        results = sorted(results, key=lambda dp: (dp.created_status, dp.id))

        return results

    except NoResultFound:
        raise HTTPException(status_code=404, detail="Detalles no encontrados.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")



def update_detail(
    detail_id: int,
    updated_data: DetailBase,
    current_user: dict,
    db: Session,
    section: str,           # "admin" o "user"
    project_id: int 
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

    # Actualizar los atributos del detalle
    for key, value in updated_data.model_dump().items():
        setattr(detail, key, value)

    try:
        db.commit()
        db.refresh(detail)

        # Definir el project_id para la recalculación:
        # En modo admin se utiliza el project_id pasado; en modo user se usa None (ya que es detalle propio)
        calc_project_id = project_id if section == "user" else None

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
            km_op_acumulated_value = calculate_km_op_acumulated(db, detail, calc_project_id)
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

        # Ejecutar cálculos generales y parciales usando el detalle actualizado
        calculate_details_generals(detail.id, db, project_id)
        calculate_details_part(db, section, calc_project_id, detail.id, name_detail_if_update, scantilon_if_update)
        db.commit()

        return {"success": "Detalle actualizado", "detail": detail}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar detalle: {str(e)}"
        )


def delete_detail(
    current_user: dict,
    detail_id: int,
    db: Session,
    section: str,           # "admin" o "user"
    project_id: int = None  # Solo se utiliza en modo user para verificar que el detalle es propio
):
    """
    Elimina (marca como eliminado) un detalle.
    
    - En modo "admin": se permite eliminar detalles globales. Solo administradores pueden hacerlo.
    - En modo "user": se permite eliminar solo detalles propios, es decir, el detalle debe pertenecer al proyecto indicado (detail.project_id == project_id).
    """
    # Buscar el detalle que no esté ya elifdsfsdminado
    detail = db.query(Detail).filter(
        Detail.id == detail_id,
        Detail.is_deleted == False
    ).first()

    if not detail:
        raise HTTPException(
            status_code=404,
            detail="Detalle no encontrado o ya eliminado"
        )

    name_detail_if_update = detail.name_detail
    scantilon_if_update = detail.scantilon_location

    if section == "admin":
        # Validar que el usuario tenga permisos de administrador.
        # Se asume que role_id == 1 corresponde a administrador.
        if current_user.get("role_id") != 1:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para eliminar detalles globales"
            )
        # En modo admin no se requiere project_id.
        calc_project_id = None
    elif section == "user":
        # En modo user se debe proporcionar un project_id
        if project_id is None:
            raise HTTPException(
                status_code=400,
                detail="Se requiere project_id en modo user"
            )
        # Verificar que el detalle pertenezca al proyecto indicado
        if detail.project_id != project_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para eliminar este detalle"
            )
        calc_project_id = project_id
    else:
        raise HTTPException(
            status_code=400,
            detail="El parámetro section debe ser 'admin' o 'user'."
        )

    try:
        # Marcar el detalle como eliminado
        detail.is_deleted = True
        db.commit()

        # Eliminar cálculos asociados al detalle
        delete_calculations_for_detail(detail_id, db)

        # Eliminar registros en la tabla Formulas asociados al detalle
        db.query(Formulas).filter(
            Formulas.item_id == detail.id,
            Formulas.type == "details"
        ).delete()

        # Realizar los cálculos necesarios
        calculate_details_part(db, section, calc_project_id, detail_id, name_detail_if_update, scantilon_if_update)
        db.commit()

        return {"message": "Detalle marcado como eliminado"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar detalle: {str(e)}"
        )




def create_default_details(detaill: DetailBase, current_user: dict, db: Session):
    """
    Crea un nuevo detalle "default" en la base de datos.
    Solo los usuarios administradores (role_id == 1) pueden crear este tipo de detalle.
    """
    # Verifica que el usuario sea administrador
    if current_user.get("role_id") != 1:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear detalles default")
    
    new_detail = Detail(
        scantilon_location=detaill.scantilon_location,
        name_detail=detaill.name_detail,
        material_id=detaill.material_id,
        layer_thickness=detaill.layer_thickness,
    )
    
    try:
        db.add(new_detail)
        db.commit()
        db.refresh(new_detail)
        
        my_detail = new_detail.model_dump()
        
        # Se llama a una función para calcular datos generales relacionados con el detalle
        calculate_details_generals(new_detail.id, db)
        
        return {"success": "Detalle default creado", "detail": my_detail}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    
    
    
def get_details_part_project(type: str, project_id: int, current_user: dict, db: Session):
    try:
        # Si el usuario es administrador (role_id == 1), puede ver todos los proyectos
        if current_user["role_id"] == 1:
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.is_deleted == False
            ).first()
        else:  # Si es un usuario normal (role_id == 2), solo puede ver los suyos
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == current_user["user_id"],
                Project.is_deleted == False
            ).first()

        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado o no autorizado.")

        results = db.query(DetailPart).filter(
            DetailPart.type == type,
            DetailPart.project_id == project_id
        ).all()

        if not results:
            raise HTTPException(status_code=404, detail="No se encontraron detalles para este proyecto.")

        # Ordenar primero por created_status y luego por id ascendente
        order_map = {
            "default": 0,
            "global": 1,
            "created": 2
        }

        results = sorted(results, key=lambda dp: (order_map.get(dp.created_status, 99), dp.id))

        return results

    except NoResultFound:
        raise HTTPException(status_code=404, detail="Detalles no encontrados.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")
    


def update_detail_part(detail_type: str, project_id: int, detail_id: int, update: DetailPartUpdate, db: Session, current_user: dict):
    """
    Endpoint para actualizar un 'DetailPart' según su tipo:
    - Muro y Techo: Se actualiza 'surface_color' y se asigna automáticamente el valor.
    - Piso: Permite actualizar otras propiedades pero no 'surface_color'.
    - Se verifica que el usuario sea dueño del proyecto asociado.
    - Se verifica que el nombre del detalle no esté repetido en el mismo proyecto.
    """
    if update.name_detail is None:
        update.name_detail = ""

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="No se encontró el proyecto.")

    if project.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="⛔ No tienes permisos para modificar este proyecto.")

    detail_part = db.query(DetailPart).filter(
        DetailPart.id == detail_id,
        DetailPart.type == detail_type,
        DetailPart.project_id == project_id
    ).first()

    if detail_part.created_status == "default":
        raise HTTPException(status_code=400, detail="No se puede modificar un detalle por defecto   .")
    
    if not detail_part:
        raise HTTPException(status_code=404, detail=f"No se encontró un detalle con ID '{detail_id}' en el proyecto '{project_id}'.")

    # Validación de nombre duplicado
    if update.name_detail:
        existing = db.query(DetailPart).filter(
            DetailPart.project_id == project_id,
            DetailPart.name_detail == update.name_detail,
            DetailPart.id != detail_id  # Evita que se compare consigo mismo
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"❌ Ya existe un detalle con el nombre '{update.name_detail}' en este proyecto.")

    constants_color = db.query(Constant).filter(
        Constant.type == "details",
        Constant.name == "generals"
    ).first()
    surface_colors = constants_color.atributs.get("surface_color", {}) if constants_color else {}

    if detail_type in ["Muro", "Techo"]:
        detail_part.info["surface_color"] = {
            "interior": {
                "name": update.info.get("surface_color", {}).get("interior", {}).get("name", "Intermedio"),
                "value": surface_colors.get(update.info.get("surface_color", {}).get("interior", {}).get("name", "Intermedio"), 0.6)
            },
            "exterior": {
                "name": update.info.get("surface_color", {}).get("exterior", {}).get("name", "Intermedio"),
                "value": surface_colors.get(update.info.get("surface_color", {}).get("exterior", {}).get("name", "Intermedio"), 0.6)
            }
        }
    elif detail_type == "Piso":
        detail_part.info.update(update.info)

    if hasattr(update, "name_detail"):
        detail_part.name_detail = update.name_detail

    flag_modified(detail_part, "info")

    change_detail = db.query(Detail).filter(
        or_(
            Detail.detail_part_id == detail_id,
            and_(
                Detail.project_id == project_id,
                Detail.name_detail == detail_part.name_detail
            )
        )
    ).all()

    for detail in change_detail:
        if hasattr(update, "name_detail"):
            detail.name_detail = update.name_detail

    try:
        db.commit()
        return {"message": f"✅ Se actualizó correctamente el detalle con ID '{detail_id}' en el proyecto '{project_id}' de tipo '{detail_type}'."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"❌ Error al actualizar el detalle: {str(e)}")



def update_detail_part_admin(detail_type: str, detail_id: int, update: DetailPartUpdate, db: Session, current_user: dict):
    """
    Endpoint para que el administrador actualice un 'DetailPart' según su tipo, 
    únicamente para aquellos en los que DetailPart.project_id es None:
    
    - Muro y Techo: Se actualiza 'surface_color' y se asigna automáticamente el valor.
    - Piso: Permite actualizar otras propiedades pero no 'surface_color'.
    - Se verifica que el nombre no esté repetido en los detalles globales.
    """
    detail_part = db.query(DetailPart).filter(
        DetailPart.id == detail_id,
        DetailPart.type == detail_type,
        DetailPart.project_id == None
    ).first()

    if not detail_part:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró un detalle con ID '{detail_id}' de tipo '{detail_type}' sin proyecto asignado."
        )

    # Validación de nombre duplicado entrfdse detalles globales
    if update.name_detail:
        existing = db.query(DetailPart).filter(
            DetailPart.project_id == None,
            DetailPart.name_detail == update.name_detail,
            DetailPart.id != detail_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"❌ Ya existe un detalle global con el nombre '{update.name_detail}'."
            )

    constants_color = db.query(Constant).filter(
        Constant.type == "details",
        Constant.name == "generals"
    ).first()
    surface_colors = constants_color.atributs.get("surface_color", {}) if constants_color else {}

    if detail_type in ["Muro", "Techo"]:
        detail_part.info["surface_color"] = {
            "interior": {
                "name": update.info.get("surface_color", {}).get("interior", {}).get("name", "Intermedio"),
                "value": surface_colors.get(update.info.get("surface_color", {}).get("interior", {}).get("name", "Intermedio"), 0.6)
            },
            "exterior": {
                "name": update.info.get("surface_color", {}).get("exterior", {}).get("name", "Intermedio"),
                "value": surface_colors.get(update.info.get("surface_color", {}).get("exterior", {}).get("name", "Intermedio"), 0.6)
            }
        }
    elif detail_type == "Piso":
        detail_part.info.update(update.info)

    detail_part.name_detail = update.name_detail
    flag_modified(detail_part, "info")

    change_detail = db.query(Detail).filter(
        or_(
            Detail.detail_part_id == detail_id,
            and_(
                Detail.project_id == None,
                Detail.name_detail == detail_part.name_detail
            )
        )
    ).all()

    for detail in change_detail:
        if hasattr(update, "name_detail"):
            detail.name_detail = update.name_detail
    try:
        db.commit()
        return {"message": f"✅ Se actualizó correctamente el detalle con ID '{detail_id}' de tipo '{detail_type}'."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"❌ Error al actualizar el detalle: {str(e)}")
    
    
    
def delete_detail_by_admin(
    current_user: dict,
    detail_id: int,
    db: Session,
    section: str,           # "admin" o "user"
    project_id: int = None  # Obligatorio en modo user; no debe enviarse en modo admin
):
    """
    Elimina (borrado físico) un detalle a partir de la tabla DetailPart y, posteriormente,
    elimina de la tabla Detail todos los registros que tengan el mismo name_detail.
    
    Además, elimina de la tabla Formulas todos los registros que tengan el mismo name_detail,
    filtrando por project_id y por su nombre.

    - En modo "user": se requiere project_id y se eliminan los registros en DetailPart, Detail y Formulas donde project_id coincide.
    - En modo "admin": se eliminan los registros en DetailPart, Detail y Formulas donde project_id es None.
    """
    # Validar el parámetro section y la presencia o ausencia de project_id
    if section not in ["admin", "user"]:
        raise HTTPException(
            status_code=400,
            detail="El parámetro section debe ser 'admin' o 'user'."
        )
    
    if section == "user" and project_id is None:
        raise HTTPException(
            status_code=400,
            detail="Se requiere project_id en modo user."
        )
    
    if section == "admin" and project_id is not None:
        raise HTTPException(
            status_code=400,
            detail="No se debe proporcionar project_id en modo admin."
        )
    
    try:
        # Consultar en la tabla DetailPart según el modo
        if section == "user":
            detail_part_query = db.query(DetailPart).filter(
                DetailPart.id == detail_id,
                DetailPart.project_id == project_id
            )
        else:  # admin
            detail_part_query = db.query(DetailPart).filter(
                DetailPart.id == detail_id,
                DetailPart.project_id.is_(None)
            )
        
        detail_part = detail_part_query.first()
        if not detail_part:
            raise HTTPException(
                status_code=404,
                detail="No se encontró el DetailPart a eliminar."
            )
        
        # Almacenar el name_detail para utilizarlo en la eliminación de Detail y Formulas
        name_detail = detail_part.name_detail

        # Eliminar el registro de DetailPart
        detail_part_query.delete(synchronize_session=False)
        
        # En la tabla Detail, eliminar aquellos registros con el mismo name_detail,
        # filtrando según el modo de operación
        if section == "user":
            details_query = db.query(Detail).filter(
                Detail.name_detail == name_detail,
                Detail.project_id == project_id
            )
        else:  # admin
            details_query = db.query(Detail).filter(
                Detail.name_detail == name_detail,
                Detail.project_id.is_(None)
            )
        
        details_query.delete(synchronize_session=False)
        
        # En la tabla Formulas, eliminar aquellos registros con el mismo name_detail,
        # filtrando según el modo de operación
        if section == "user":
            formulas_query = db.query(Formulas).filter(
                Formulas.name == name_detail,
                Formulas.project_id == project_id
            )
        else:  # admin
            formulas_query = db.query(Formulas).filter(
                Formulas.name == name_detail,
                Formulas.project_id.is_(None)
            )
        
        formulas_query.delete(synchronize_session=False)
        
        db.commit()
        return {
            "message": f"Se eliminaron el DetailPart y sus Details y Formulas asociados con name_detail '{name_detail}'."
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar detalle: {str(e)}"
        )

        
        
        
def get_all_detail_part_admin(type: str, current_user: dict, db: Session):
    try:
        results = (
            db.query(DetailPart)
            .filter(DetailPart.type == type, DetailPart.project_id == None)
            .all()
        )

        if not results:
            raise HTTPException(status_code=404, detail="No se encontraron detalles para este tipo.")

        # Ordenar primero por created_status y luego por id ascendente
        order_map = {
            "default": 0,
            "global": 1,
            "created": 2
        }

        results = sorted(results, key=lambda dp: (order_map.get(dp.created_status, 99), dp.id))

        return results

    except NoResultFound:
        raise HTTPException(status_code=404, detail="Detalles no encontrados.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")

from dataclasses import dataclass
@dataclass
class DetailNodeLayer:
    id: int
    name: str
    thickness: float
    material: Constant

def get_wall_layer(detail_parent_id: int, db: Session):
    results=db.query(Detail).filter(Detail.detail_part_id == detail_parent_id).all()
    layers: List[DetailNodeLayer] = []
    for result in results:
        material=db.query(Constant).filter(Constant.id == result.material_id).first()
        node_layer = DetailNodeLayer(
                id=result.id,
                name='result.name',
                thickness=result.layer_thickness,
                material=material
            )

        node_layer.material.atributs.get('density')
        layers.append(node_layer)
    return layers