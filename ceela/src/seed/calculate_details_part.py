"""
create_details_part.py

Este módulo contiene:
  - Funciones de cálculo y actualización para la tabla DetailPart, utilizando la lógica
    que se usaba en el seed (agrupación por (scantilon_location, name_detail) y cálculos extra).
  - La función create_details_part, que crea un nuevo Detail, inserta su registro en Formulas,
    y actualiza DetailPart.
  - La función create_details_part_seed, que ejecuta el mismo proceso para seed,
    es decir, sin asociar a ningún proyecto (project_id == None) y en modo admin.
  - Los métodos de cálculo adicionales adaptados para seed/admin, incluyendo:
      * calculate_km_op_acumulated
      * calculate_position_insulation
      * recalculate_position_insulation_user (para usuarios)
      * recalculate_position_insulation_seed (para seed)
      
IMPORTANTE: Revisa y adapta las funciones y consultas según la estructura y lógica de tu proyecto.
"""

from sqlalchemy import func, cast, Float, Integer, String, and_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging

# Importa tus modelos (ajustafds los nombrefdsfdffds según tu proyecto)
from src.models.entity.constant import Constant
from src.models.entity.details import Detail
from src.models.entity.formulas import Formulas
from src.models.entity.detail_part import DetailPart
from src.models.entity.calculations import Calculation

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_aislacion_bajo_piso(project_id, name_detail, scantilon_location, db: Session):
    """
    Calcula la aislación bajo piso considerando solo los materiales con is_insulation == 1.
    Para el seed se ejecuta con project_id == None.
    """
    insulated_detail_ids = db.query(Detail.id).filter(
        Detail.scantilon_location == scantilon_location,
        Detail.id.in_(
            db.query(Calculation.reference_id)
            .filter(
                Calculation.type == "details",
                Calculation.name == "generals",
                func.coalesce(cast(Calculation.values["is_insulation"].astext, Integer), 0) == 1
            )
        )
    ).all()
    insulated_ids = {row[0] for row in insulated_detail_ids} if insulated_detail_ids else set()
    if not insulated_ids:
        return None

    material_conductivities = db.query(
        Detail.id,
        Detail.layer_thickness,
        cast(Constant.atributs["conductivity"].astext, Float)
    ).join(Constant, Detail.material_id == Constant.id)\
     .filter(Constant.name == "materials")\
     .filter(Detail.name_detail == name_detail)\
     .filter(Detail.scantilon_location == scantilon_location)\
     .filter(Detail.id.in_(insulated_ids))\
     .filter(Detail.id.in_(
         db.query(Formulas.item_id)
         .filter(Formulas.project_id.is_(project_id), Formulas.type == "details")
     )).all()

    total_thickness = sum(thickness for _, thickness, conductivity in material_conductivities
                          if conductivity is not None and conductivity < 0.7)
    total_conductivity = sum(conductivity for _, _, conductivity in material_conductivities if conductivity is not None)
    return (total_conductivity, total_thickness)


