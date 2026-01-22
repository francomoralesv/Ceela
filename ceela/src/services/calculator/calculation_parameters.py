from __future__ import annotations

# =========================
# Imports
# =========================
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import and_, or_, func, cast
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.types import Float, Integer, String, Text

from src.models.entity.calculations import Calculation
from src.models.entity.formulas import Formulas
from src.models.entity.details import Detail
from src.models.entity.detail_part import DetailPart
from src.models.entity.constant import Constant
from src.models.entity.elements import Element
from src.seed.calculation import calculation_nodes_fourier, calculation_km_op, is_wood, is_insulating


# =========================
# Utilidades SQL (helpers)
# =========================
def json_float(expr, key: str):
    """Convierte JSON->text->float, con cast SQLAlchemy."""
    return cast(expr[key].astext, Float)


def json_int(expr, key: str):
    """Convierte JSON->text->int, con cast SQLAlchemy."""
    return cast(expr[key].astext, Integer)


def coalesce_float(expr, default: float = 0.0):
    """COALESCE para Float."""
    return func.coalesce(expr, default)


# =========================
# Cálculos acumulados / auxiliares
# =========================
def calculate_km_op_acumulated(db: Session, detail: Detail, project_id: Optional[int] = None) -> float:
    """
    Suma 'km_op' (Calculation.values["km_op"]) de todos los Calculations que:
    - coinciden en (scantilon_location, name_detail) con el Detail dado
    - type="details" y name="generals"
    - pertenecen al mismo project_id (o None si no se indicó)
    """
    project_condition = (Calculation.project_id == project_id) if project_id is not None else Calculation.project_id.is_(None)

    total = (
        db.query(func.sum(json_float(Calculation.values, "km_op")))
        .join(Detail, Calculation.reference_id == Detail.id)
        .filter(
            Calculation.type == "details",
            Calculation.name == "generals",
            project_condition,
            Detail.scantilon_location == detail.scantilon_location,
            Detail.name_detail == detail.name_detail,
        )
        .scalar()
        or 0.0
    )
    return float(total)


# =========================
# Posición de aislante
# =========================
from sqlalchemy import and_, exists
from sqlalchemy.orm import aliased

def calculate_position_insulation(
    id_detail: int,
    limit_cp_bordes: float,
    db: Session,
    project_id: Optional[int] = None,
) -> int:
    # Asegura que cualquier insert/update previo sea visible y que no leas cache
    db.flush()
    db.expire_all()

    # Helper para filtrar proj_id None vs con valor
    def _proj_filter(col):
        return (col.is_(None) if project_id is None else col == project_id)

    # 1) name_detail + is_insulation del detail actual
    detail_data = (
        db.query(
            Detail.name_detail,
            coalesce_float(json_float(Calculation.values, "is_insulation"), 0).label("is_insulation"),
        )
        .outerjoin(
            Calculation,
            and_(
                Calculation.type == "details",
                Calculation.name == "generals",
                Calculation.reference_id == id_detail,
                _proj_filter(Calculation.project_id),
            ),
        )
        .filter(Detail.id == id_detail)
        .one_or_none()
    )

    if not detail_data or float(detail_data.is_insulation) == 0:
        return 0

    name_detail = detail_data.name_detail

    # 2) Sumar is_insulation y km_op para todos los detalles con el mismo name_detail
    #    Evitar duplicados por Formulas usando EXISTS en vez de JOIN.
    F = aliased(Formulas)
    sum_row = (
        db.query(
            coalesce_float(func.sum(json_float(Calculation.values, "is_insulation")), 0),
            coalesce_float(func.sum(json_float(Calculation.values, "km_op")), 0),
        )
        .join(Detail, Detail.id == Calculation.reference_id)
        .filter(
            Calculation.type == "details",
            Calculation.name == "generals",
            _proj_filter(Calculation.project_id),
            Detail.name_detail == name_detail,
            _proj_filter(Detail.project_id),
            exists().where(and_(
                F.item_id == Detail.id,
                F.type == "details",
                _proj_filter(F.project_id),
            ))
        )
        .one()
    )
    sum_is_insulation = float(sum_row[0])
    sum_km_op = float(sum_row[1])

    if sum_is_insulation == 0 or sum_km_op == 0:
        return 0

    # 3) Sumar km_op_acumulated para el id_detail (filtrando por project_id)
    km_op_acumulated = (
        db.query(coalesce_float(func.sum(json_float(Formulas.atributs, "km_op_acumulated")), 0))
        .filter(
            Formulas.type == "details",
            _proj_filter(Formulas.project_id),
            Formulas.item_id == id_detail,
        )
        .scalar() or 0.0
    )
    km_op_acumulated = float(km_op_acumulated)

    # Reglas de posición
    if km_op_acumulated < (limit_cp_bordes * sum_km_op):
        return 1
    if km_op_acumulated > ((1 - limit_cp_bordes) * sum_km_op):
        return 3
    return 2


