import math
import os
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy.orm import Session

from src.services.calculator.weather.weather_service import get_weather_data_from_coord_one
from src.services.datos.materials import get_material_details, get_nodos_area_by_orientation
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.wall import WallEnclosure
from src.models.entity.roof import RoofEnclosure
from src.models.entity.floor import FloorEnclosure
from src.models.entity.window import WindowEnclosure
from src.models.entity.door import DoorEnclosure
from src.models.entity.detail_part import DetailPart
from src.models.entity.details import Detail
from src.models.entity.formulas import Formulas
from src.services.elements_enclosure.floor import get_floor_enclosures
from src.services.elements_enclosure.roof import get_roof_enclosures
from src.services.elements_enclosure.wall_service import get_wall_enclosures
from src.services.project.project_service import get_project_by_id_only
from src.utils.processor import read_parquet_file


# ------------- Utilidades internas ------------------------------------------

def _safe_div(num: float, den: float, default: float = 0.0) -> float:
    """Divide sin lanzar ZeroDivisionError."""
    try:
        return num / den if den else default
    except Exception:
        return default


def _safe_round(value: float, ndigits: int = 0, default: float = 0.0) -> float:
    """round() envuelto para evitar fallos con None o tipos inválidos."""
    try:
        return round(value, ndigits)
    except Exception:
        return default


def _first(iterable, default=None):
    """Devuelve el primer elemento de un iterable o un valor por defecto."""
    return next(iter(iterable), default)


# ------------- Constantes ----------------------------------------------------

AJUSTE_DESFASE_VERTICAL: Dict[str, Dict[str, float]] = {
    "cargas_internas": {"valor": 0.0, "pendiente": 0.3181, "coef_posicion": -0.0029},
    "sol":             {"valor": 0.0, "pendiente": 0.0016, "coef_posicion": -0.0276},
    "infiltraciones":  {"valor": 1.5, "pendiente": 2.1513, "coef_posicion": 2.8145},
}

PORCENTAJE_MAX_RNC_VENTANAS = 0.2

# ------------- Cálculos de área – U – Km·OP ---------------------------------

from typing import List, Dict, Any, Tuple
from collections import defaultdict

# Constantes provistas
RSI_M = 0.13
RSE_M = 0.04
RSI_T = 0.09
RSE_T = 0.04
RSI_P = 0.17
RSE_P = 0.04

# ------- Helpers de rendimiento (solo internos, no cambian tus APIs) --------
from typing import Tuple
import numpy as np

def _prefetch_everything(project_id: int, db: Session):
    """Carga masiva para evitar N+1 (se usa internamente en muros/techos/pisos)."""
    enclosures = (
        db.query(EnclosureGenerals)
          .filter(EnclosureGenerals.project_id == project_id)
          .all()
    )

    # Servicios ya existentes (se mantienen); se agregan en memoria
    all_walls, all_roofs, all_floors = [], [], []
    for e in enclosures:
        all_walls.extend(get_wall_enclosures(e.id, None, db, skip_permission_check=True) or [])
        all_roofs.extend(get_roof_enclosures(e.id, None, db, skip_permission_check=True) or [])
        all_floors.extend(get_floor_enclosures(e.id, None, db, skip_permission_check=True) or [])

    # Windows para todos los muros en batch
    wall_ids = [w.get("wall_id") for w in all_walls if w.get("wall_id") is not None]
    windows = (db.query(WindowEnclosure)
                 .filter(WindowEnclosure.housed_in.in_(wall_ids))
                 .all()) if wall_ids else []

    # DetailPart / Detail / Formulas para todos los items
    detail_part_ids = set()
    detail_part_ids.update([w.get("wall_id") for w in all_walls if w.get("wall_id")])
    detail_part_ids.update([r.get("roof_id") for r in all_roofs if r.get("roof_id")])
    detail_part_ids.update([f.get("floor_id") for f in all_floors if f.get("floor_id")])

    detail_parts = (db.query(DetailPart).filter(DetailPart.id.in_(list(detail_part_ids))).all()
                    if detail_part_ids else [])
    dp_by_id = {dp.id: dp for dp in detail_parts}

    details = db.query(Detail).filter(Detail.detail_part_id.in_(list(detail_part_ids))).all() if detail_part_ids else []
    detail_ids = [d.id for d in details]
    formulas = db.query(Formulas).filter(Formulas.item_id.in_(detail_ids)).all() if detail_ids else []

    return enclosures, all_walls, all_roofs, all_floors, windows, dp_by_id, details, formulas