def calculate_details_part_extras(db: Session, name_detail: str, scantilon_location: str, limites_cp_liviano: float, limites_cp_pesado: float):
    """
    Calcula los valores "extras" para DetailPart:
      - Espesor de aislamiento.
      - Suma de fourier_nodes y km_op, y una clasificación (cat_ceeup).
      - Posición del aislamiento (basada en la suma de Formulas.atributs["position_insulation"]).
      
    Se usan registros con project_id == None.
    """
    # Material conductivfdsities para aislamiento
    material_conductivities = db.query(
        Detail.id,
        Detail.layer_thickness,
        cast(Constant.atributs["conductivity"].astext, Float)
    ).join(Constant, Detail.material_id == Constant.id)\
     .filter(Constant.name == "materials")\
     .filter(Detail.name_detail == name_detail)\
     .filter(Detail.scantilon_location == scantilon_location)\
     .filter(Detail.id.in_(
         db.query(Formulas.item_id)
         .filter(Formulas.project_id.is_(None), Formulas.type == "details")
     )).all()
    if not material_conductivities:
        return None

    total_thickness = sum(thickness for _, thickness, conductivity in material_conductivities
                          if conductivity is not None and conductivity < 0.07)

    # Datos de cálculos: fourier_nodes, km_op, is_wood
    calculation_data = db.query(
        cast(Calculation.values["fourier_nodes"].astext, Float),
        cast(Calculation.values["km_op"].astext, Float),
        cast(Calculation.values["is_wood"].astext, Integer)
    ).filter(
        Calculation.reference_id.in_(
            db.query(Detail.id)
            .filter(Detail.name_detail == name_detail, Detail.scantilon_location == scantilon_location)
        )
    ).filter(
        Calculation.type == "details",
        Calculation.name == "generals"
    ).all()
    total_fourier_nodes = sum(row[0] for row in calculation_data if row[0] is not None)
    total_km_op = sum(row[1] for row in calculation_data if row[1] is not None)
    total_is_wood = sum(row[2] for row in calculation_data if row[2] is not None and row[2] >= 1)
    suma_km_op_wood = sum(row[1] for row in calculation_data if row[1] is not None and row[2] == 1)
    doble_suma_km_op_wood = 2 * suma_km_op_wood

    if total_is_wood >= 1 and doble_suma_km_op_wood > total_km_op:
        classification = "EM"
    elif total_km_op == 0:
        classification = 0
    elif total_km_op <= limites_cp_liviano:
        classification = "EL"
    elif total_km_op >= limites_cp_pesado:
        classification = "EP"
    else:
        classification = "EI"

    # Cálculo de la posición del aislamiento
    total_position_insulation = db.query(
        func.sum(cast(Formulas.atributs["position_insulation"].astext, Integer))
    ).filter(
        Formulas.project_id.is_(None),
        Formulas.type == "details",
        Formulas.item_id.in_(
            db.query(Detail.id)
            .filter(Detail.name_detail == name_detail, Detail.scantilon_location == scantilon_location)
        )
    ).scalar() or 0

    insulation_category = db.query(
        cast(Constant.atributs["insulation_position"].astext, String)
    ).filter(
        Constant.name == "generals",
        Constant.type == "details"
    ).scalar()
    if insulation_category:
        try:
            insulation_category = eval(insulation_category).get(str(total_position_insulation), "Desconocido")
        except Exception:
            insulation_category = "Desconocido"

    
    detail_part = (
        db.query(DetailPart)
        .filter(
            DetailPart.project_id.is_(None),
            DetailPart.name_detail == name_detail,
            DetailPart.type == scantilon_location
        )
        .first()
    )

    if detail_part:
        detail_part.calculations["espesor_aislacion"] = total_thickness
        detail_part.calculations["fourier_nodes"] = total_fourier_nodes
        detail_part.calculations["km_op"] = total_km_op
        detail_part.calculations["cat_ceeup"] = classification
        detail_part.calculations["position_insulation"] = insulation_category
        flag_modified(detail_part, "calculations")

        return {
            "espesor_aislacion": total_thickness,
            "fourier_nodes": total_fourier_nodes,
            "km_op": total_km_op,
            "cat_ceeup": classification,
            "position_insulation": insulation_category
        }