def recalculate_position_insulation(limit_cp_bordes: float, db: Session, project_id: Optional[int] = None) -> None:
    """
    Recalcula y actualiza 'position_insulation' en Formulas.atributs para todas las fórmulas del proyecto.
    Agrupa por item_id para calcular una sola vez por detalle.
    """
    formulas = (
        db.query(Formulas)
        .filter(Formulas.project_id == project_id, Formulas.type == "details")
        .all()
    )
    if not formulas:
        print("⚠️ No hay detalles válidos para recalcular en el proyecto.")
        return

    # Agrupar por item_id
    formulas_by_detail: Dict[int, List[Formulas]] = {}
    for f in formulas:
        formulas_by_detail.setdefault(f.item_id, []).append(f)

    # Calcular y aplicar
    for id_detail, group in formulas_by_detail.items():
        pos = calculate_position_insulation(id_detail, limit_cp_bordes, db, project_id)
        for f in group:
            f.atributs = {**f.atributs, "position_insulation": pos}
            flag_modified(f, "atributs")

    db.commit()


# =========================
# Detalles (cálculos por grupo)
# =========================
def calculate_details_part(
    db: Session,
    section: str,
    project_id: Optional[int] = None,
    edited_detail_id: Optional[int] = None,
    name_detail: Optional[str] = None,
    scantilon_location: Optional[str] = None,
    *,
    debug: bool = True
) -> None:
    if section != "user":
        project_id = None

    if debug:
        print("=== [calculate_details_part] START ===")
        print(f"[ctx] section={section} project_id={project_id} edited_detail_id={edited_detail_id} "
              f"name_detail={name_detail} scantilon_location={scantilon_location}")

    # Para evitar cache desactualizada si vienes de inserts/updates previos
    db.flush(); db.expire_all()

    # ----- 1) Determinar claves de grupo afectadas -----
    group_keys: set[Tuple[str, str]] = set()
    if edited_detail_id:
        detail = db.query(Detail).filter(Detail.id == edited_detail_id).one_or_none()
        if detail:
            group_keys.add((detail.scantilon_location, detail.name_detail))
            if scantilon_location and name_detail and (scantilon_location, name_detail) != (
                detail.scantilon_location, detail.name_detail
            ):
                group_keys.add((scantilon_location, name_detail))
        else:
            if name_detail and scantilon_location:
                group_keys.add((scantilon_location, name_detail))
            else:
                raise HTTPException(status_code=404, detail="Detalle no encontrado para edición o eliminación.")
    else:
        groups = (
            db.query(Detail.scantilon_location, Detail.name_detail)
              .join(Formulas, Formulas.item_id == Detail.id)
              .filter(Formulas.project_id == project_id, Formulas.type == "details")
              .distinct()
              .all()
        )
        group_keys = set(groups)

    if debug:
        print(f"[groups] count={len(group_keys)} -> {list(group_keys)}")

    if not group_keys:
        if debug: print("⚠️ [groups] vacío. END.")
        return

    # ----- 2) Traer formulas/calculations de los grupos -----
    group_conditions = or_(*[and_(Detail.scantilon_location == loc, Detail.name_detail == name)
                             for loc, name in group_keys])
    formulas_all = (
        db.query(Detail.scantilon_location, Detail.name_detail, Calculation.values)
          .join(Formulas, Formulas.item_id == Detail.id)
          .join(Calculation, Calculation.reference_id == Detail.id)
          .filter(
              Formulas.project_id == project_id,
              Formulas.type == "details",
              Calculation.type == "details",
              Calculation.name == "generals",
              group_conditions,
          )
          .all()
    )

    if debug:
        print(f"[formulas_all] rows={len(formulas_all)}")

    formulas_grouped: Dict[Tuple[str, str], List[Dict]] = {}
    for loc, name, calc_values in formulas_all:
        formulas_grouped.setdefault((loc, name), []).append(calc_values)

    if debug:
        for key in group_keys:
            rows = formulas_grouped.get(key, [])
            print(f"  [group {key}] calc_rows={len(rows)} r_sum={sum(v.get('r',0.0) for v in rows)}")

    # ----- 3) Cargar DetailPart existentes -----
    dp_conditions = or_(*[and_(DetailPart.type == loc, DetailPart.name_detail == name) for loc, name in group_keys])
    existing_dp = (
        db.query(DetailPart)
          .populate_existing()
          .filter(DetailPart.project_id == project_id, dp_conditions)
          .all()
    )
    dp_map: Dict[Tuple[str, str], DetailPart] = {(dp.type, dp.name_detail): dp for dp in existing_dp}

    if debug:
        print(f"[detail_parts existing] count={len(existing_dp)} keys={list(dp_map.keys())}")

    grupos_con_cambio: List[Tuple[str, str]] = []

    # ----- 4) Iterar grupos y actualizar/crear DetailPart -----
    for key in group_keys:
        location, name = key
        records = formulas_grouped.get(key, [])
        total_r = sum(v.get("r", 0.0) for v in records)

        if location == "Muro":
            rsi, rse = 0.13, 0.04
            default_info = {"surface_color": {
                "interior": {"name": "Intermedio", "value": 0.6},
                "exterior": {"name": "Intermedio", "value": 0.6},
            }}
        elif location == "Techo":
            rsi, rse = 0.09, 0.04
            default_info = {"surface_color": {
                "interior": {"name": "Intermedio", "value": 0.6},
                "exterior": {"name": "Intermedio", "value": 0.6},
            }}
        elif location == "Piso":
            rsi, rse = 0.17, 0.04
            lam, e_aisl = calculate_aislacion_bajo_piso(project_id, name, location, db)
            piso_default_info = {
                "aislacion_bajo_piso": {"lambda": lam, "e_aisl": e_aisl},
                "ref_aisl_vertical": {"lambda": 0, "e_aisl": 0, "d": 0},
                "ref_aisl_horizontal": {"lambda": 0, "e_aisl": 0, "d": 0},
            }
        else:
            rsi, rse = 0.0, 0.0
            default_info = {}

        denom = (rsi + rse + total_r)
        value_u = 1 / denom if denom > 0 else 0.0

        if debug:
            print(f"  [iter {key}] rsi={rsi} rse={rse} total_r={total_r} -> value_u={value_u} records={len(records)}")

        if not records:
            if key in dp_map:
                dp = dp_map[key]
                if debug: print(f"    [DP update] set value_u=0 (no records) prev={dp.value_u}")
                dp.value_u = 0
        else:
            if key in dp_map:
                dp = dp_map[key]
                if debug: print(f"    [DP update] {key} value_u: {dp.value_u} -> {value_u}")
                dp.value_u = value_u
                if location == "Piso":
                    info = dp.info or {}
                    info["aislacion_bajo_piso"] = {"lambda": lam, "e_aisl": e_aisl}
                    if debug: print(f"    [DP info/Piso] aisl_bajo_piso={{'lambda': {lam}, 'e_aisl': {e_aisl}}}")
                    dp.info = info
                    flag_modified(dp, "info")
            else:
                info_to_use = piso_default_info if location == "Piso" else default_info
                new_dp = DetailPart(
                    project_id=project_id,
                    type=location,
                    name_detail=name,
                    value_u=value_u,
                    info=info_to_use,
                )
                db.add(new_dp)
                dp_map[key] = new_dp
                if debug: print(f"    [DP create] {key} value_u={value_u}")

        grupos_con_cambio.append(key)

    db.commit()
    if debug: print("[commit] value_u/info persisted")

    # ----- 5) Recalcular posición primero (Formulas) -----
    db.flush(); db.expire_all()
    limit_cp_bordes_new = (
        db.query(cast(Constant.atributs["light_for_edge_layer"].astext, Float))
          .filter(Constant.name == "generals", Constant.type == "details")
          .scalar()
        or 0.0
    )
    if debug: print(f"[limits] light_for_edge_layer={limit_cp_bordes_new}")

    recalculate_position_insulation(float(limit_cp_bordes_new), db, project_id=project_id)
    db.commit()
    if debug: print("[commit] position_insulation updated in Formulas")

    # ----- 6) Extras por grupo (usa Formulas ya actualizadas) -----
    db.flush(); db.expire_all()
    for location, name in grupos_con_cambio:
        if debug: print(f"[extras] calc for {(location, name)}")
        calculate_details_part_extras(
            project_id=project_id,
            name_detail=name,
            scantilon_location=location,
            db=db,
            limites_cp_liviano=75_000,
            limites_cp_pesado=175_000,
        )
    db.commit()
    if debug:
        print("[commit] extras persisted")
        print("=== [calculate_details_part] END ===")



