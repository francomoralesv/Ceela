# create_details_part_fixed.py

import json
import logging
from typing import Optional, Tuple, Dict, Any, List
from sqlalchemy.exc import IntegrityError
import pandas as pd
from fastapi import HTTPException
from sqlalchemy import func, cast, Float, Integer, String, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

# Modelos (ajusta rutas según tu proyecto)
from src.models.entity.constant import Constant
from src.models.entity.details import Detail
from src.models.entity.formulas import Formulas
from src.models.entity.detail_part import DetailPart
from src.models.entity.calculations import Calculation
from src.seed.calculation import calculation_default_details

# Si ya tienes estos helpers en otro módulo y prefieres importarlos, elimina estas definiciones.
# from src.seed.calculate_details_part import calculate_aislacion_bajo_piso, calculate_details_part_extras

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==========================
# Utilidades de Cálculo Base
# ==========================

def calculate_km_op_acumulated(db: Session, detail: Detail) -> float:
    """
    Suma acumulada de km_op por grupo (scantilon_location, name_detail) ordenado por Detail.id.
    project_id == None (seed/admin).
    """
    subq = (
        db.query(
            Calculation.reference_id,
            func.sum(
                cast(Calculation.values["km_op"].astext, Float)
            ).over(
                order_by=Detail.id,
                partition_by=[Detail.scantilon_location, Detail.name_detail]
            ).label("km_op_acumulated"),
        )
        .join(Detail, Calculation.reference_id == Detail.id)
        .filter(
            Calculation.type == "details",
            Calculation.name == "generals",
            Detail.scantilon_location == detail.scantilon_location,
            Detail.name_detail == detail.name_detail,
        )
        .subquery()
    )

    value = (
            db.query(subq.c.km_op_acumulated)
            .filter(subq.c.reference_id == detail.id)
            .scalar()
            or 0.0
    )
    return float(value)


def calculate_position_insulation(id_detail: int, limit_cp_bordes: float, db: Session) -> int:
    """
    Calcula la posición del aislante para un Detail específico (seed).
    Retorna: 0=sin aislante, 1=interior, 2=intermedio, 3=exterior.
    """
    detail_data = (
        db.query(
            Detail.name_detail,
            func.coalesce(cast(Calculation.values["is_insulation"].astext, Float), 0.0),
        )
        .outerjoin(
            Calculation,
            and_(
                Calculation.type == "details",
                Calculation.name == "generals",
                Calculation.reference_id == id_detail,
            ),
        )
        .filter(Detail.id == id_detail)
        .first()
    )
    if not detail_data:
        return 0

    name_detail, is_insulation = detail_data
    if float(is_insulation or 0.0) == 0.0:
        return 0

    sum_is_insulation, sum_km_op = (
            db.query(
                func.coalesce(func.sum(cast(Calculation.values["is_insulation"].astext, Float)), 0.0),
                func.coalesce(func.sum(cast(Calculation.values["km_op"].astext, Float)), 0.0),
            )
            .join(Formulas, Formulas.item_id == Calculation.reference_id)
            .filter(
                Calculation.type == "details",
                Calculation.name == "generals",
                Formulas.type == "details",
                Formulas.project_id.is_(None),
                Formulas.item_id.in_(db.query(Detail.id).filter(Detail.name_detail == name_detail)),
            )
            .first()
            or (0.0, 0.0)
    )

    if sum_is_insulation == 0.0 or sum_km_op == 0.0:
        return 0

    km_op_acumulated = (
            db.query(func.coalesce(cast(Formulas.atributs["km_op_acumulated"].astext, Float), 0.0))
            .filter(Formulas.project_id.is_(None), Formulas.type == "details", Formulas.item_id == id_detail)
            .scalar()
            or 0.0
    )

    if km_op_acumulated < (limit_cp_bordes * sum_km_op):
        return 1
    elif km_op_acumulated > ((1 - limit_cp_bordes) * sum_km_op):
        return 3
    return 2


def recalculate_position_insulation_user(project_id: int, limit_cp_bordes: float, db: Session) -> None:
    """
    Recalcula position_insulation para todos los Details de un proyecto (modo usuario).
    """
    ids = [r[0] for r in
           db.query(Formulas.item_id).filter(Formulas.project_id == project_id, Formulas.type == "details").all()]
    if not ids:
        logger.info("⚠️ No hay detalles válidos para recalcular en el proyecto.")
        return

    # Cache atributos actuales para no perder otras claves
    info_map: Dict[int, Dict[str, Any]] = {
        det_id: f.atributs
        for det_id, f in db.query(Formulas.item_id, Formulas).filter(
            Formulas.project_id == project_id, Formulas.type == "details"
        ).all()
    }

    for det_id in ids:
        pos = calculate_position_insulation(det_id, limit_cp_bordes, db)
        formula = (
            db.query(Formulas)
            .filter(Formulas.project_id == project_id, Formulas.item_id == det_id, Formulas.type == "details")
            .first()
        )
        if formula:
            formula.atributs = {**(info_map.get(det_id, {}) or {}), "position_insulation": pos}
            flag_modified(formula, "atributs")
    db.commit()