def update_detail_part_for_group(db: Session, location: str, name_detail: str):
    """
    Para el grupo definido por (scantilon_location, name_detail) (con project_id == None),
    se suman los valores de la clave "r" y se calculan los valores de U y extras para actualizar
    o insertar el registro correspondiente en DetailPart.
    """
    joined_details = db.query(
        Detail.scantilon_location,
        Detail.name_detail,
        Calculation.values
    ).join(Calculation, Calculation.reference_id == Detail.id)\
     .filter(
         Detail.project_id.is_(None),
         Detail.scantilon_location == location,
         Detail.name_detail == name_detail,
         Calculation.type == "details",
         Calculation.name == "generals"
     ).all()

    if not joined_details:
        logger.info(f"No se encontraron registros para actualizar DetailPart ({location}, {name_detail}).")
        return

    r_sum = sum(
        (calc_values.get("r", 0.0) if calc_values else 0.0)
        for _, _, calc_values in joined_details
    )

    constant_color = db.query(Constant).filter(
        Constant.type == "details",
        Constant.name == "generals"
    ).first()
    surface_colors = constant_color.atributs.get("surface_color", {}) if constant_color else {}
    constant_resistance = db.query(Constant).filter(
        Constant.type == "elements",
        Constant.name == "generals"
    ).first()
    thermal_resistances = constant_resistance.atributs.get("thermal_resistances", {}) if constant_resistance else {}

    if location == "Muro":
        info = {
            "surface_color": {
                "interior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                "exterior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)}
            }
        }
        rsi = thermal_resistances.get("rsi_wall", 0.13)
        rse = thermal_resistances.get("rse_wall", 0.04)
    elif location == "Techo":
        info = {
            "surface_color": {
                "interior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                "exterior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)}
            }
        }
        rsi = thermal_resistances.get("rsi_roof", 0.09)
        rse = thermal_resistances.get("rse_roof", 0.04)
    elif location == "Piso":
        aislacion = calculate_aislacion_bajo_piso(None, name_detail, location, db)
        if aislacion:
            lambda_val, e_aisl = aislacion
        else:
            lambda_val, e_aisl = 0, 0
        info = {
            "aislacion_bajo_piso": {"lambda": lambda_val, "e_aisl": e_aisl},
            "ref_aisl_vertical": {"lambda": 0, "e_aisl": 0, "d": 0},
            "ref_aisl_horizontal": {"lambda": 0, "e_aisl": 0, "d": 0}
        }
        rsi = thermal_resistances.get("rsi_floor", 0.17)
        rse = thermal_resistances.get("rse_floor", 0.04)
    else:
        info = {}
        rsi = rse = 0

    denominator = rsi + rse + r_sum
    value_u = 1 / denominator if denominator != 0 else 0.0

    limites_cp_liviano = 75_000
    limites_cp_pesado = 175_000
    extras = calculate_details_part_extras(db, name_detail, location, limites_cp_liviano, limites_cp_pesado)

    existing_record = db.query(DetailPart)\
        .filter(DetailPart.project_id.is_(None),
                DetailPart.type == location,
                DetailPart.name_detail == name_detail)\
        .first()

    try:
        if existing_record:
            existing_record.value_u = value_u
            existing_record.info = info
            existing_record.calculations = extras
            # Usamos flag_modified para indicar que se han modificado campos de tipo dict
            flag_modified(existing_record, "info")
            flag_modified(existing_record, "calculations")
            db.commit()
            logger.info(f"Actualizado DetailPart para ({location}, {name_detail}).")
        else:
            new_dp = DetailPart(
                project_id=None,
                type=location,
                name_detail=name_detail,
                value_u=value_u,
                info=info,
                calculations=extras
            )
            db.add(new_dp)
            
            flag_modified(existing_record, "info")
            flag_modified(existing_record, "calculations")
            
            db.commit()
            logger.info(f"Insertado nuevo DetailPart para ({location}, {name_detail}).")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar/inserción en DetailPart: {e}")


def calculate_km_op_acumulated(db: Session, detail: Detail) -> float:
    """
    Calcula el km_op_acumulated de manera progresiva, sumando el km_op de los detalles previos
    con la misma ubicación de escantillón y nombre de detalle.
    Se asume project_id == None (modo seed/admin).
    """
    subquery = (
        db.query(
            Calculation.reference_id,
            func.sum(cast(Calculation.values["km_op"].astext, Float)).over(
                order_by=Detail.id,
                partition_by=[Detail.scantilon_location, Detail.name_detail]
            ).label("km_op_acumulated")
        )
        .join(Detail, Calculation.reference_id == Detail.id)
        .filter(
            Calculation.type == "details",
            Calculation.name == "generals",
            Detail.scantilon_location == detail.scantilon_location,
            Detail.name_detail == detail.name_detail
        )
        .subquery()
    )

    km_op_acumulated = db.query(subquery.c.km_op_acumulated)\
                         .filter(subquery.c.reference_id == detail.id)\
                         .scalar() or 0
    return km_op_acumulated


