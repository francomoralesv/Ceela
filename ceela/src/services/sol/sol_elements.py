# -----------------------------------------------------------------------------
#  MÓDULO  :  solar_openings.py
# -----------------------------------------------------------------------------
#  *Añadido* el cálculo de la ganancia solar “Q solar” para cada hueco:
#      Q = ((RadDir·(1-Fsh)·Veo) + RadDif) · g_gl · Área · (1-Ffr)
#  Se exporta como window_Qsol_{i} y door_Qsol_{i}.
# -----------------------------------------------------------------------------

import os
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import Depends

from src.models.entity.door import DoorEnclosure
from src.models.entity.elements import Element
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.fav import Fav
from src.models.entity.project_table import Project
from src.models.entity.window import WindowEnclosure
from src.services.database.db_connection import get_db
from src.services.datos.materials import get_enclosures_by_project

TILT = 0

ORIENTACIONES_AZIMUT = {
    "HR": dict(azimut_min=None, azimut_max=None, azimut_considerado=None, yk_vent=0, azimut_360=None),
    "N":  dict(azimut_min=337.5, azimut_max=22.5,  azimut_considerado=0,   yk_vent=180, azimut_360=180),
    "NE": dict(azimut_min=22.5,  azimut_max=67.5,  azimut_considerado=45,  yk_vent=135, azimut_360=135),
    "E":  dict(azimut_min=67.5,  azimut_max=112.5, azimut_considerado=90,  yk_vent=90,  azimut_360=90),
    "SE": dict(azimut_min=112.5, azimut_max=157.5, azimut_considerado=135, yk_vent=45,  azimut_360=45),
    "S":  dict(azimut_min=157.5, azimut_max=202.5, azimut_considerado=180, yk_vent=0,   azimut_360=0),
    "SO": dict(azimut_min=202.5, azimut_max=247.5, azimut_considerado=225, yk_vent=-45, azimut_360=315),
    "O":  dict(azimut_min=247.5, azimut_max=292.5, azimut_considerado=270, yk_vent=-90, azimut_360=270),
    "NO": dict(azimut_min=292.5, azimut_max=337.5, azimut_considerado=315, yk_vent=-135, azimut_360=225),
}


# ---------------------------------------------------------------------------
# Utilidades generales
# ---------------------------------------------------------------------------

def calcular_yk(orientation: str, tilt: float) -> float:
    datos = ORIENTACIONES_AZIMUT.get(orientation)
    if datos is None:
        return 0.0
    yk = datos["yk_vent"]
    return (yk + tilt) if yk > 0 else (yk - tilt)


def _to_float(val, name: str, ctx_id: int):
    if hasattr(val, "as_float"):
        return val.as_float()
    if isinstance(val, (int, float)):
        return float(val)
    raise RuntimeError(f"{name} (id={ctx_id}) no convertible a float ({type(val).__name__})")


# ---------------------------------------------------------------------------
# Ventanas
# ---------------------------------------------------------------------------