# =========================
# Piso: aislación bajo piso
# =========================
def calculate_aislacion_bajo_piso(
    project_id: int,
    name_detail: str,
    scantilon_location: str,
    db: Session,
):
    """
    Suma lambda (conductividad) y espesor total de capas con is_insulation == 1 para un Piso.
    Mantiene prints para depuración.
    """
    # Ids de detalles aislantes (is_insulation == 1)
    insulated_detail_ids_rows = (
        db.query(Detail.id)
        .filter(Detail.scantilon_location == scantilon_location)
        .filter(
            Detail.id.in_(
                db.query(Calculation.reference_id)
                .filter(Calculation.type == "details", Calculation.name == "generals")
                .filter(coalesce_float(cast(Calculation.values["is_insulation"].cast(Text), Integer), 0) == 1)
            )
        )
        .all()
    )
    insulated_detail_ids = {row[0] for row in insulated_detail_ids_rows} if insulated_detail_ids_rows else set()
    print("\nInsulated Detail IDs:", insulated_detail_ids)
    if not insulated_detail_ids:
        return None

    # Conductividades
    material_conductivities = (
        db.query(
            Constant.id,
            cast(Constant.atributs["conductivity"].cast(Text), Float),
        )
        .filter(Constant.name == "materials")
        .filter(
            Constant.id.in_(
                db.query(Detail.material_id)
                .filter(Detail.name_detail == name_detail)
                .filter(Detail.scantilon_location == scantilon_location)
                .filter(Detail.id.in_(insulated_detail_ids))
                .filter(
                    Detail.id.in_(
                        db.query(Formulas.item_id).filter(
                            Formulas.project_id == project_id, Formulas.type == "details"
                        )
                    )
                )
            )
        )
        .all()
    )
    print("\nMaterial Conductivities:", material_conductivities)

    lambda_total = sum(c for _, c in material_conductivities if c is not None)
    print("\nTotal Lambda:", lambda_total)

    # Espesores
    detail_thicknesses = (
        db.query(Detail.id, cast(Detail.layer_thickness.cast(Text), Float))
        .filter(Detail.name_detail == name_detail)
        .filter(Detail.scantilon_location == scantilon_location)
        .filter(Detail.id.in_(insulated_detail_ids))
        .filter(
            Detail.id.in_(
                db.query(Formulas.item_id).filter(Formulas.project_id == project_id, Formulas.type == "details")
            )
        )
        .all()
    )
    print("\nDetail Thicknesses:", detail_thicknesses)

    total_thickness = sum(t for _, t in detail_thicknesses if t is not None)
    print("\nTotal Layer Thickness:", total_thickness)

    return lambda_total, total_thickness