def calculate_position_insulation(id_detail: int, limit_cp_bordes: float, db: Session) -> int:
    """
    Calcula la posición del aislante para un detail específico.
    Adaptado para seed (project_id == None). Se usa dentro de los métodos de recálculo.
    """
    detail_data = db.query(
        Detail.name_detail,
        func.coalesce(cast(Calculation.values["is_insulation"].astext, Float), 0)
    ).outerjoin(Calculation, and_(
        Calculation.type == "details",
        Calculation.name == "generals",
        Calculation.reference_id == id_detail
    )).filter(Detail.id == id_detail).first()

    if not detail_data:
        return 0

    name_detail, is_insulation = detail_data

    if is_insulation == 0:
        return 0  

    sum_insulation_km = db.query(
        func.coalesce(func.sum(cast(Calculation.values["is_insulation"].astext, Float)), 0),
        func.coalesce(func.sum(cast(Calculation.values["km_op"].astext, Float)), 0)
    ).join(Formulas, Formulas.item_id == Calculation.reference_id)\
     .filter(
         Calculation.type == "details",
         Calculation.name == "generals",
         Formulas.type == "details",
         Formulas.project_id.is_(None),
         Formulas.item_id.in_(
             db.query(Detail.id).filter(Detail.name_detail == name_detail)
         )
     ).first()

    sum_is_insulation, sum_km_op = sum_insulation_km or (0, 0)

    if sum_is_insulation == 0 or sum_km_op == 0:
        return 0 

    km_op_acumulated = db.query(
        func.coalesce(cast(Formulas.atributs["km_op_acumulated"].astext, Float), 0)
    ).filter(
        Formulas.project_id.is_(None),
        Formulas.type == "details",
        Formulas.item_id == id_detail
    ).scalar() or 0

    if km_op_acumulated < (limit_cp_bordes * sum_km_op):
        return 1
    elif km_op_acumulated > ((1 - limit_cp_bordes) * sum_km_op):
        return 3
    return 2


def recalculate_position_insulation_user(project_id: int, limit_cp_bordes: float, db: Session):
    """
    Recalcula y actualiza la posición del aislamiento (`position_insulation`) de todos los detalles
    activos en un proyecto (modo usuario).
    """
    valid_detail_ids = [
        det_id for (det_id,) in db.query(Formulas.item_id)
        .filter(Formulas.project_id == project_id, Formulas.type == "details")
        .all()
    ]

    if not valid_detail_ids:
        logger.info("⚠️ No hay detalles válidos para recalcular en el proyecto.")
        return

    detail_info = {
        det_id: formula.atributs
        for det_id, formula in db.query(Formulas.item_id, Formulas)
        .filter(Formulas.project_id == project_id, Formulas.type == "details")
        .all()
    }

    for det_id in valid_detail_ids:
        position_insulation = calculate_position_insulation(det_id, limit_cp_bordes, db)
        formula = db.query(Formulas).filter(
            Formulas.project_id == project_id,
            Formulas.item_id == det_id,
            Formulas.type == "details"
        ).first()
        if formula:
            formula.atributs = {**detail_info.get(det_id, {}), "position_insulation": position_insulation}
            flag_modified(formula, "atributs")
    db.commit()


def recalculate_position_insulation_seed(limit_cp_bordes: float, db: Session):
    """
    Recalcula y actualiza la posición del aislamiento (`position_insulation`) de todos los detalles
    en seed (modo admin, project_id == None).
    """
    valid_detail_ids = [
        det_id for (det_id,) in db.query(Formulas.item_id)
        .filter(Formulas.project_id.is_(None), Formulas.type == "details")
        .all()
    ]

    if not valid_detail_ids:
        logger.info("⚠️ No hay detalles válidos para recalcular en seed.")
        return

    detail_info = {
        det_id: formula.atributs
        for det_id, formula in db.query(Formulas.item_id, Formulas)
        .filter(Formulas.project_id.is_(None), Formulas.type == "details")
        .all()
    }

    for det_id in valid_detail_ids:
        position_insulation = calculate_position_insulation(det_id, limit_cp_bordes, db)
        formula = db.query(Formulas).filter(
            Formulas.project_id.is_(None),
            Formulas.item_id == det_id,
            Formulas.type == "details"
        ).first()
        if formula:
            formula.atributs = {**detail_info.get(det_id, {}), "position_insulation": position_insulation}
            flag_modified(formula, "atributs")
    db.commit()