def recalculate_position_insulation_seed(limit_cp_bordes: float, db: Session) -> None:
    """
    Recalcula position_insulation para todos los Details en seed/admin (project_id == None).
    """
    ids = [r[0] for r in
           db.query(Formulas.item_id).filter(Formulas.project_id.is_(None), Formulas.type == "details").all()]
    if not ids:
        logger.info("⚠️ No hay detalles válidos para recalcular en seed.")
        return

    info_map: Dict[int, Dict[str, Any]] = {
        det_id: f.atributs
        for det_id, f in db.query(Formulas.item_id, Formulas).filter(
            Formulas.project_id.is_(None), Formulas.type == "details"
        ).all()
    }

    for det_id in ids:
        pos = calculate_position_insulation(det_id, limit_cp_bordes, db)
        formula = (
            db.query(Formulas)
            .filter(Formulas.project_id.is_(None), Formulas.item_id == det_id, Formulas.type == "details")
            .first()
        )
        if formula:
            formula.atributs = {**(info_map.get(det_id, {}) or {}), "position_insulation": pos}
            flag_modified(formula, "atributs")
    db.commit()


# ======================================
# Aislación y Extras (portados y pulidos)
# ======================================

def calculate_aislacion_bajo_piso(
        project_id: Optional[int],
        name_detail: str,
        scantilon_location: str,
        db: Session,
) -> Optional[Tuple[float, float]]:
    """
    Calcula aislación bajo piso considerando materiales con is_insulation == 1.
    Retorna (total_conductivity, total_thickness_aislante<0.07).
    Para seed: project_id == None.
    """
    insulated_ids = db.query(Detail.id).filter(
        Detail.scantilon_location == scantilon_location,
        Detail.id.in_(
            db.query(Calculation.reference_id).filter(
                Calculation.type == "details",
                Calculation.name == "generals",
                func.coalesce(cast(Calculation.values["is_insulation"].astext, Integer), 0) == 1,
            )
        ),
    ).all()
    id_set = {r[0] for r in insulated_ids} if insulated_ids else set()
    if not id_set:
        return None

    rows = (
        db.query(
            Detail.id,
            Detail.layer_thickness,
            cast(Constant.atributs["conductivity"].astext, Float),
        )
        .join(Constant, Detail.material_id == Constant.id)
        .filter(
            Constant.name == "materials",
            Detail.name_detail == name_detail,
            Detail.scantilon_location == scantilon_location,
            Detail.id.in_(id_set),
            Detail.id.in_(
                db.query(Formulas.item_id).filter(Formulas.project_id.is_(project_id), Formulas.type == "details")
            ),
        )
        .all()
    )
    total_thickness = sum(t for _, t, k in rows if k is not None and k < 0.07)  # umbral unificado
    total_conductivity = sum(k for _, _, k in rows if k is not None)
    return (total_conductivity, total_thickness)


def calcular_ifc(
        db: Session,
        name_detail: str,
        detail_type: str,
        overwrite: bool = False,
        max_retries: int = 5,
) -> DetailPart:
    """
    Upsert de code_ifc para DetailPart (project_id=None).

    - Si NO existe el DetailPart (detail_type, name_detail): lo crea con code_ifc correlativo.
    - Si SÍ existe:
        * Si overwrite=True, o code_ifc está vacío/NULL -> asigna un correlativo nuevo y persiste.
        * Si overwrite=False y ya tiene code_ifc -> NO lo toca.

    Retorna el DetailPart persistido.
    """
    if detail_type not in ("Muro", "Techo", "Piso"):
        raise HTTPException(status_code=400, detail="detail_type inválido (Muro/Techo/Piso).")

    prefix_map = {"Muro": "MURO", "Techo": "TECHO", "Piso": "PISO"}
    prefix = prefix_map[detail_type]

    def _next_code_ifc() -> str:
        rows = (
            db.query(DetailPart.code_ifc)
            .filter(DetailPart.project_id.is_(None))
            .filter(DetailPart.code_ifc.isnot(None))
            .filter(DetailPart.code_ifc != "")
            .filter(DetailPart.code_ifc.like(f"{prefix}_%"))
            .all()
        )
        nums = []
        for (code,) in rows:
            parts = code.split("_")
            if len(parts) == 2 and parts[1].isdigit():
                nums.append(int(parts[1]))
        next_num = (max(nums) + 1) if nums else 1
        return f"{prefix}_{next_num:03d}"

    # buscar existente por grupo (seed)
    dp = (
        db.query(DetailPart)
        .filter(
            DetailPart.project_id.is_(None),
            DetailPart.type == detail_type,
            DetailPart.name_detail == name_detail,
        )
        .first()
    )

    try:
        if dp:
            needs_update = overwrite or not dp.code_ifc or dp.code_ifc.strip() == ""
            if not needs_update:
                return dp

            # asignar correlativo nuevo con reintentos por colisión UNIQUE
            attempts = 0
            while True:
                attempts += 1
                dp.code_ifc = _next_code_ifc()
                try:
                    db.commit()
                    db.refresh(dp)
                    break
                except IntegrityError:
                    db.rollback()
                    if attempts >= max_retries:
                        raise HTTPException(
                            status_code=500,
                            detail="No se pudo actualizar code_ifc (colisiones repetidas).",
                        )
            return dp

        # crear nuevo si no existe
        code_ifc = _next_code_ifc()
        dp = DetailPart(
            project_id=None,
            type=detail_type,
            name_detail=name_detail,
            code_ifc=code_ifc,
        )
        db.add(dp)
        db.commit()
        db.refresh(dp)
        return dp

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en calcular_ifc: {e}")