# =========================
# Extras por DetailPart
# =========================
def calculate_details_part_extras(
    project_id: int,
    name_detail: str,
    scantilon_location: str,
    db: Session,
    limites_cp_liviano: float,
    limites_cp_pesado: float,
):
    """
    Calcula:
      - espesor total de capas con k < 0.07 (tal como estaba),
      - fourier_nodes, km_op, conteo de madera,
      - clasificación CEEUP (EL/EI/EP o EM),
      - posición de aislante (leyenda),
    y guarda en DetailPart.calculations.
    """

    # Conductividades de materiales para el grupo
    material_conductivities = (
        db.query(
            Detail.id,
            Detail.layer_thickness,
            cast(Constant.atributs["conductivity"].astext, Float),
        )
        .join(Constant, Detail.material_id == Constant.id)
        .filter(Constant.name == "materials")
        .filter(Detail.name_detail == name_detail)
        .filter(Detail.scantilon_location == scantilon_location)
        .filter(
            Detail.id.in_(
                db.query(Formulas.item_id).filter(Formulas.project_id == project_id, Formulas.type == "details")
            )
        )
        .all()
    )
    if not material_conductivities:
        return None

    # NOTA: Mantengo el umbral 0.07 tal cual estaba en tu código original
    total_thickness = sum(
        thickness for _, thickness, conductivity in material_conductivities if conductivity and conductivity < 0.07
    )

    # Datos de Calculation para el grupo
    calculation_data = (
        db.query(
            json_float(Calculation.values, "fourier_nodes"),
            json_float(Calculation.values, "km_op"),
            json_int(Calculation.values, "is_wood"),
        )
        .filter(Calculation.type == "details")
        .filter(Calculation.project_id == project_id)
        .filter(
            Calculation.reference_id.in_(
                db.query(Detail.id)
                .filter(Detail.name_detail == name_detail, Detail.scantilon_location == scantilon_location)
                .filter(Detail.project_id == project_id)
            )
        )
        .all()
    )

    total_fourier_nodes = sum(row[0] for row in calculation_data if row[0] is not None)
    total_km_op = sum(row[1] for row in calculation_data if row[1] is not None)
    total_is_wood = sum(row[2] for row in calculation_data if row[2] is not None and row[2] >= 1)
    suma_km_op_wood = sum(row[1] for row in calculation_data if row[1] is not None and row[2] == 1)
    doble_suma_km_op_wood = 2 * suma_km_op_wood

    # Clasificación
    if total_is_wood >= 1 and doble_suma_km_op_wood > total_km_op:
        classification = "EM"
    elif total_km_op <= limites_cp_liviano:
        classification = "EL"
    elif total_km_op >= limites_cp_pesado:
        classification = "EP"
    else:
        classification = "EI"

    # Suma de position_insulation (numérica)
    total_position_insulation = (
        db.query(
            func.coalesce(func.sum(cast(Formulas.atributs["position_insulation"].astext, Integer)), 0)
        )
        .filter(
            Formulas.project_id == project_id,
            Formulas.type == "details",
            Formulas.name == name_detail,
            # opcional pero recomendable: limitar a los Detail del mismo grupo
            Formulas.item_id.in_(
                db.query(Detail.id).filter(
                    Detail.project_id == project_id,
                    Detail.name_detail == name_detail,
                    Detail.scantilon_location == scantilon_location,
                )
            ),
        )
        .scalar()
    )
    print("Nombre Detalle: ", name_detail)
    print("total position insulation: ", total_position_insulation)

    # Leyenda/categoría a partir del total (usa eval tal como tenías)
    insulation_category = (
        db.query(cast(Constant.atributs["insulation_position"].astext, String))
        .filter(Constant.name == "generals", Constant.type == "details")
        .scalar()
    )
    if insulation_category:
        insulation_category = eval(insulation_category).get(str(total_position_insulation), "sa")

    # Guardar en DetailPart.calculations
    detail_part = (
        db.query(DetailPart)
        .filter(
            DetailPart.project_id == project_id,
            DetailPart.name_detail == name_detail,
            DetailPart.type == scantilon_location,
        )
        .first()
    )
    
    
    print(f"[DEBUG] Nombre Detalle: {name_detail}")
    print(f"[DEBUG] total_thickness: {total_thickness}")
    print(f"[DEBUG] total_fourier_nodes: {total_fourier_nodes}")
    print(f"[DEBUG] total_km_op: {total_km_op}")
    print(f"[DEBUG] total_is_wood: {total_is_wood}")
    print(f"[DEBUG] suma_km_op_wood: {suma_km_op_wood}")
    print(f"[DEBUG] doble_suma_km_op_wood: {doble_suma_km_op_wood}")
    print(f"[DEBUG] classification: {classification}")
    print(f"[DEBUG] total_position_insulation: {total_position_insulation}")
    print(f"[DEBUG] insulation_category: {insulation_category}")
    print()
        
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
            "position_insulation": insulation_category,
        }

    return None