def create_details_part(detail, current_user, db: Session, section: str, project_id: int):
    """
    Crea un nuevo Detail, inserta su registro en Formulas y, a la vez,
    actualiza el registro en DetailPart correspondiente.

    Para la sección "user":
      - Se requiere project_id.
      - El Detail se asocia al proyecto.
      - Se realiza el recálculo de la posición de aislamiento para el proyecto.

    Para la sección "admin":
      - Se crea el Detail con project_id == None.
      - Se registra en Formulas y se actualiza DetailPart usando la lógica del seed.
      - Se recalcula la posición de aislamiento en modo seed.

    Retorna:
        dict: Resultado de la operación, incluyendo el Detail creado.
    """
    if section not in ["user", "admin"]:
        return {"error": "Sección inválida. Use 'user' o 'admin'."}

    detail_data = {
        "scantilon_location": detail.scantilon_location,
        "name_detail": detail.name_detail,
        "material_id": detail.material_id,
        "layer_thickness": detail.layer_thickness,
    }
    if section == "user":
        if project_id is None:
            return {"error": "Para 'user' se requiere project_id."}
        detail_data["project_id"] = project_id
    else:
        detail_data["project_id"] = None

    new_detail = Detail(**detail_data)
    try:
        db.add(new_detail)
        db.commit()
        db.refresh(new_detail)
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    detail_atributs = {
        "scantilon_location": new_detail.scantilon_location,
        "name_detail": new_detail.name_detail,
        "material_id": new_detail.material_id,
        "layer_thickness": new_detail.layer_thickness,
        "km_op_acumulated": calculate_km_op_acumulated(db, new_detail),
        "position_insulation": 0
    }
    formula_project_id = project_id if section == "user" else None

    try:
        new_formula = Formulas(
            project_id=formula_project_id,
            item_id=new_detail.id,
            type="details",
            name=new_detail.name_detail,
            atributs=detail_atributs,
            is_deleted=False
        )
        db.add(new_formula)
        db.commit()
        db.refresh(new_formula)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear fórmula: {str(e)}")

    # Se ejecuta el recálculo de posición de aislamiento en todos los casos
    if section == "user":
        limit_cp_bordes = (
            db.query(cast(Constant.atributs["light_for_edge_layer"].astext, Float))
              .filter(Constant.name == "generals", Constant.type == "details")
              .scalar() or 0.0
        )
        recalculate_position_insulation_user(project_id, limit_cp_bordes, db)
    else:
        limit_cp_bordes = (
            db.query(cast(Constant.atributs["light_for_edge_layer"].astext, Float))
              .filter(Constant.name == "generals", Constant.type == "details")
              .scalar() or 0.0
        )
        recalculate_position_insulation_seed(limit_cp_bordes, db)


    return {
        "success": "Detalle, fórmula y parte de detalles actualizados correctamente.",
        "detail": new_detail.__dict__
    }