def calculate_details_part_extras(
        db: Session,
        name_detail: str,
        scantilon_location: str,
        limites_cp_liviano: float,
        limites_cp_pesado: float,
) -> Dict[str, Any]:
    """
    Calcula extras de DetailPart: espesor_aislacion, fourier_nodes, km_op, cat_ceeup, position_insulation (categoría).
    Usa project_id == None.
    """
    # Espesor aislante por conductividad < 0.07
    mat_rows = (
        db.query(
            Detail.id,
            Detail.layer_thickness,
            cast(Constant.atributs["conductivity"].astext, Float),
        )
        .join(Constant, Detail.material_id == Constant.id)
        .filter(
            Constant.name == "materials",
            Detail.name_detail == name_detail,
            Detail.scantilon_location == scantilon_location,
            Detail.id.in_(db.query(Formulas.item_id).filter(Formulas.project_id.is_(None), Formulas.type == "details")),
        )
        .all()
    )
    espesor_aisl = sum(t for _, t, k in mat_rows if k is not None and k < 0.07)

    # Datos de cálculos
    calc_rows = (
        db.query(
            cast(Calculation.values["fourier_nodes"].astext, Float),
            cast(Calculation.values["km_op"].astext, Float),
            cast(Calculation.values["is_wood"].astext, Integer),
        )
        .filter(
            Calculation.type == "details",
            Calculation.name == "generals",
            Calculation.reference_id.in_(
                db.query(Detail.id).filter(
                    Detail.name_detail == name_detail,
                    Detail.scantilon_location == scantilon_location,
                )
            ),
        )
        .all()
    )
    total_fourier_nodes = sum(x for x, _, _ in calc_rows if x is not None)
    total_km_op = sum(y for _, y, _ in calc_rows if y is not None)
    total_is_wood = sum(z for _, _, z in calc_rows if z is not None and z >= 1)
    suma_km_op_wood = sum(y for _, y, z in calc_rows if y is not None and z == 1)
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

    # position_insulation -> categoría por suma
    total_position_insulation = (
            db.query(func.sum(cast(Formulas.atributs["position_insulation"].astext, Integer)))
            .filter(
                Formulas.project_id.is_(None),
                Formulas.type == "details",
                Formulas.item_id.in_(
                    db.query(Detail.id).filter(
                        Detail.name_detail == name_detail, Detail.scantilon_location == scantilon_location
                    )
                ),
            )
            .scalar()
            or 0
    )

    raw_ins_cat = (
        db.query(cast(Constant.atributs["insulation_position"].astext, String))
        .filter(Constant.name == "generals", Constant.type == "details")
        .scalar()
    )
    ins_cat_map: Dict[str, str] = {}
    if raw_ins_cat:
        try:
            ins_cat_map = json.loads(raw_ins_cat)
        except Exception:
            ins_cat_map = {}
    ins_category = ins_cat_map.get(str(total_position_insulation), "Desconocido")

    # Upsert parcial en DetailPart.calculations (si existe)
    dp = (
        db.query(DetailPart)
        .filter(
            DetailPart.project_id.is_(None),
            DetailPart.name_detail == name_detail,
            DetailPart.type == scantilon_location,
        )
        .first()
    )
    result = {
        "espesor_aislacion": espesor_aisl,
        "fourier_nodes": total_fourier_nodes,
        "km_op": total_km_op,
        "cat_ceeup": classification,
        "position_insulation": ins_category,
    }
    if dp:
        if not dp.calculations:
            dp.calculations = {}
        dp.calculations.update(result)
        flag_modified(dp, "calculations")
    return result