# =========================
# Cálculos generales de un Detail
# =========================
def calculate_details_generals(detail_id: int, db: Session, project_id: Optional[int] = None) -> None:
    """
    Crea/actualiza Calculation (type='details', name='generals') para el Detail dado.
    No cambia la lógica original.
    """
    detail = db.query(Detail).filter(Detail.id == detail_id).one_or_none()
    if not detail:
        raise HTTPException(status_code=404, detail="Detalle no encontrado.")

    # Material base
    if detail.material_id == 0:
        conductivity = density = specific_heat = 0
    else:
        material = db.query(Constant).filter(Constant.id == detail.material_id).one_or_none()
        if not material:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró constante para el material ID {detail.material_id}",
            )
        conductivity = material.atributs.get("conductivity")
        density = material.atributs.get("density")
        specific_heat = material.atributs.get("specific_heat")

    # Constantes generales
    constants = (
        db.query(Constant)
        .filter(Constant.name == "generals", Constant.type == "details")
        .first()
    )
    if not constants:
        print("⚠️ No se encontraron las constantes generales en la base de datos.")
        return

    try:
        f_ref = constants.atributs["Fourier"]["F_ref"]
        dt_fourier = constants.atributs["Fourier"]["dt_Fourier"]
        is_wood_data = {item["name"]: item["value"] for item in constants.atributs["is_wood"]}
        is_insulating_data = {item["name"]: item["value"] for item in constants.atributs["is_insulation"]}
    except (KeyError, TypeError):
        raise HTTPException(status_code=500, detail="Error al procesar las constantes generales.")

    # Cálculos
    if conductivity == 0:
        r_value = 0.0
        fourier_nodes = 0
        km_op = 0.0
        is_wood_ = 0
        is_insulating_ = 0
    else:
        r_value = (detail.layer_thickness / 100) / conductivity
        fourier_nodes = calculation_nodes_fourier(
            conductivity, density, specific_heat, detail.layer_thickness, f_ref, dt_fourier
        )
        km_op = calculation_km_op(specific_heat, density, detail.layer_thickness)
        is_wood_ = is_wood(detail.layer_thickness, conductivity, density, specific_heat, is_wood_data)
        is_insulating_ = is_insulating(conductivity, density, is_insulating_data)

    calc_values = {
        "r": r_value,
        "fourier_nodes": fourier_nodes,
        "km_op": km_op,
        "is_wood": is_wood_,
        "is_insulation": is_insulating_,
    }

    # Upsert de Calculation
    try:
        existing = (
            db.query(Calculation)
            .filter(
                Calculation.reference_id == detail.id,
                Calculation.type == "details",
                Calculation.name == "generals",
            )
            .one_or_none()
        )
        if existing:
            existing.values = calc_values
            existing.project_id = project_id
            flag_modified(existing, "values")
            print(f"🔄 Cálculo actualizado para Detail ID {detail.id}: R = {r_value}")
        else:
            new_calculation = Calculation(
                reference_id=detail.id,
                type="details",
                name="generals",
                values=calc_values,
                project_id=project_id,
            )
            db.add(new_calculation)
            print(f"✅ Nuevo cálculo agregado para Detail ID {detail.id}: R = {r_value}")

        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")