def _surface_resistances_for(comp: str) -> Tuple[float, float]:
    comp_lower = (comp or "").strip().lower()
    if comp_lower == "roof":
        return RSI_T, RSE_T
    if comp_lower in ("floor", "floor2"):
        return RSI_P, RSE_P
    return RSI_M, RSE_M  # por defecto muro

# ---------------------- Cálculos de área – U – Km·OP -------------------------

def calculate_rnc_area_u_km_op(current_user: dict, project_id: int, db: Session) -> List[Dict[int, Any]]:
    enclosures = (
        db.query(EnclosureGenerals)
        .filter(EnclosureGenerals.project_id == project_id)
        .all()
    )

    elements: List[Dict[int, Any]] = []

    for enclosure in enclosures:
        materials = get_nodos_area_by_orientation(enclosure.id, db, current_user) or []
        materials_2 = get_material_details(enclosure_id=enclosure.id, current_user=current_user, db=db) or []

        if not materials:
            elements.append({enclosure.id: {"type": "muro", "suma_area": 0.0, "suma_u_a": 0.0,
                                            "material_info": [], "suma_km_op": 0.0}})
            continue

        # --- DataFrames
        df_area = pd.DataFrame(materials).rename(columns={
            "Area": "area", "Componente": "componente",
            "Orientacion": "orientacion", "type": "type", "item_id": "item_id"
        })
        df_area["area"] = pd.to_numeric(df_area["area"], errors="coerce").fillna(0.0)
        df_area["componente"] = df_area["componente"].astype(str).fillna("")
        df_area["orientacion"] = df_area["orientacion"].astype(str).fillna("")

        details_list = materials_2.get("data", []) if isinstance(materials_2, dict) else materials_2
        df_det = pd.DataFrame(details_list)
        if not df_det.empty:
            mi = pd.json_normalize(df_det["material_info"]).rename(columns={"c": "c", "p": "p", "d": "d", "R": "R"})
            df_det = pd.concat([df_det.drop(columns=["material_info"]), mi], axis=1)
        else:
            df_det = pd.DataFrame(columns=["capa", "orientation", "c", "p", "d", "R"])

        for col in ["c", "p", "d", "R"]:
            df_det[col] = pd.to_numeric(df_det[col], errors="coerce").fillna(0.0)
        df_det["capa"] = df_det.get("capa", "").astype(str)
        df_det["orientation"] = df_det.get("orientation", "").astype(str)

        # --- Km·OP por (capa, orient) y por capa
        df_kmop_orient = (
            df_det.assign(kmop=lambda x: x["c"] * x["p"] * x["d"])
                  .groupby(["capa", "orientation"], as_index=False)["kmop"].sum()
        )
        df_kmop_capa = (
            df_det.assign(kmop=lambda x: x["c"] * x["p"] * x["d"])
                  .groupby(["capa"], as_index=False)["kmop"].sum()
                  .rename(columns={"kmop": "kmop_capa"})
        )
        # --- Sum R por capa (para U)
        df_sumR = df_det.groupby("capa", as_index=False)["R"].sum().rename(columns={"R": "sumR"})

        # --- U por fila de área (join + vectorizado)
        df_u = df_area.merge(df_sumR, left_on="componente", right_on="capa", how="left")
        comp_lower = df_u["componente"].str.lower()
        rsi = np.where(comp_lower.eq("roof"), RSI_T,
              np.where(comp_lower.isin(["floor", "floor2"]), RSI_P, RSI_M))
        rse = np.where(comp_lower.eq("roof"), RSE_T,
              np.where(comp_lower.isin(["floor", "floor2"]), RSE_P, RSE_M))
        sumR = pd.to_numeric(df_u["sumR"], errors="coerce").fillna(0.0).to_numpy()
        denom = rsi + rse + sumR
        u_vals = np.divide(1.0, denom, out=np.zeros_like(denom, dtype=float), where=denom > 0)

        df_u["u"] = u_vals

        # --- Km·OP con fallback a capa
        df_u = df_u.merge(df_kmop_orient, left_on=["componente", "orientacion"],
                          right_on=["capa", "orientation"], how="left")
        df_u = df_u.merge(df_kmop_capa, left_on="componente", right_on="capa", how="left", suffixes=("", "_by_capa"))
        df_u["km_op"] = df_u["kmop"].fillna(df_u["kmop_capa"]).fillna(0.0)

        # --- Solo muros para sumatorias principales
        is_wall = df_u["componente"].str.startswith("Wall", na=False)
        df_muros = df_u[is_wall].copy()

        suma_area = float(df_muros["area"].sum())
        suma_u_a = float((df_muros["u"] * df_muros["area"]).sum())
        suma_km_op = float((df_muros["km_op"] * df_muros["area"]).sum())

        material_info = df_u[["area", "u", "km_op", "type", "item_id", "componente", "orientacion"]].copy()
        material_info["u_a"] = material_info["u"] * material_info["area"]
        material_info["km_op_area"] = material_info["km_op"] * material_info["area"]
        material_info = material_info.to_dict(orient="records")

        elements.append({
            enclosure.id: {
                "type": (materials[0].get("type", "muro") if materials else "muro"),
                "suma_area": suma_area,
                "suma_u_a": suma_u_a,
                "material_info": material_info,
                "suma_km_op": suma_km_op,
            }
        })

    return elements