def update_detail_part_for_group(db: Session, location: str, name_detail: str) -> None:
    """
    (location, name_detail), seed: calcula U y extras y actualiza/crea DetailPart.
    """
    rows = (
        db.query(Detail.scantilon_location, Detail.name_detail, Calculation.values)
        .join(Calculation, Calculation.reference_id == Detail.id)
        .filter(
            Detail.project_id.is_(None),
            Detail.scantilon_location == location,
            Detail.name_detail == name_detail,
            Calculation.type == "details",
            Calculation.name == "generals",
        )
        .all()
    )
    if not rows:
        logger.info(f"No hay registros para DetailPart ({location}, {name_detail}).")
        return

    r_sum = 0.0
    for _, _, vals in rows:
        if isinstance(vals, dict):
            r_sum += float(vals.get("r", 0.0) or 0.0)

    const_color = db.query(Constant).filter(Constant.type == "details", Constant.name == "generals").first()
    surface_colors = const_color.atributs.get("surface_color", {}) if const_color else {}

    const_res = db.query(Constant).filter(Constant.type == "elements", Constant.name == "generals").first()
    tr = const_res.atributs.get("thermal_resistances", {}) if const_res else {}

    if location == "Muro":
        info = {
            "surface_color": {
                "interior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                "exterior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
            }
        }
        rsi, rse = float(tr.get("rsi_wall", 0.13)), float(tr.get("rse_wall", 0.04))
    elif location == "Techo":
        info = {
            "surface_color": {
                "interior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                "exterior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
            }
        }
        rsi, rse = float(tr.get("rsi_roof", 0.09)), float(tr.get("rse_roof", 0.04))
    elif location == "Piso":
        aislacion = calculate_aislacion_bajo_piso(None, name_detail, location, db) or (0.0, 0.0)
        lambda_val, e_aisl = aislacion
        info = {
            "aislacion_bajo_piso": {"lambda": lambda_val, "e_aisl": e_aisl},
            "ref_aisl_vertical": {"lambda": 0.0, "e_aisl": 0.0, "d": 0.0},
            "ref_aisl_horizontal": {"lambda": 0.0, "e_aisl": 0.0, "d": 0.0},
        }
        rsi, rse = float(tr.get("rsi_floor", 0.17)), float(tr.get("rse_floor", 0.04))
    else:
        info = {}
        rsi = rse = 0.0

    denom = rsi + rse + r_sum
    value_u = (1.0 / denom) if denom != 0 else 0.0

    extras = calculate_details_part_extras(
        db, name_detail=name_detail, scantilon_location=location, limites_cp_liviano=75_000, limites_cp_pesado=175_000
    )

    existing = (
        db.query(DetailPart)
        .filter(DetailPart.project_id.is_(None), DetailPart.type == location, DetailPart.name_detail == name_detail)
        .first()
    )
    try:
        if existing:
            existing.value_u = value_u
            existing.info = info
            existing.calculations = extras
            flag_modified(existing, "info")
            flag_modified(existing, "calculations")
        else:
            new_dp = DetailPart(
                project_id=None,
                type=location,
                name_detail=name_detail,
                value_u=value_u,
                info=info,
                calculations=extras,
            )
            db.add(new_dp)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar/inserción en DetailPart: {e}")
        raise


# ==========================================
# Recalcular DetailPart (dual signature)
# ==========================================