def calculate_details_part_seed(db: Session, edited_detail_id: int = None):
    """
    Recalcula la tabla DetailPart en modo seed (admin) usando los detalles que tengan 
    project_id == None y created_status == "default". Se obtienen los detalles a través 
    de la tabla intermedia 'Formulas'.

    Si se pasa un edited_detail_id, se elimina primero el DetailPart correspondiente 
    a ese detalle (según su name_detail) para luego recalcularlo. Si no se pasa edited_detail_id 
    y ya existen registros en DetailPart, la función retorna sin hacer nada (se calcula solo una vez).
    """
    # Si se está editando un detalle, eliminar su registro en DetailPart (según su name_detail)
    if edited_detail_id:
        detail_to_edit = db.query(Detail).filter(
            Detail.id == edited_detail_id,
            Detail.project_id.is_(None),
            Detail.created_status == "default"
        ).first()
        if not detail_to_edit:
            raise HTTPException(status_code=404, detail="Detalle no encontrado.")
        db.query(DetailPart).filter(
            DetailPart.name_detail == detail_to_edit.name_detail,
            DetailPart.project_id.is_(None)
        ).delete()
        db.commit()
    else:
        # Si ya se calcularon registros previamente, no se vuelve a calcular
        existe = db.query(DetailPart).filter(DetailPart.project_id.is_(None)).first()
        if existe:
            print("✅ DetailPart ya ha sido calculado previamente. Se omite la recalculación.")
            return

    # Seleccionar IDs de detalles que cumplen los criterios
    selected_details = db.query(Detail.id).join(Formulas, Formulas.item_id == Detail.id)\
        .filter(
            Formulas.project_id.is_(None),
            Formulas.type == "details",
            Detail.created_status == "default"
        ).all()
    selected_ids = [d[0] for d in selected_details]
    if not selected_ids:
        raise HTTPException(status_code=400, detail="No se encontraron detalles para recalcular.")

    # Extraer información: ubicación, nombre y valores de cálculos
    details = db.query(
        Detail.scantilon_location,
        Detail.name_detail,
        Calculation.values
    ).join(Formulas, Formulas.item_id == Detail.id)\
     .join(Calculation, Calculation.reference_id == Detail.id)\
     .filter(
         Formulas.project_id.is_(None),
         Formulas.type == "details",
         Detail.id.in_(selected_ids),
         Calculation.type == "details",
         Calculation.name == "generals"
     ).all()

    if not details:
        raise HTTPException(status_code=400, detail="No se encontraron detalles seleccionados para recalcular.")

    # Agrupar por (scantilon_location, name_detail) acumulando la suma de la clave "r"
    grouped_details = {}
    for location, name, values in details:
        r_value = values.get("r", 0.0)
        key = (location, name)
        if key not in grouped_details:
            grouped_details[key] = {
                "type": location,
                "name_detail": name,
                "value_u": 0.0,
                "info": {},
                "r_sum": 0.0
            }
        grouped_details[key]["r_sum"] += r_value

    # Consultar constantes para obtener colores y resistencias térmicas
    constants_color = db.query(Constant).filter(
        Constant.type == "details",
        Constant.name == "generals"
    ).first()
    surface_colors = constants_color.atributs.get("surface_color", {}) if constants_color else {}

    constants_resistance = db.query(Constant).filter(
        Constant.type == "elements",
        Constant.name == "generals"
    ).first()
    thermal_resistances = constants_resistance.atributs.get("thermal_resistances", {}) if constants_resistance else {}

    # Recorrer cada grupo para definir "info" y calcular el valor U
    for (location, name), data in grouped_details.items():
        if location == "Muro":
            data["info"] = {
                "surface_color": {
                    "interior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                    "exterior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)}
                }
            }
            rsi = thermal_resistances.get("rsi_wall", 0.13)
            rse = thermal_resistances.get("rse_wall", 0.04)
        elif location == "Techo":
            data["info"] = {
                "surface_color": {
                    "interior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                    "exterior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)}
                }
            }
            rsi = thermal_resistances.get("rsi_roof", 0.09)
            rse = thermal_resistances.get("rse_roof", 0.04)
        elif location == "Piso":
            # Para Piso se invoca el cálculo de aislación
            aislacion = calculate_aislacion_bajo_piso(None, name, location, db)
            if aislacion:
                lambda_val, e_aisl = aislacion
            else:
                lambda_val, e_aisl = 0, 0
            data["info"] = {
                "aislacion_bajo_piso": {"lambda": lambda_val, "e_aisl": e_aisl},
                "ref_aisl_vertical": {"lambda": 0, "e_aisl": 0, "d": 0},
                "ref_aisl_horizontal": {"lambda": 0, "e_aisl": 0, "d": 0}
            }
            rsi = thermal_resistances.get("rsi_floor", 0.17)
            rse = thermal_resistances.get("rse_floor", 0.04)
        else:
            rsi = 0
            rse = 0

        total_r = data["r_sum"]
        data["value_u"] = 1 / (rsi + rse + total_r) if (rsi + rse + total_r) != 0 else 0.0
        del data["r_sum"]

    # Insertar o actualizar registros en DetailPart para cada grupo
    for (location, name), data in grouped_details.items():
        existing_dp = db.query(DetailPart).filter(
            DetailPart.project_id.is_(None),
            DetailPart.type == location,
            DetailPart.name_detail == name
        ).first()
        if existing_dp:
            existing_dp.value_u = data["value_u"]
            existing_dp.info = data["info"]
        else:
            new_dp = DetailPart(
                project_id=None,
                type=location,
                name_detail=name,
                value_u=data["value_u"],
                info=data["info"]
            )
            db.add(new_dp)
    try:
        db.commit()
        print(f"✅ DetailPart recalculados para {len(grouped_details)} grupos.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al recalcular DetailPart: {e}")

    # Segunda fase opcional: invocar funciones extras (solo si es necesario)
    for (name, location) in grouped_details.keys():
        calculate_details_part_extras(
            db=db,
            name_detail=name,
            scantilon_location=location,
            limites_cp_liviano=75_000,
            limites_cp_pesado=175_000
        )
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error finalizando el recálculo extra: {e}")