# -------------------------------- Muros --------------------------------------

def calculate_rnc_muro(current_user: dict, project_id: int, db: Session) -> List[Dict[int, Any]]:
    enclosures, all_walls, _, _, windows, dp_by_id, details, formulas = _prefetch_everything(project_id, db)
    elements: List[Dict[int, Any]] = []

    df_walls = pd.DataFrame(all_walls)
    if df_walls.empty:
        for enclosure in enclosures:
            elements.append({
                enclosure.id: {
                    "type": "wall",
                    "suma_area": 0.0,
                    "suma_area_e_total": 0.0,
                    "wall_info": [],
                    "area_maxima": 0.0,
                    "id_material_area_maxima": None,
                    "suma_exterior": 0.0,
                    "suma_area_ventana": 0.0,
                    "suma_adiabatico": 0.0,
                    "suma_area_e_aislacion": 0.0,
                }
            })
        return elements

    df_walls = df_walls.rename(columns={"wall_id": "wall_id"})
    if "area" in df_walls:
        df_walls["area"] = pd.to_numeric(df_walls["area"], errors="coerce").fillna(0.0)
    df_walls["characteristics"] = df_walls.get("characteristics", "").astype(str).str.lower().fillna("")
    df_walls["espacio_contiguo"] = df_walls["characteristics"]

    # Ventanas: área sumada por muro (si quieres 1:1, cambia sum() por first())
    if windows:
        df_win = pd.DataFrame([{"housed_in": w.housed_in,
                                "area_ventana": (getattr(w, "high", 0) or 0) * (getattr(w, "broad", 0) or 0)}
                               for w in windows])
        df_win = df_win.groupby("housed_in", as_index=False)["area_ventana"].sum()
        df_walls = df_walls.merge(df_win, left_on="wall_id", right_on="housed_in", how="left")
        df_walls["area_ventana"] = df_walls["area_ventana"].fillna(0.0)
    else:
        df_walls["area_ventana"] = 0.0

    # Espesores & aislación desde DetailPart y Formulas (en batch)
    # sum(layer_thickness) por item_id
    if formulas:
        df_for = pd.DataFrame([{"item_id": f.item_id,
                                "layer_thickness": (f.atributs or {}).get("layer_thickness", 0.0)}
                               for f in formulas])
        df_sum_esp = df_for.groupby("item_id", as_index=False)["layer_thickness"].sum() \
                           .rename(columns={"layer_thickness": "espesor_total"})
    else:
        df_sum_esp = pd.DataFrame(columns=["item_id", "espesor_total"])

    df_walls = df_walls.merge(df_sum_esp, left_on="wall_id", right_on="item_id", how="left")
    df_walls["espesor_total"] = pd.to_numeric(df_walls["espesor_total"], errors="coerce").fillna(0.0)

    # espesor_aislacion por DetailPart
    df_dp = pd.DataFrame([{"wall_id": k, "espesor_aislacion": (v.calculations or {}).get("espesor_aislacion", 0.0)}
                          for k, v in dp_by_id.items()])
    df_walls = df_walls.merge(df_dp, on="wall_id", how="left")
    df_walls["espesor_aislacion"] = pd.to_numeric(df_walls["espesor_aislacion"], errors="coerce").fillna(0.0)

    # Derivados
    df_walls["area_e_total"] = df_walls["area"] * df_walls["espesor_total"]
    df_walls["area_e_aislacion"] = df_walls["area"] * df_walls["espesor_aislacion"]
    df_walls["exterior"] = np.where(df_walls["espacio_contiguo"].eq("exterior"), df_walls["area"], 0.0)
    df_walls["adiabatico"] = np.where(df_walls["espacio_contiguo"].eq("exterior"), 0.0, df_walls["area"])

    # Por recinto
    # Si tu dict de muro trae 'enclosure_id', úsalo; si no, filtramos por nada (todos)
    for enclosure in enclosures:
        if "enclosure_id" in df_walls.columns:
            df_e = df_walls[df_walls["enclosure_id"] == enclosure.id]
        else:
            df_e = df_walls

        if df_e.empty:
            elements.append({
                enclosure.id: {
                    "type": "wall",
                    "suma_area": 0.0,
                    "suma_area_e_total": 0.0,
                    "wall_info": [],
                    "area_maxima": 0.0,
                    "id_material_area_maxima": None,
                    "suma_exterior": 0.0,
                    "suma_area_ventana": 0.0,
                    "suma_adiabatico": 0.0,
                    "suma_area_e_aislacion": 0.0,
                }
            })
            continue

        # id de material con mayor área
        idxmax = int(df_e["area"].values.argmax())
        id_material_area_maxima = int(df_e.iloc[idxmax]["wall_id"])

        wall_info = df_e[[
            "wall_id", "area", "area_e_total", "espesor_aislacion", "espesor_total",
            "area_e_aislacion", "espacio_contiguo", "exterior", "area_ventana", "adiabatico"
        ]].rename(columns={"area_ventana": "area_ventana"}).to_dict(orient="records")

        elements.append({
            enclosure.id: {
                "type": "wall",
                "suma_area": float(df_e["area"].sum()),
                "suma_area_e_total": float(df_e["area_e_total"].sum()),
                "wall_info": wall_info,
                "area_maxima": float(df_e["area"].max()),
                "id_material_area_maxima": id_material_area_maxima,
                "suma_exterior": float(df_e["exterior"].sum()),
                "suma_area_ventana": float(df_e["area_ventana"].sum()),
                "suma_adiabatico": float(df_e["adiabatico"].sum()),
                "suma_area_e_aislacion": float(df_e["area_e_aislacion"].sum()),
            }
        })

    return elements