def calculate_details_part_seed(
        db: Session,
        detail_type: Optional[str] = None,
        name_detail: Optional[str] = None,
        edited_detail_id: Optional[int] = None,
) -> None:
    """
    Modo 1 (por grupo): pasa detail_type y name_detail (y opcional edited_detail_id) -> recalcula solo ese grupo.
      - Si edited_detail_id está presente: SOBRESCRIBE (update/insert) el DetailPart del grupo.
      - Si edited_detail_id es None: NO sobrescribe si ya existe; solo crea si no existe.

    Modo 2 (global seed): no pases detail_type/name_detail -> recalcula todos los grupos del seed.
      - Si edited_detail_id está presente: borra/recacula ese grupo.
      - Si edited_detail_id es None y ya existe algún DetailPart seed: retorna (no sobrescribe).
    """
    if detail_type and name_detail:
        # ======= MODO GRUPO =======
        update_allowed = edited_detail_id is not None

        if edited_detail_id:
            # borrar el DP del grupo del detail editado (para recrearlo limpio)
            det = (
                db.query(Detail)
                .filter(
                    Detail.id == edited_detail_id,
                    Detail.project_id.is_(None),
                    Detail.created_status == "default",
                    Detail.scantilon_location == detail_type,
                    Detail.name_detail == name_detail,
                )
                .first()
            )
            if not det:
                raise HTTPException(status_code=404, detail="Detalle no encontrado para edición.")
            db.query(DetailPart).filter(
                DetailPart.name_detail == name_detail,
                DetailPart.project_id.is_(None),
                DetailPart.type == detail_type,
            ).delete(synchronize_session=False)
            db.commit()

        # IDs del grupo
        selected_ids = [
            r[0]
            for r in db.query(Detail.id)
            .join(Formulas, Formulas.item_id == Detail.id)
            .filter(
                Formulas.project_id.is_(None),
                Formulas.type == "details",
                Detail.created_status == "default",
                Detail.scantilon_location == detail_type,
                Detail.name_detail == name_detail,
            )
            .all()
        ]
        if not selected_ids:
            raise HTTPException(status_code=400, detail="No se encontraron detalles para recalcular (grupo).")

        # r_sum
        r_sum = (
                db.query(func.coalesce(func.sum(cast(Calculation.values["r"].astext, Float)), 0.0))
                .filter(
                    Calculation.type == "details",
                    Calculation.name == "generals",
                    Calculation.reference_id.in_(selected_ids),
                )
                .scalar()
                or 0.0
        )
        r_sum = float(r_sum)

        # constantes
        const_color = db.query(Constant).filter(Constant.type == "details", Constant.name == "generals").first()
        surface_colors = const_color.atributs.get("surface_color", {}) if const_color else {}
        const_res = db.query(Constant).filter(Constant.type == "elements", Constant.name == "generals").first()
        tr = const_res.atributs.get("thermal_resistances", {}) if const_res else {}

        if detail_type == "Muro":
            info = {
                "surface_color": {
                    "interior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                    "exterior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                }
            }
            rsi, rse = float(tr.get("rsi_wall", 0.13)), float(tr.get("rse_wall", 0.04))
        elif detail_type == "Techo":
            info = {
                "surface_color": {
                    "interior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                    "exterior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                }
            }
            rsi, rse = float(tr.get("rsi_roof", 0.09)), float(tr.get("rse_roof", 0.04))
        elif detail_type == "Piso":
            lambda_val, e_aisl = calculate_aislacion_bajo_piso(None, name_detail, detail_type, db) or (0.0, 0.0)
            info = {
                "aislacion_bajo_piso": {"lambda": lambda_val, "e_aisl": e_aisl},
                "ref_aisl_vertical": {"lambda": 0.0, "e_aisl": 0.0, "d": 0.0},
                "ref_aisl_horizontal": {"lambda": 0.0, "e_aisl": 0.0, "d": 0.0},
            }
            rsi, rse = float(tr.get("rsi_floor", 0.17)), float(tr.get("rse_floor", 0.04))
        else:
            info = {}
            rsi = rse = 0.0

        denom = rsi + rse + r_sum
        value_u = (1.0 / denom) if denom != 0 else 0.0

        # Upsert DP con política "solo sobrescribir si edited_detail_id"
        did_write = False
        dp = (
            db.query(DetailPart)
            .filter(DetailPart.project_id.is_(None), DetailPart.type == detail_type,
                    DetailPart.name_detail == name_detail)
            .first()
        )
        if dp:
            if update_allowed:
                dp.value_u = value_u
                dp.info = info
                flag_modified(dp, "info")
                did_write = True
            else:
                # No tocar registros existentes si no estamos en edición
                logger.info(
                    f"ℹ️ DetailPart existente para ({detail_type}, {name_detail}); no se sobrescribe (sin edited_detail_id).")
                return
        else:
            # No existe: crear siempre (esto no es "sobrescribir")
            dp = DetailPart(project_id=None, type=detail_type, name_detail=name_detail, value_u=value_u, info=info)
            db.add(dp)
            did_write = True

        try:
            if did_write:
                db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al recalcular DetailPart (grupo): {e}")

        # extras: solo si hubo escritura
        if did_write:
            try:
                calculate_details_part_extras(
                    db=db,
                    name_detail=name_detail,
                    scantilon_location=detail_type,
                    limites_cp_liviano=75_000,
                    limites_cp_pesado=175_000,
                )
                db.commit()
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Error finalizando extras (grupo): {e}")

            logger.info(f"✅ Recalculado DetailPart grupo: ({detail_type}, {name_detail}).")
        return

    # ======= MODO GLOBAL (SEED) =======
    if edited_detail_id:
        det = (
            db.query(Detail)
            .filter(Detail.id == edited_detail_id, Detail.project_id.is_(None), Detail.created_status == "default")
            .first()
        )
        if not det:
            raise HTTPException(status_code=404, detail="Detalle no encontrado.")
        db.query(DetailPart).filter(DetailPart.name_detail == det.name_detail, DetailPart.project_id.is_(None)).delete(
            synchronize_session=False
        )
        db.commit()
    else:
        existing = db.query(DetailPart).filter(DetailPart.project_id.is_(None)).first()
        if existing:
            logger.info("✅ DetailPart ya calculado (seed). Se omite recalculación global.")
            return

    # IDs seed
    seed_ids = [
        r[0]
        for r in db.query(Detail.id)
        .join(Formulas, Formulas.item_id == Detail.id)
        .filter(Formulas.project_id.is_(None), Formulas.type == "details", Detail.created_status == "default")
        .all()
    ]
    if not seed_ids:
        raise HTTPException(status_code=400, detail="No se encontraron detalles para recalcular (seed).")

    details = (
        db.query(Detail.scantilon_location, Detail.name_detail, Calculation.values)
        .join(Formulas, Formulas.item_id == Detail.id)
        .join(Calculation, Calculation.reference_id == Detail.id)
        .filter(
            Formulas.project_id.is_(None),
            Formulas.type == "details",
            Detail.id.in_(seed_ids),
            Calculation.type == "details",
            Calculation.name == "generals",
        )
        .all()
    )
    if not details:
        raise HTTPException(status_code=400, detail="No hay detalles seleccionados (seed).")

    groups: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for loc, name, vals in details:
        key = (loc, name)
        if key not in groups:
            groups[key] = {"type": loc, "name_detail": name, "r_sum": 0.0, "info": {}, "value_u": 0.0}
        if isinstance(vals, dict):
            groups[key]["r_sum"] += float(vals.get("r", 0.0) or 0.0)

    const_color = db.query(Constant).filter(Constant.type == "details", Constant.name == "generals").first()
    surface_colors = const_color.atributs.get("surface_color", {}) if const_color else {}
    const_res = db.query(Constant).filter(Constant.type == "elements", Constant.name == "generals").first()
    tr = const_res.atributs.get("thermal_resistances", {}) if const_res else {}

    for (loc, name), data in groups.items():
        if loc == "Muro":
            data["info"] = {
                "surface_color": {
                    "interior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                    "exterior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                }
            }
            rsi, rse = float(tr.get("rsi_wall", 0.13)), float(tr.get("rse_wall", 0.04))
        elif loc == "Techo":
            data["info"] = {
                "surface_color": {
                    "interior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                    "exterior": {"name": "Intermedio", "value": surface_colors.get("Intermedio", 0.6)},
                }
            }
            rsi, rse = float(tr.get("rsi_roof", 0.09)), float(tr.get("rse_roof", 0.04))
        elif loc == "Piso":
            lambda_val, e_aisl = calculate_aislacion_bajo_piso(None, name, loc, db) or (0.0, 0.0)
            data["info"] = {
                "aislacion_bajo_piso": {"lambda": lambda_val, "e_aisl": e_aisl},
                "ref_aisl_vertical": {"lambda": 0.0, "e_aisl": 0.0, "d": 0.0},
                "ref_aisl_horizontal": {"lambda": 0.0, "e_aisl": 0.0, "d": 0.0},
            }
            rsi, rse = float(tr.get("rsi_floor", 0.17)), float(tr.get("rse_floor", 0.04))
        else:
            rsi = rse = 0.0
        total_r = float(data["r_sum"])
        data["value_u"] = (1.0 / (rsi + rse + total_r)) if (rsi + rse + total_r) != 0 else 0.0
        del data["r_sum"]

    # Upsert por grupo (global): se escribe porque estamos creando todo desde cero (o edit específico)
    for (loc, name), data in groups.items():
        dp = (
            db.query(DetailPart)
            .filter(DetailPart.project_id.is_(None), DetailPart.type == loc, DetailPart.name_detail == name)
            .first()
        )
        if dp:
            dp.value_u = data["value_u"]
            dp.info = data["info"]
            flag_modified(dp, "info")
        else:
            db.add(
                DetailPart(
                    project_id=None, type=loc, name_detail=name, value_u=data["value_u"], info=data["info"]
                )
            )
    try:
        db.commit()
        logger.info(f"✅ DetailPart recalculados (seed): {len(groups)} grupos.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al recalcular DetailPart (seed): {e}")

    # Extras por grupo
    for (loc, name) in groups.keys():
        calculate_details_part_extras(
            db=db,
            name_detail=name,
            scantilon_location=loc,
            limites_cp_liviano=75_000,
            limites_cp_pesado=175_000,
        )
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error finalizando extras (seed): {e}")