# =========================
# Borrado de cálculos por Detail
# =========================
def delete_calculations_for_detail(detail_id: int, db: Session):
    """Elimina todos los Calculation del Detail dado."""
    try:
        deleted = (
            db.query(Calculation)
            .filter(Calculation.reference_id == detail_id, Calculation.type == "details")
            .delete(synchronize_session=False)
        )
        db.commit()
        print(f"🗑️ Eliminados {deleted} cálculos para Detail ID {detail_id}.")
        return {"success": True, "message": f"Eliminados {deleted} cálculos para Detail ID {detail_id}"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar cálculos: {str(e)}")


# =========================
# Elemento puerta (cálculo U)
# =========================
def calculate_element_door(rsi_m: float, rse_m: float, element_door: Element, db: Session):
    """
    Calcula y guarda en element_door.calculations:
      - u_ponderado_opaco, u_vidrio, u_ponderado, r_puro
    Mantiene exactamente el mismo flujo y operaciones.
    """
    # Ventana asociada (opcional)
    ventana_id = element_door.atributs.get("ventana_id")
    window_asociate_door: Optional[Element] = None
    if ventana_id:
        window_asociate_door = db.query(Element).filter(Element.id == ventana_id).first()

    u_puerta_opaca = element_door.atributs.get("u_puerta_opaca", 0)
    porcentaje_vidrio = element_door.atributs.get("porcentaje_vidrio", 0)
    u_marco = element_door.u_marco
    fm = element_door.fm

    # U ponderado para la parte opaca (evitar /0)
    if (1 - porcentaje_vidrio) == 0:
        u_ponderado_opaco = 0
    else:
        u_ponderado_opaco = (u_puerta_opaca * (1 - porcentaje_vidrio - fm) + u_marco * fm) / (1 - porcentaje_vidrio)

    # U del vidrio si hay ventana asociada
    u_vidrio = window_asociate_door.atributs.get("u_vidrio", 0) if window_asociate_door else 0

    # U ponderado global
    u_ponderado = u_puerta_opaca * (1 - porcentaje_vidrio - fm) + (u_vidrio * porcentaje_vidrio) + (u_marco * fm)

    # Resistencia pura (evitando división por cero)
    r_puro = 0 if u_ponderado_opaco == 0 else 1 / u_ponderado_opaco - (rsi_m + rse_m)

    # Actualizar cálculos
    element_door.calculations.update(
        {
            "u_ponderado_opaco": u_ponderado_opaco,
            "u_vidrio": u_vidrio,
            "u_ponderado": u_ponderado,
            "r_puro": r_puro,
        }
    )
    flag_modified(element_door, "calculations")
    db.commit()