# -------------------------------- Techos -------------------------------------

def calculate_rnc_techo(current_user: dict, project_id: int, db: Session) -> List[Dict[int, Any]]:
    enclosures, _, all_roofs, _, _, dp_by_id, _, formulas = _prefetch_everything(project_id, db)
    elements: List[Dict[int, Any]] = []

    df_roofs = pd.DataFrame(all_roofs)
    if df_roofs.empty:
        for enclosure in enclosures:
            elements.append({enclosure.id: {"type": "roof", "suma_area": 0.0, "roof_info": [],
                                            "suma_km_op": 0.0, "area_maxima": 0.0,
                                            "exterior_mayor": 0.0, "num_roof": 0}})
        return elements

    df_roofs = df_roofs.rename(columns={"roof_id": "roof_id"})
    df_roofs["area"] = pd.to_numeric(df_roofs["area"], errors="coerce").fillna(0.0)
    df_roofs["characteristic"] = df_roofs.get("characteristic", "").astype(str).str.lower().fillna("")
    df_roofs["exterior"] = np.where(df_roofs["characteristic"].eq("exterior"), 1.0, 0.0)
    df_roofs["adiabatico"] = 1.0 - df_roofs["exterior"]

    # km_op & espesores desde DetailPart/Formulas
    df_dp = pd.DataFrame([{"roof_id": k,
                           "km_op": (v.calculations or {}).get("km_op", 0.0),
                           "esp_aisl": (v.calculations or {}).get("espesor_aislacion", 0.0)}
                          for k, v in dp_by_id.items()])
    df_roofs = df_roofs.merge(df_dp, on="roof_id", how="left")
    df_roofs["km_op"] = pd.to_numeric(df_roofs["km_op"], errors="coerce").fillna(0.0)

    if formulas:
        df_for = pd.DataFrame([{"item_id": f.item_id,
                                "layer_thickness": (f.atributs or {}).get("layer_thickness", 0.0)}
                               for f in formulas])
        df_sum_esp = df_for.groupby("item_id", as_index=False)["layer_thickness"].sum() \
                           .rename(columns={"layer_thickness": "esp_total"})
        df_roofs = df_roofs.merge(df_sum_esp, left_on="roof_id", right_on="item_id", how="left")
    else:
        df_roofs["esp_total"] = 0.0

    df_roofs["esp_total"] = pd.to_numeric(df_roofs.get("esp_total", 0.0), errors="coerce").fillna(0.0)

    for enclosure in enclosures:
        df_e = df_roofs[df_roofs["enclosure_id"] == enclosure.id] if "enclosure_id" in df_roofs.columns else df_roofs
        if df_e.empty:
            elements.append({enclosure.id: {"type": "roof", "suma_area": 0.0, "roof_info": [],
                                            "suma_km_op": 0.0, "area_maxima": 0.0,
                                            "exterior_mayor": 0.0, "num_roof": 0}})
            continue

        idxmax = int(df_e["area"].values.argmax())
        exterior_mayor = float(df_e.iloc[idxmax]["exterior"])

        roof_info = df_e[["area", "esp_aisl", "esp_total", "exterior", "adiabatico", "km_op"]].rename(
            columns={"esp_aisl": "espesor_aislacion", "esp_total": "espesor_total"}
        ).to_dict(orient="records")

        elements.append({
            enclosure.id: {
                "type": "roof",
                "suma_area": float(df_e["area"].sum()),
                "roof_info": roof_info,
                "suma_km_op": float(df_e["km_op"].sum()),
                "area_maxima": float(df_e["area"].max()),
                "exterior_mayor": exterior_mayor,
                "num_roof": int(len(df_e))
            }
        })

    return elements