# ==============================
# Creación de DetailPart (seed)
# ==============================

def create_detail_part_seed(db: Session, name_detail: str, detail_type: str) -> DetailPart:
    """
    Crea DetailPart en seed con code_ifc único e info por defecto.
    """
    if detail_type not in ("Muro", "Techo", "Piso"):
        raise HTTPException(400, "Tipo inválido. Debe ser 'Muro', 'Techo' o 'Piso'.")

    exists = (
        db.query(DetailPart)
        .filter(DetailPart.name_detail == name_detail, DetailPart.type == detail_type, DetailPart.project_id.is_(None))
        .first()
    )
    if exists:
        return exists

    processed_info: Dict[str, Any] = {}
    consts = db.query(Constant).filter(Constant.type == "details", Constant.name == "generals").first()
    colors = consts.atributs.get("surface_color", {}) if consts else {}

    if detail_type in ("Muro", "Techo"):
        int_name = ext_name = "Intermedio"
        processed_info["surface_color"] = {
            "interior": {"name": int_name, "value": colors.get(int_name, 0.6)},
            "exterior": {"name": ext_name, "value": colors.get(ext_name, 0.6)},
        }
    else:  # Piso
        processed_info["ref_aisl_vertical"] = {"d": 0.0, "e_aisl": 0.0, "lambda": 0.0}
        processed_info["ref_aisl_horizontal"] = {"d": 0.0, "e_aisl": 0.0, "lambda": 0.0}

    prefix_map = {"Muro": "MURO", "Techo": "TECHO", "Piso": "PISO"}
    prefix = prefix_map[detail_type]

    existing_codes = [r[0] for r in db.query(DetailPart.code_ifc).filter(DetailPart.code_ifc.like(f"{prefix}_%")).all()]
    nums = []
    for c in existing_codes:
        parts = c.split("_")
        if len(parts) == 2 and parts[1].isdigit():
            nums.append(int(parts[1]))
    next_num = (max(nums) + 1) if nums else 1
    code_ifc = f"{prefix}_{next_num:03d}"

    dp = DetailPart(name_detail=name_detail, type=detail_type, info=processed_info, code_ifc=code_ifc, project_id=None)
    try:
        db.add(dp)
        db.commit()
        db.refresh(dp)
        return dp
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Error al crear DetailPart (seed): {e}")