def calculate_sol_windows(df: pd.DataFrame, enclosure_id: int, db: Session) -> pd.DataFrame:

    print(f"[DEBUG] calculate_sol_windows(enclosure_id={enclosure_id})")
    windows = db.query(WindowEnclosure).filter(WindowEnclosure.enclosure_id == enclosure_id).all()
    if not windows:
        print(f"[DEBUG] No hay ventanas para enclosure_id={enclosure_id}.")
        return df

    df["azimut_phisol_360"] = np.where(df["azimut_libro"] < 0,
                                       df["azimut_libro"] + 360,
                                       df["azimut_libro"])

    w_total = 0
    for i, window in enumerate(windows, start=1):
        fav = db.query(Fav).filter(Fav.item_id == window.id, Fav.type == "window").first()
        if not fav:
            print(f"[WARN] No hay Fav para window.id={window.id}, salto.")
            continue
        el = db.get(Element, window.window_id)
        if not el:
            print(f"[WARN] No hay Element para window_id={window.window_id}, salto.")
            continue

        try:
            fav1      = {k: _to_float(v, f"fav1[{k}]",      window.id) for k, v in fav.fav1.items()}
            fav2_der  = {k: _to_float(v, f"fav2_der[{k}]",  window.id) for k, v in fav.fav2_der.items()}
            fav2_izq  = {k: _to_float(v, f"fav2_izq[{k}]",  window.id) for k, v in fav.fav2_izq.items()}
            fav3      = {k: _to_float(v, f"fav3[{k}]",      window.id) for k, v in fav.fav3.items()}
        except Exception as e:
            print(f"[WARN] {e}; salto window.id={window.id}.")
            continue

        orientation, hk, wk = window.orientation, window.high, window.broad
        area = hk * wk
        Ffr  = 1.0 - el.fm
        g_gl = _to_float(el.atributs["fs_vidrio"], "fs_vidrio", window.id)

        yk = calcular_yk(orientation, TILT)
        yk_360 = (yk if yk >= 0 else yk + 360)

        lk_finr_r, dk_finr_r = fav2_der["s"], fav2_der["p"]
        lk_ovh_q, dk_ovh_q   = fav1["d"], fav1["l"]
        lk_fini_i, dk_fini_i = fav2_izq["s"], fav2_izq["p"]

        beta, alfa, e_val, t_val = fav3["beta"], fav3["alfa"], fav3["e"], fav3["t"]

        ecos_alfa = e_val * np.cos(np.radians(90 - alfa))
        wk_alfa   = np.maximum(0.0, t_val - ecos_alfa)
        alfa_360  = np.mod(yk_360 - alfa, 360)
        dk_finr_r_l = 0.0 if wk_alfa == 0 else e_val * np.sin(np.radians(90 - alfa))
        porcentaje_vent_alfa  = 0.0 if t_val == 0 else (t_val - wk_alfa) / t_val
        porcentaje_vent_plana = 1.0 - porcentaje_vent_alfa

        ecos_beta = e_val * np.cos(np.radians(beta))
        hk_beta   = np.maximum(0.0, t_val - ecos_beta)
        dk_beta   = e_val * np.sin(np.radians(beta))
        porcentaje_opaco = 0.0 if t_val == 0 else (t_val - hk_beta) / t_val

        az = df["azimut_phisol_360"]
        alt = df["alt"]
        mask = np.where(
            yk_360 < 90,  (az > yk_360 + 270) | (az < yk_360 + 90),
            np.where(
                yk_360 > 270, (az > yk_360 - 90) | (az < yk_360 - 270),
                (az > yk_360 - 90) & (az < yk_360 + 90),
            ),
        )
        df[f"window_veo_sol_{i}"] = (mask & (alt > 0)).astype(int)

        # hk_ovh_q_t
        rad_alt  = np.radians(alt)
        rad_diff = np.radians(df["azimut_libro"] - yk)
        expr     = dk_ovh_q * np.tan(rad_alt) / np.cos(rad_diff) - lk_ovh_q
        df[f"window_hk_ovh_q_t_{i}"] = np.clip(expr, 0, hk)

        # wk_finr_r
        expr = dk_finr_r * np.tan(-rad_diff - lk_finr_r)
        df[f"window_wk_finr_r_{i}"] = np.clip(expr, 0, wk)

        # wk_finl_l
        expr = dk_fini_i * np.tan(rad_diff - lk_fini_i)
        df[f"window_wk_finl_l_{i}"] = np.clip(expr, 0, wk)

        # Fsh_dir_k_t_FAV_1_y_FAV2
        veo, hk_ovh = df[f"window_veo_sol_{i}"], df[f"window_hk_ovh_q_t_{i}"]
        wf_r, wf_l  = df[f"window_wk_finr_r_{i}"], df[f"window_wk_finl_l_{i}"]
        df[f"window_Fsh_dir_k_t_FAV_1_y_FAV2_{i}"] = np.where(
            hk == 0, 0,
            veo * (hk_ovh * wk + (hk - hk_ovh) * (wf_r + wf_l)) / (hk * wk)
        )

        # a_Fs
        azi360  = df["azimut_phisol_360"]
        df[f"window_a_Fs_{i}"] = np.where(
            (beta != 0) | (t_val == 0),
            0,
            np.where(alfa > 0,
                     df[f"window_veo_sol_{i}"] * (azi360 < alfa_360),
                     df[f"window_veo_sol_{i}"] * (azi360 > alfa_360))
        ).astype(int)

        # wk_finl_l_l
        ang = np.radians(df["azimut_libro"] - yk)
        expr1 = np.clip(dk_finr_r_l * np.tan(ang - ecos_alfa), 0.0, wk_alfa)
        expr2 = np.clip(dk_finr_r_l * np.tan(ang),             0.0, wk_alfa)
        df[f"window_wk_finl_l_l_{i}"] = np.where(alfa < 0, expr1, expr2)

        # wk_finr_r_r
        ang_b = -ang
        r1 = np.clip(dk_finr_r_l * np.tan(ang_b - ecos_alfa), 0.0, wk_alfa)
        r2 = np.clip(dk_finr_r_l * np.tan(ang_b),             0.0, wk_alfa)
        df[f"window_wk_finr_r_r_{i}"] = np.where(alfa > 0, r1, r2)

        # fsh_dir_k_t_para_a
        inner_a = np.where(
            wk_alfa == 0,
            porcentaje_vent_plana + (1 - df[f"window_a_Fs_{i}"]) * porcentaje_vent_alfa,
            ((df[f"window_wk_finr_r_r_{i}"] / wk_alfa
            +  df[f"window_wk_finl_l_l_{i}"] / wk_alfa) * porcentaje_vent_plana
            + (1 - df[f"window_a_Fs_{i}"]) * porcentaje_vent_alfa),
        )
        df[f"window_fsh_dir_k_t_para_a_{i}"] = np.where(t_val == 0, 0,
                                                        df[f"window_veo_sol_{i}"] * inner_a)

        # b_fsh y fsh_dir_k_t_para_b
        ang_tan = np.tan(np.radians(df["alt"]))
        cos_c   = np.cos(np.radians(df["azimut_libro"] - yk))
        raw_b   = dk_beta * ang_tan / cos_c
        clamped = np.where(raw_b < 0, 0.0,
                           np.where(raw_b >= hk_beta, hk_beta, raw_b))
        df[f"window_b_fsh_{i}"] = np.where(alfa != 0, 0.0, clamped)

        inner_b = porcentaje_opaco + (df[f"window_b_fsh_{i}"] / hk_beta) * (1 - porcentaje_opaco)
        df[f"window_fsh_dir_k_t_para_b_{i}"] = np.where(
            hk_beta == 0, 0.0, df[f"window_veo_sol_{i}"] * inner_b
        )

        # FAR
        clave_obstruccion = f"Obstruccion_{window.orientation}"
        if clave_obstruccion not in df.columns:
            print(f"[WARN] Columna {clave_obstruccion} no encontrada, usando 0.")
            df[f"window_FAR_{i}"] = 0.0
        else:
            meses = {"enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
                     "julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12}
            fila = (df["mes"].str.lower().map(meses) - 1) * 24 + df["hora"] - 23
            fila = fila.clip(lower=0, upper=len(df)-1).astype(int)
            df[f"window_FAR_{i}"] = df[clave_obstruccion].values[fila]

        # Fsh_dir_k_t  (máximo fila-a-fila)
        df[f"window_Fsh_dir_k_t_{i}"] = np.max(
            df[
                [
                    f"window_Fsh_dir_k_t_FAV_1_y_FAV2_{i}",
                    f"window_fsh_dir_k_t_para_a_{i}",
                    f"window_fsh_dir_k_t_para_b_{i}",
                    f"window_FAR_{i}",
                ]
            ].values,
            axis=1
        )

        # -----------------------------------------------------------------
        #  Q SOLAR  (implementación directa de la fórmula de Excel)
        # -----------------------------------------------------------------
        rad_dir_col  = f"rad_directa_{orientation}"
        rad_dif_col  = f"rad_dif_{orientation}"

        if rad_dir_col not in df.columns or rad_dif_col not in df.columns:
            print(f"[WARN] Columnas {rad_dir_col}/{rad_dif_col} no encontradas; Qsolar=0.")
            df[f"window_w_parcial_{i}"] = 0.0
        else:
            df[f"window_w_parcial_{i}"] = (
                (
                    df[rad_dir_col] * (1 - df[f"window_Fsh_dir_k_t_{i}"]) * df[f"window_veo_sol_{i}"]
                    + df[rad_dif_col]
                )
                * g_gl
                * area
                * (1 - Ffr)
            )

        w_total += df[f"window_w_parcial_{i}"]
    
    df["window_w_total"] = w_total
    return df


def convert_parquet_window_project(
    db: Session,
    project_id: int,
    extra_keep: List[str] | None = None,
) -> Dict[int, Path]:
    """
    Para cada enclosure del proyecto:
      Lee
        public/sol_recinto/<project_id>/<enclosure_id>_sol_recinto.parquet
        public/parametros_solares/{project_id}_parametros_solares.parquet   <-- generado automáticamente
        public/sol_obstruction/<project_id>/<enclosure_id>_sol_obstruction.parquet
      Calcula ventanas y exporta:
        public/sol_windows/<project_id>/<enclosure_id>_sol_window.parquet
      Devuelve {enclosure_id: ruta_salida}
    """
    extra_keep = extra_keep or ["azimut_phisol_360", "window_w_total"]

    # ── Parquet de parámetros solares (uno por proyecto) ──────────
    p_param_solar = Path("public") / "parametros_solares" / f"{project_id}_parametros_solares.parquet"
    if not p_param_solar.is_file():
        raise FileNotFoundError(p_param_solar)

    # ── Recintos del proyecto ─────────────────────────────────────
    enclosures: List[EnclosureGenerals] = get_enclosures_by_project(
            project_id, db=db)

    # ── Carpeta de salida ─────────────────────────────────────────
    out_root = Path("public") / "sol_windows" / str(project_id)
    out_root.mkdir(parents=True, exist_ok=True)

    rutas: Dict[int, Path] = {}

    for enclosure in enclosures:
        enclosure_id = enclosure.id

        p_recinto     = Path("public") / "sol_recinto"     / str(project_id) / f"{enclosure_id}_sol_recinto.parquet"
        p_obstruction = Path("public") / "sol_obstruction" / str(project_id) / f"{enclosure_id}_sol_obstruction.parquet"

        if not p_recinto.is_file() or not p_obstruction.is_file():
            print(f"[DEBUG]⚠️ Saltando {enclosure_id}: falta {p_recinto} o {p_obstruction}")
            continue

        # ── Concatenar DataFrames ─────────────────────────────────
        df = pd.concat(
            [pd.read_parquet(p).reset_index(drop=True) for p in (p_recinto, p_param_solar, p_obstruction)],
            axis=1,
        )

        df = calculate_sol_windows(df, enclosure_id, db)

        # ── Columnas de salida ────────────────────────────────────
        veo_cols = sorted(
            (
                c for c in df.columns if any(
                    c.startswith(pref) for pref in (
                        "window_veo_sol_", "window_hk_ovh_q_t_", "window_wk_finr_r_",
                        "window_wk_finl_l_", "window_Fsh_dir_k_t_FAV_1_y_FAV2_",
                        "window_a_Fs_", "window_wk_finl_l_l_", "window_wk_finr_r_r_",
                        "window_fsh_dir_k_t_para_a_", "window_b_fsh_",
                        "window_fsh_dir_k_t_para_b_", "window_FAR_", "window_Fsh_dir_k_t_",
                        "window_w_parcial_"
                    )
                )
            ),
            key=lambda s: int(s.rsplit("_", 1)[1]),
        )
        keep_cols = [c for c in extra_keep if c in df.columns]
        df_out = df[keep_cols + veo_cols]

        out_path = out_root / f"{enclosure_id}_sol_window.parquet"
        df_out.to_parquet(out_path, engine="pyarrow", index=False)
        print(f"✅ Ventanas {enclosure_id} → {out_path}")

        rutas[enclosure_id] = out_path

    return rutas

def read_sol_window_parquet(enclosure_id: int, project_id: int, db: Session) -> pd.DataFrame:
    """
    Lee el Parquet de ventanas para el enclosure_id y devuelve el DataFrame.
    Agrega columnas month (1-12, cada valor se repite 24 veces) y
    hour (1-24, ciclo completo para cada mes).
    """
    print(f"📂 Ventanas {enclosure_id}")
    p = Path("public") / "sol_windows" / str(project_id) / f"{enclosure_id}_sol_window.parquet"
    if not p.is_file():
        convert_parquet_window_project(db, project_id)
    if not p.is_file():
        raise FileNotFoundError(p)
        
    # Leer el parquet
    df = pd.read_parquet(p)
    
    # Crear arrays para month y hour
    months = []
    hours = []
    
    # Para cada mes (1-12)
    for month in range(1, 13):
        months.extend([month] * 24)
        hours.extend(list(range(1, 25)))
    
    df['month'] = months
    df['hour'] = hours
    df = df[['window_w_total', 'month', 'hour']]
    return df


# ---------------------------------------------------------------------------
# Puertas
# ---------------------------------------------------------------------------

def calculate_sol_doors(df: pd.DataFrame, enclosure_id: int, db: Session) -> pd.DataFrame:
    doors = db.query(DoorEnclosure).filter(DoorEnclosure.enclosure_id == enclosure_id).all()
    if not doors:
        print(f"[DEBUG] No hay puertas para enclosure_id={enclosure_id}.")
        return df

    df["azimut_phisol_360"] = np.where(df["azimut_libro"] < 0,
                                       df["azimut_libro"] + 360,
                                       df["azimut_libro"])

    w_total = 0
    for i, door in enumerate(doors, start=1):
        fav = db.query(Fav).filter(Fav.item_id == door.id, Fav.type == "door").first()
        if not fav:
            print(f"[WARN] No hay Fav tipo 'door' para door.id={door.id}, salto.")
            continue
        el = db.get(Element, door.door_id)
        if not el:
            print(f"[WARN] No hay Element para door_id={door.door_id}, salto.")
            continue

        try:
            fav1      = {k: _to_float(v, f"fav1[{k}]",      door.id) for k, v in fav.fav1.items()}
            fav2_der  = {k: _to_float(v, f"fav2_der[{k}]",  door.id) for k, v in fav.fav2_der.items()}
            fav2_izq  = {k: _to_float(v, f"fav2_izq[{k}]",  door.id) for k, v in fav.fav2_izq.items()}
            fav3      = {k: _to_float(v, f"fav3[{k}]",      door.id) for k, v in fav.fav3.items()}
        except Exception as e:
            print(f"[WARN] {e}; salto door.id={door.id}.")
            continue
        
        window = db.query(Element).filter(Element.id == el.atributs["ventana_id"]).first()
        orientation, hk, wk = door.orientation, door.high, door.broad
        area = hk * wk
        Ffr  = 1.0 - el.fm
        g_gl = _to_float(window.atributs["fs_vidrio"], "fs_vidrio", door.id)
        yk = calcular_yk(orientation, TILT)
        yk_360 = (yk if yk >= 0 else yk + 360)

        lk_finr_r, dk_finr_r = fav2_der["s"], fav2_der["p"]
        lk_ovh_q, dk_ovh_q   = fav1["d"], fav1["l"]
        lk_fini_i, dk_fini_i = fav2_izq["s"], fav2_izq["p"]

        beta, alfa, e_val, t_val = fav3["beta"], fav3["alfa"], fav3["e"], fav3["t"]

        ecos_alfa = e_val * np.cos(np.radians(90 - alfa))
        wk_alfa   = max(0.0, t_val - ecos_alfa)
        alfa_360  = np.mod(yk_360 - alfa, 360)
        dk_finr_r_l = 0.0 if wk_alfa == 0 else e_val * np.sin(np.radians(90 - alfa))
        por_vent_alfa  = 0.0 if t_val == 0 else (t_val - wk_alfa) / t_val
        por_vent_plana = 1.0 - por_vent_alfa

        ecos_beta = e_val * np.cos(np.radians(beta))
        hk_beta   = max(0.0, t_val - ecos_beta)
        dk_beta   = e_val * np.sin(np.radians(beta))
        por_opaco = 0.0 if t_val == 0 else (t_val - hk_beta) / t_val

        az, alt = df["azimut_phisol_360"], df["alt"]
        mask = np.where(
            yk_360 < 90,  (az > yk_360 + 270) | (az < yk_360 + 90),
            np.where(
                yk_360 > 270, (az > yk_360 - 90) | (az < yk_360 - 270),
                (az > yk_360 - 90) & (az < yk_360 + 90),
            ),
        )
        df[f"door_veo_sol_{i}"] = (mask & (alt > 0)).astype(int)

        # hk_ovh_q_t
        rad_alt  = np.radians(alt)
        rad_diff = np.radians(df["azimut_libro"] - yk)
        expr     = dk_ovh_q * np.tan(rad_alt) / np.cos(rad_diff) - lk_ovh_q
        df[f"door_hk_ovh_q_t_{i}"] = np.clip(expr, 0, hk)

        # wk_finr_r
        expr = dk_finr_r * np.tan(-rad_diff - lk_finr_r)
        df[f"door_wk_finr_r_{i}"] = np.clip(expr, 0, wk)

        # wk_finl_l
        expr = dk_fini_i * np.tan(rad_diff - lk_fini_i)
        df[f"door_wk_finl_l_{i}"] = np.clip(expr, 0, wk)

        # Fsh_dir_k_t_FAV_1_y_FAV2
        veo, hk_ovh = df[f"door_veo_sol_{i}"], df[f"door_hk_ovh_q_t_{i}"]
        wf_r, wf_l  = df[f"door_wk_finr_r_{i}"], df[f"door_wk_finl_l_{i}"]
        df[f"door_Fsh_dir_k_t_FAV_1_y_FAV2_{i}"] = np.where(
            hk == 0, 0,
            veo * (hk_ovh * wk + (hk - hk_ovh) * (wf_r + wf_l)) / (hk * wk)
        )

        # a_Fs
        azi360 = df["azimut_phisol_360"]
        df[f"door_a_Fs_{i}"] = np.where(
            (beta != 0) | (t_val == 0),
            0,
            np.where(alfa > 0,
                     df[f"door_veo_sol_{i}"] * (azi360 < alfa_360),
                     df[f"door_veo_sol_{i}"] * (azi360 > alfa_360))
        ).astype(int)

        # wk_finl_l_l
        ang = np.radians(df["azimut_libro"] - yk)
        expr1 = np.clip(dk_finr_r_l * np.tan(ang - ecos_alfa), 0.0, wk_alfa)
        expr2 = np.clip(dk_finr_r_l * np.tan(ang),             0.0, wk_alfa)
        df[f"door_wk_finl_l_l_{i}"] = np.where(alfa < 0, expr1, expr2)

        # wk_finr_r_r
        ang_b = -ang
        r1 = np.clip(dk_finr_r_l * np.tan(ang_b - ecos_alfa), 0.0, wk_alfa)
        r2 = np.clip(dk_finr_r_l * np.tan(ang_b),             0.0, wk_alfa)
        df[f"door_wk_finr_r_r_{i}"] = np.where(alfa > 0, r1, r2)

        # fsh_dir_k_t_para_a
        inner_a = np.where(
            wk_alfa == 0,
            por_vent_plana + (1 - df[f"door_a_Fs_{i}"]) * por_vent_alfa,
            ((df[f"door_wk_finr_r_r_{i}"] / wk_alfa
            +  df[f"door_wk_finl_l_l_{i}"] / wk_alfa) * por_vent_plana
            + (1 - df[f"door_a_Fs_{i}"]) * por_vent_alfa),
        )
        df[f"door_fsh_dir_k_t_para_a_{i}"] = np.where(t_val == 0, 0,
                                                      df[f"door_veo_sol_{i}"] * inner_a)

        # b_fsh y fsh_dir_k_t_para_b
        ang_tan = np.tan(np.radians(df["alt"]))
        cos_c   = np.cos(np.radians(df["azimut_libro"] - yk))
        raw_b   = dk_beta * ang_tan / cos_c
        clamped = np.where(raw_b < 0, 0.0,
                           np.where(raw_b >= hk_beta, hk_beta, raw_b))
        df[f"door_b_fsh_{i}"] = np.where(alfa != 0, 0.0, clamped)

        inner_b = por_opaco + (df[f"door_b_fsh_{i}"] / hk_beta) * (1 - por_opaco)
        df[f"door_fsh_dir_k_t_para_b_{i}"] = np.where(
            hk_beta == 0, 0.0, df[f"door_veo_sol_{i}"] * inner_b
        )

        # FAR
        clave_obstruccion = f"Obstruccion_{door.orientation}"
        if clave_obstruccion not in df.columns:
            print(f"[WARN] Columna {clave_obstruccion} no encontrada, usando 0.")
            df[f"door_FAR_{i}"] = 0.0
        else:
            meses = {"enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
                     "julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12}
            fila = (df["mes"].str.lower().map(meses) - 1) * 24 + df["hora"] - 23
            fila = fila.clip(lower=0, upper=len(df)-1).astype(int)
            df[f"door_FAR_{i}"] = df[clave_obstruccion].values[fila]

        # **CORREGIDO**  -> usamos .values y axis=1
        df[f"door_Fsh_dir_k_t_{i}"] = np.max(
            df[
                [
                    f"door_Fsh_dir_k_t_FAV_1_y_FAV2_{i}",
                    f"door_fsh_dir_k_t_para_a_{i}",
                    f"door_fsh_dir_k_t_para_b_{i}",
                    f"door_FAR_{i}",
                ]
            ].values,
            axis=1
        )

        # -----------------------------------------------------------------
        #  Q SOLAR  (implementación directa de la fórmula de Excel)
        # -----------------------------------------------------------------
        rad_dir_col  = f"rad_directa_{orientation}"
        rad_dif_col  = f"rad_dif_{orientation}"

        if rad_dir_col not in df.columns or rad_dif_col not in df.columns:
            print(f"[WARN] Columnas {rad_dir_col}/{rad_dif_col} no encontradas; Qsolar=0.")
            df[f"door_w_parcial_{i}"] = 0.0
        else:
            df[f"door_w_parcial_{i}"] = (
                (
                    df[rad_dir_col] * (1 - df[f"door_Fsh_dir_k_t_{i}"]) * df[f"door_veo_sol_{i}"]
                    + df[rad_dif_col]
                )
                * g_gl
                * area
                * (1 - Ffr)
            )

        w_total += df[f"door_w_parcial_{i}"]
    
    df["door_w_total"] = w_total
    return df


def convert_parquet_door_project(
    db: Session,
    project_id: int,
    extra_keep: List[str] | None = None,
) -> Dict[int, Path]:
    """
    Igual que la función de ventanas, pero genera:
      public/sol_doors/<project_id>/<enclosure_id>_sol_door.parquet
    """
    extra_keep = extra_keep or ["azimut_phisol_360", "door_w_total"]

    # ── Parquet de parámetros solares ─────────────────────────────
    p_param_solar = Path("public") / "parametros_solares" / f"{project_id}_parametros_solares.parquet"
    if not p_param_solar.is_file():
        raise FileNotFoundError(p_param_solar)

    # ── Recintos del proyecto ─────────────────────────────────────
    enclosures: List[EnclosureGenerals] = (
        db.query(EnclosureGenerals)
        .filter(EnclosureGenerals.project_id == project_id)
        .all()
    )
    if not enclosures:
        raise ValueError("El proyecto no tiene recintos")

    # ── Carpeta de salida ─────────────────────────────────────────
    out_root = Path("public") / "sol_doors" / str(project_id)
    out_root.mkdir(parents=True, exist_ok=True)

    rutas: Dict[int, Path] = {}

    for enclosure in enclosures:
        enclosure_id = enclosure.id

        p_recinto     = Path("public") / "sol_recinto"     / str(project_id) / f"{enclosure_id}_sol_recinto.parquet"
        p_obstruction = Path("public") / "sol_obstruction" / str(project_id) / f"{enclosure_id}_sol_obstruction.parquet"

        if not p_recinto.is_file() or not p_obstruction.is_file():
            print(f"⚠️ Saltando {enclosure_id}: falta {p_recinto} o {p_obstruction}")
            continue

        # ── Concatenar DataFrames ─────────────────────────────────
        df = pd.concat(
            [pd.read_parquet(p).reset_index(drop=True) for p in (p_recinto, p_param_solar, p_obstruction)],
            axis=1,
        )

        df = calculate_sol_doors(df, enclosure_id, db)

        # ── Columnas de salida ────────────────────────────────────
        door_cols = sorted(
            (
                c for c in df.columns if any(
                    c.startswith(pref) for pref in (
                        "door_veo_sol_", "door_hk_ovh_q_t_", "door_wk_finr_r_",
                        "door_wk_finl_l_", "door_Fsh_dir_k_t_FAV_1_y_FAV2_",
                        "door_a_Fs_", "door_wk_finl_l_l_", "door_wk_finr_r_r_",
                        "door_fsh_dir_k_t_para_a_", "door_b_fsh_",
                        "door_fsh_dir_k_t_para_b_", "door_FAR_", "door_Fsh_dir_k_t_",
                        "door_w_parcial_"
                    )
                )
            ),
            key=lambda s: int(s.rsplit("_", 1)[1]),
        )
        keep_cols = [c for c in extra_keep if c in df.columns]
        df_out = df[keep_cols + door_cols]

        out_path = out_root / f"{enclosure_id}_sol_door.parquet"
        df_out.to_parquet(out_path, engine="pyarrow", index=False)
        print(f"✅ Puertas {enclosure_id} → {out_path}")

        rutas[enclosure_id] = out_path

    return rutas

# ---------------------------------------------------------------------------
# Ejecución de ejemplo
# ---------------------------------------------------------------------------
# if __name__ == "__main__":
    # db = next(get_db())

    # resultado_windows = convert_parquet_window_project(
    #     "public/sol_recinto/chile_peru_arequipa_05_04_2025.processed_promedios_parametros_solares_sol_recinto.parquet",
    #     "public/parametros_solares/chile_peru_arequipa_05_04_2025.processed_promedios_parametros_solares.parquet",
    #     "public/sol_obstruction/chile_peru_arequipa_05_04_2025.processed_promedios_parametros_solares_sol_obstruction.parquet",
    #     49,
    #     db,
    # )
    # print(resultado_windows)

    # resultado_doors = convert_parquet_door_project(
    #     "public/sol_recinto/chile_peru_arequipa_05_04_2025.processed_promedios_parametros_solares_sol_recinto.parquet",
    #    "public/parametros_solares/chile_peru_arequipa_05_04_2025.processed_promedios_parametros_solares.parquet",
    #     "public/sol_obstruction/chile_peru_arequipa_05_04_2025.processed_promedios_parametros_solares_sol_obstruction.parquet",
    #     49,
    #     db,
    # )
    # print(resultado_doors)