# -------------------------------- Pisos --------------------------------------

def calculate_rnc_piso(current_user: dict, project_id: int, db: Session) -> List[Dict[int, Any]]:
    enclosures, _, _, all_floors, _, dp_by_id, _, formulas = _prefetch_everything(project_id, db)
    elements: List[Dict[int, Any]] = []

    df_floors = pd.DataFrame(all_floors)
    if df_floors.empty:
        for enclosure in enclosures:
            elements.append({enclosure.id: {"type": "floor", "suma_area": 0.0, "floor_info": [],
                                            "suma_km_op": 0.0, "area_maxima": 0.0,
                                            "exterior_mayor": 0.0, "num_floor": 0}})
        return elements

    df_floors = df_floors.rename(columns={"floor_id": "floor_id"})
    df_floors["area"] = pd.to_numeric(df_floors["area"], errors="coerce").fillna(0.0)
    df_floors["characteristic"] = df_floors.get("characteristic", "").astype(str).str.lower().fillna("")
    df_floors["exterior"] = np.where(df_floors["characteristic"].eq("exterior"), 1.0, 0.0)
    df_floors["adiabatico"] = 1.0 - df_floors["exterior"]

    df_dp = pd.DataFrame([{
        "floor_id": k,
        "km_op": (v.calculations or {}).get("km_op", 0.0),
        "esp_aisl": ((v.info or {}).get("aislacion_bajo_piso", {}) or {}).get("e_aisl", 0.0)
    } for k, v in dp_by_id.items()])
    df_floors = df_floors.merge(df_dp, on="floor_id", how="left")
    df_floors["km_op"] = pd.to_numeric(df_floors["km_op"], errors="coerce").fillna(0.0)

    if formulas:
        df_for = pd.DataFrame([{"item_id": f.item_id,
                                "layer_thickness": (f.atributs or {}).get("layer_thickness", 0.0)}
                               for f in formulas])
        df_sum_esp = df_for.groupby("item_id", as_index=False)["layer_thickness"].sum() \
                           .rename(columns={"layer_thickness": "esp_total"})
        df_floors = df_floors.merge(df_sum_esp, left_on="floor_id", right_on="item_id", how="left")
    else:
        df_floors["esp_total"] = 0.0

    df_floors["esp_total"] = pd.to_numeric(df_floors.get("esp_total", 0.0), errors="coerce").fillna(0.0)

    for enclosure in enclosures:
        df_e = df_floors[df_floors["enclosure_id"] == enclosure.id] if "enclosure_id" in df_floors.columns else df_floors
        if df_e.empty:
            elements.append({enclosure.id: {"type": "floor", "suma_area": 0.0, "floor_info": [],
                                            "suma_km_op": 0.0, "area_maxima": 0.0,
                                            "exterior_mayor": 0.0, "num_floor": 0}})
            continue

        idxmax = int(df_e["area"].values.argmax())
        exterior_mayor = float(df_e.iloc[idxmax]["exterior"])

        floor_info = df_e[["area", "esp_aisl", "esp_total", "exterior", "adiabatico", "km_op"]].rename(
            columns={"esp_aisl": "espesor_aislacion", "esp_total": "espesor_total"}
        ).to_dict(orient="records")

        elements.append({
            enclosure.id: {
                "type": "floor",
                "suma_area": float(df_e["area"].sum()),
                "floor_info": floor_info,
                "suma_km_op": float(df_e["km_op"].sum()),
                "area_maxima": float(df_e["area"].max()),
                "exterior_mayor": exterior_mayor,
                "num_floor": int(len(df_e))
            }
        })

    return elements