# ==========================================
# Flujo Excel -> Details -> Formulas -> DP
# ==========================================

def create_details_generals_default(file_path: str, db: Session) -> None:
    """
    Lee Excel -> inserta Details (seed) -> calcula/asegura CALCULATIONS -> crea/actualiza DetailPart por grupo
    (y sobreescribe detail_part_id) -> crea Formulas -> recalcula aislamiento -> recalcula DetailPart por grupo.
    """
    try:
        df = pd.read_excel(
            file_path, sheet_name="1. Materiales", engine="openpyxl", skiprows=10, usecols="M:Z", nrows=8
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo el archivo: {e}")

    list_columns = df.columns[:4]
    list_detail = {h: df[h].astype(str).str.strip().tolist() for h in list_columns}

    existing_details = {
        (d.scantilon_location, d.name_detail, d.material_id, d.layer_thickness)
        for d in db.query(
            Detail.scantilon_location, Detail.name_detail, Detail.material_id, Detail.layer_thickness
        ).all()
    }

    material_mapping = {row[1]: row[0] for row in db.query(Constant.id, Constant.atributs["name"]).all()}

    new_details: List[Dict[str, Any]] = []
    groups_to_recalc: set = set()  # (detail_type, name_detail)

    # Guardamos “huellas” para luego resolver IDs y a qué grupo pertenecen
    pending_records: List[Dict[str, Any]] = []

    for i in range(1, len(list_detail["Ubicación"]) - 1):
        location = list_detail["Ubicación"][i]
        name_detail = list_detail["Nombre .1"][i]
        material_name = list_detail["Capas de"][i]
        try:
            layer_thickness = float(list_detail["Espesor capa"][i])
        except ValueError:
            continue

        id_material = material_mapping.get(material_name)

        if (location, name_detail, id_material, layer_thickness) in existing_details:
            logger.info(f"⚠️ Detalle '{name_detail}' ya existe con misma configuración. Se omite.")
            continue

        # Normalizamos a tipo para agrupar (sin crear aún el DetailPart)
        if location.lower().startswith("muro"):
            detail_type = "Muro"
        elif location.lower().startswith("techo"):
            detail_type = "Techo"
        elif location.lower().startswith("piso"):
            detail_type = "Piso"
        else:
            logger.warning(f"❌ Tipo no reconocido para la ubicación: {location}")
            continue

        groups_to_recalc.add((detail_type, name_detail))

        # NOTA: NO asignamos detail_part_id aquí; se sobreescribirá luego
        payload = {
            "scantilon_location": location,
            "name_detail": name_detail,
            "material_id": id_material,
            "layer_thickness": layer_thickness,
            "created_status": "default",
            "project_id": None,
            # "detail_part_id": se setea después de calculation_default_details
        }
        new_details.append(payload)

        # guardamos también el detail_type para que las claves de grupo coincidan
        pending_records.append({
            "scantilon_location": location,
            "detail_type": detail_type,  # <— para que la clave sea (detail_type, name_detail)
            "name_detail": name_detail,
            "material_id": id_material,
            "layer_thickness": layer_thickness,
        })

    if new_details:
        try:
            db.bulk_insert_mappings(Detail, new_details)
            db.commit()
            logger.info(f"✅ {len(new_details)} detalles agregados.")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al insertar detalles: {e}")
    else:
        logger.info("⚠️ No se agregaron nuevos detalles.")
        return

    # Aseguramos que CALCULATIONS incluye también los detalles recién insertados
    calculation_default_details(db=db)
    db.expire_all()  # refrescar sesión para lecturas frescas

    # Resolver IDs reales insertados por grupo con clave (detail_type, name_detail)
    group_ids: Dict[tuple, List[int]] = {}
    for rec in pending_records:
        det = db.query(Detail.id, Detail.name_detail).filter(
            Detail.project_id.is_(None),
            Detail.created_status == "default",
            Detail.scantilon_location == rec["scantilon_location"],
            Detail.name_detail == rec["name_detail"],
            Detail.material_id == rec["material_id"],
            Detail.layer_thickness == rec["layer_thickness"],
        ).order_by(Detail.id.desc()).first()
        if det:
            key = (rec["detail_type"], det.name_detail)  # <— clave consistente con groups_to_recalc
            group_ids.setdefault(key, []).append(det.id)

    # AHORA creamos/obtenemos el DetailPart por grupo y SOBREESCRIBIMOS detail_part_id en los Details del grupo
    for dt_type, nm_detail in groups_to_recalc:
        dp = create_detail_part_seed(db, nm_detail, dt_type)  # <— después de calculation_default_details
        ids = group_ids.get((dt_type, nm_detail), [])
        if ids:
            db.query(Detail).filter(Detail.id.in_(ids)).update(
                {"detail_part_id": dp.id}, synchronize_session=False
            )
            db.commit()

    # Creamos Formulas (ya podemos calcular km_op_acumulated con CALCULATIONS lista)
    inserted = db.query(Detail).filter(
        Detail.created_status == "default",
        Detail.project_id.is_(None)
    ).all()
    if not inserted:
        raise HTTPException(status_code=400, detail="No se encontraron detalles insertados para crear fórmulas.")

    for det in inserted:
        km_op = calculate_km_op_acumulated(db, det)
        det_attrs = {
            "scantilon_location": det.scantilon_location,
            "name_detail": det.name_detail,
            "material_id": det.material_id,
            "layer_thickness": det.layer_thickness,
            "km_op_acumulated": km_op,
            "position_insulation": 0,
        }
        new_formula = Formulas(
            project_id=None, item_id=det.id, type="details", name=det.name_detail, atributs=det_attrs, is_deleted=False
        )
        try:
            db.add(new_formula)
            db.commit()
            db.refresh(new_formula)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al crear fórmula para detail {det.id}: {e}")

    # Recalcular posición de aislación
    limit_cp_bordes = (
            db.query(cast(Constant.atributs["light_for_edge_layer"].astext, Float))
            .filter(Constant.name == "generals", Constant.type == "details")
            .scalar()
            or 0.0
    )
    recalculate_position_insulation_seed(limit_cp_bordes, db)

    # Recalcular DetailPart SOLO para los grupos insertados (paso final)
    for dt_type, nm_detail in groups_to_recalc:
        edited_id = None
        ids = group_ids.get((dt_type, nm_detail))
        if ids:
            edited_id = ids[-1]  # o ids[0]
        calculate_details_part_seed(
            db=db,
            detail_type=dt_type,
            name_detail=nm_detail,
            edited_detail_id=edited_id
        )
        calcular_ifc(db=db, name_detail=nm_detail, detail_type=dt_type)

    logger.info("✅ Fórmulas, aislamiento y DetailPart actualizados correctamente (seed).")


# ============================
# Crear Detail (user/admin)
# ============================

def create_details_part(detail: Detail, current_user, db: Session, section: str, project_id: Optional[int]) -> Dict[
    str, Any]:
    """
    Crea un Detail y su Formula; recalcula position_insulation según sección (user/admin).
    """
    if section not in ["user", "admin"]:
        return {"error": "Sección inválida. Use 'user' o 'admin'."}

    detail_data = {
        "scantilon_location": detail.scantilon_location,
        "name_detail": detail.name_detail,
        "material_id": detail.material_id,
        "layer_thickness": detail.layer_thickness,
        "project_id": project_id if section == "user" else None,
    }

    new_detail = Detail(**detail_data)
    try:
        db.add(new_detail)
        db.commit()
        db.refresh(new_detail)
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    det_attrs = {
        "scantilon_location": new_detail.scantilon_location,
        "name_detail": new_detail.name_detail,
        "material_id": new_detail.material_id,
        "layer_thickness": new_detail.layer_thickness,
        "km_op_acumulated": calculate_km_op_acumulated(db, new_detail),
        "position_insulation": 0,
    }
    formula_project_id = project_id if section == "user" else None

    try:
        new_formula = Formulas(
            project_id=formula_project_id,
            item_id=new_detail.id,
            type="details",
            name=new_detail.name_detail,
            atributs=det_attrs,
            is_deleted=False,
        )
        db.add(new_formula)
        db.commit()
        db.refresh(new_formula)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear fórmula: {str(e)}")

    limit_cp_bordes = (
            db.query(cast(Constant.atributs["light_for_edge_layer"].astext, Float))
            .filter(Constant.name == "generals", Constant.type == "details")
            .scalar()
            or 0.0
    )
    if section == "user":
        recalculate_position_insulation_user(project_id, limit_cp_bordes, db)
    else:
        recalculate_position_insulation_seed(limit_cp_bordes, db)

    return {"success": "Detalle, fórmula y DetailPart actualizados.", "detail": new_detail.__dict__}