# --------------------------- Consolidado RNC ---------------------------------

def datos_rnc(current_user: dict, project_id: int, db: Session) -> List[Dict[int, Any]]:
    enclosures = (
        db.query(EnclosureGenerals)
        .filter(EnclosureGenerals.project_id == project_id)
        .all()
    )

    calc_area   = {k: v for d in calculate_rnc_area_u_km_op(current_user, project_id, db) for k, v in d.items()}
    rnc_muro    = {k: v for d in calculate_rnc_muro(current_user, project_id, db)      for k, v in d.items()}
    rnc_techo   = {k: v for d in calculate_rnc_techo(current_user, project_id, db)     for k, v in d.items()}
    rnc_piso    = {k: v for d in calculate_rnc_piso(current_user, project_id, db)      for k, v in d.items()}

    project = get_project_by_id_only(project_id, db)
    zone = project.project_metadata.get("zone")
    weather_metadata = get_weather_data_from_coord_one(db, project.latitude, project.longitude, zone)
    weather_path = weather_metadata.location
    monthly_path = weather_metadata.complementary
    weather_processed_df = read_parquet_file(weather_path)
    monthly_processed_data_df = read_parquet_file(monthly_path)

    from src.services.calculator.python.process_python_input import PyProcessInput

    elements: List[Dict[int, Any]] = []

    for enclosure in enclosures:
        enc_id = enclosure.id

        # --- promedios
        u_promedio_muros = _safe_div(
            calc_area.get(enc_id, {}).get("suma_u_a", 0.0),
            calc_area.get(enc_id, {}).get("suma_area", 0.0)
        )

        kmop_promedio_muros = _safe_div(
            calc_area.get(enc_id, {}).get("suma_km_op", 0.0),
            calc_area.get(enc_id, {}).get("suma_area", 0.0)
        )

        kmop_promedio_techumbre = _safe_div(
            rnc_techo.get(enc_id, {}).get("suma_km_op", 0.0),
            rnc_techo.get(enc_id, {}).get("num_roof", 0.0)
        )

        kmop_promedio_piso = _safe_div(
            rnc_piso.get(enc_id, {}).get("suma_km_op", 0.0),
            rnc_piso.get(enc_id, {}).get("num_floor", 0.0)
        )

        # --- techos/pisos adiabáticos
        techo_adiabatico = "Si" if rnc_techo.get(enc_id, {}).get("exterior_mayor", 1) == 0 else "No"
        piso_adiabatico  = "Si" if rnc_piso.get(enc_id, {}).get("exterior_mayor", 1) == 0 else "No"

        # --- aislación exterior (solo sobre el id más grande)
        try:
            id_mat_max = rnc_muro[enc_id]["id_material_area_maxima"]
            detail_part = db.query(DetailPart).get(id_mat_max)
            details = db.query(Detail).filter(Detail.detail_part_id == detail_part.id).all()
            detail_ids = [d.id for d in details]
            formulas = db.query(Formulas).filter(Formulas.item_id.in_(detail_ids)).all()
            aislacion_ext = "Si" if any((f.atributs or {}).get("position_insulation", 0) > 0 for f in formulas) else "No"
        except Exception:
            aislacion_ext = "No"

        # --- áreas y espesores
        area_recinto = min(rnc_piso.get(enc_id, {}).get("suma_area", 0.0), 20)
        altura_recinto = getattr(enclosure, "height", 0.0)
        suma_area_muro = rnc_muro.get(enc_id, {}).get("suma_area", 0.0)

        espesor_promedio_muros = _safe_div(
            rnc_muro.get(enc_id, {}).get("suma_area_e_total", 0.0),
            suma_area_muro
        )
        espesor_aislacion_promedio_muros = _safe_div(
            rnc_muro.get(enc_id, {}).get("suma_area_e_aislacion", 0.0),
            suma_area_muro
        )

        m2_muros_ext = rnc_muro.get(enc_id, {}).get("suma_exterior", 0.0)
        m2_vent      = rnc_muro.get(enc_id, {}).get("suma_area_ventana", 0.0)
        m2_muros_ad  = rnc_muro.get(enc_id, {}).get("suma_adiabatico", 0.0)

        cargas_internas  = AJUSTE_DESFASE_VERTICAL["cargas_internas"]["valor"]
        renovaciones_aire = AJUSTE_DESFASE_VERTICAL["infiltraciones"]["valor"]

        porcentaje_vent = _safe_div(m2_vent, (m2_muros_ext + m2_vent))
        volumen_recinto = area_recinto * altura_recinto

        u_kmax_vol = _safe_round(
            _safe_div(u_promedio_muros * _safe_div(kmop_promedio_muros, volumen_recinto) *
                      ((espesor_aislacion_promedio_muros / espesor_promedio_muros) + 1 if espesor_promedio_muros else 1),
                      1),
            0
        )

        # kmop promedio envolvente
        try:
            numerador = (
                kmop_promedio_muros * m2_muros_ad + m2_muros_ext
                + kmop_promedio_techumbre * area_recinto
                + kmop_promedio_piso * area_recinto
            )
            denominador = (area_recinto * 2) + m2_muros_ext + m2_muros_ad
            kmop_promedio_envolvente = _safe_round(_safe_div(numerador, denominador), 0)
        except Exception:
            kmop_promedio_envolvente = 0.0

        # kmop adiabático promedio
        try:
            term_c13 = 0.0 if techo_adiabatico.lower() == "no" else kmop_promedio_techumbre * area_recinto
            kmop_ad_promedio = _safe_div(
                (kmop_promedio_muros * m2_muros_ad) + term_c13,
                area_recinto + m2_muros_ad
            )
        except Exception:
            kmop_ad_promedio = 0.0

        # límites de ventanas
        maximo_ventanas = PORCENTAJE_MAX_RNC_VENTANAS if porcentaje_vent > PORCENTAJE_MAX_RNC_VENTANAS else porcentaje_vent
        n_vent = min(m2_vent, maximo_ventanas * (m2_muros_ext + m2_vent))

        # PyProcessInput (1 build por recinto)
        def get_sol_file(enclosure_id: int):
            route_sol = f"public/sol_recinto/{project_id}/"
            sol_file_parquet = os.path.join(route_sol, str(enclosure_id) + '_sol_recinto.parquet')
            return sol_file_parquet

        sol_file = get_sol_file(enclosure.id)

        areas_for_py = get_nodos_area_by_orientation(enclosure.id, db=db)
        areas_for_py = pd.DataFrame(areas_for_py).drop(columns=["Absorcion", "item_id", "type"], errors="ignore")

        py_process_input = PyProcessInput(
            project, enclosure.id, weather_processed_df,
            monthly_processed_data_df, areas_for_py=areas_for_py, sol_file=sol_file, db=db
        )
        tupla = py_process_input.build(weather_processed_df, monthly_processed_data_df)
        resultado_df = tupla[2]
        promedio_flujo = resultado_df["flujo_sol"].mean()

        if porcentaje_vent == 0:
            flujo_sol = 0
        else:
            flujo_sol = promedio_flujo * maximo_ventanas / porcentaje_vent

        elements.append({
            enc_id: {
                "espesor_aislacion_promedio_muros": espesor_aislacion_promedio_muros,
                "m2_muros_ext": m2_muros_ext,
                "m2_vent": m2_vent,
                "m2_muros_ad": m2_muros_ad,
                "cargas_internas": cargas_internas,
                "renovaciones_aire": renovaciones_aire,
                "aislacion_ext": aislacion_ext,
                "area_recinto": area_recinto,
                "altura_recinto": altura_recinto,
                "espesor_promedio_muros": espesor_promedio_muros,
                "piso_adiabatico": piso_adiabatico,
                "techo_adiabatico": techo_adiabatico,
                "u_promedio_muros": u_promedio_muros,
                "kmop_promedio_muros": kmop_promedio_muros,
                "kmop_promedio_techumbre": kmop_promedio_techumbre,
                "kmop_promedio_piso": kmop_promedio_piso,
                "porcentaje_vent": porcentaje_vent,
                "volumen_recinto": volumen_recinto,
                "u_kmax_vol": u_kmax_vol,
                "flujo_sol": flujo_sol,
                "kmop_promedio_envolvente": kmop_promedio_envolvente,
                "kmop_ad_promedio": kmop_ad_promedio,
                "maximo_ventanas": maximo_ventanas,
                "n_vent": n_vent,
            }
        })

    return elements
