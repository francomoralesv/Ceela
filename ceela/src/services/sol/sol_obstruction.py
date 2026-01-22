import re
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import Depends
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.obstruction import Division, Orientation
from src.services.database.db_connection import get_db
from src.models.entity.project_table import Project
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import os
from pathlib import Path


CUADRANTES_FAR = {
  "DIVISION 1": 72,
  "DIVISION 2": 36,
  "DIVISION 3": 0,
  "DIVISION 4": -36,
  "DIVISION 5": -72
};


ORIENTACIONES_AZIMUT = {
    "HR":               {"orientacion": "HR", "azimut_360_considerado": None},
    "0° ≤ Az < 22,5°":     {"orientacion": "N",    "azimut_360_considerado": 168.75},
    "22,5° ≤ Az < 45°":    {"orientacion": "NE",   "azimut_360_considerado": 146.25},
    "45° ≤ Az < 67,5°":    {"orientacion": "NE",   "azimut_360_considerado": 123.75},
    "67,5° ≤ Az < 90°":    {"orientacion": "E",    "azimut_360_considerado": 101.25},
    "90° ≤ Az < 112,5°":   {"orientacion": "E",    "azimut_360_considerado":  78.75},
    "112,5° ≤ Az < 135°":  {"orientacion": "SE",   "azimut_360_considerado":  56.25},
    "135° ≤ Az < 157,5°":  {"orientacion": "SE",   "azimut_360_considerado":  33.75},
    "157,5° ≤ Az < 180°":  {"orientacion": "S",    "azimut_360_considerado":  11.25},
    "-180° ≤ Az < -157,5°": {"orientacion": "S",   "azimut_360_considerado": 348.75},
    "-157,5° ≤ Az < -135°": {"orientacion": "SO",  "azimut_360_considerado": 326.25},
    "-135° ≤ Az < -112,5°": {"orientacion": "SO",  "azimut_360_considerado": 303.75},
    "-112,5° ≤ Az < -90°":  {"orientacion": "O",   "azimut_360_considerado": 281.25},
    "-90° ≤ Az < -67,5°":   {"orientacion": "O",   "azimut_360_considerado": 258.75},
    "-67,5° ≤ Az < -45°":   {"orientacion": "NO",  "azimut_360_considerado": 236.25},
    "-45° ≤ Az < -22,5°":   {"orientacion": "NO",  "azimut_360_considerado": 213.75},
    "-22,5° ≤ Az < 0°":     {"orientacion": "N",   "azimut_360_considerado": 191.25},
}


CUADRANTES_FAR = {
    "DIVISION 1": 72,
    "DIVISION 2": 36,
    "DIVISION 3": 0,
    "DIVISION 4": -36,
    "DIVISION 5": -72
}

def calculate_yk_360_division(division, yk_360_central):
    try:
        base = CUADRANTES_FAR[division.upper()]
        angulo = base + yk_360_central

        if angulo < 0:
            return angulo + 360
        elif angulo > 360:
            return angulo - 360
        else:
            return angulo
    except KeyError:
        return 0



def calculate_yk_360_der(yk_360_division, division):
    try:
        resta = np.degrees(np.arctan((division.d / 2) / division.b))
        resultado = yk_360_division - resta

        if resultado < 0:
            return 360 + resultado
        else:
            return resultado
    except Exception:
        return 0
    
    
def calculate_yk_360_izq(yk_360_division, division):
    try:
        suma = np.degrees(np.arctan((division.d / 2) / division.b))
        resultado = yk_360_division + suma

        if resultado > 360:
            return resultado - 360
        else:
            return resultado
    except Exception:
        return 0
    

def calculate_a_sol(division):
    try:
        if division.a == 0:
            return 0
        else:
            return np.degrees(np.arctan(division.a / division.b))
    except Exception:
        return 0
    
    
def calculate_sol_obstruction(
    df: pd.DataFrame,
    enclosure_id: int,
    db: Session
) -> pd.DataFrame:
    
    orientations = db.query(Orientation).filter(
        Orientation.enclosure_id == enclosure_id,
        Orientation.is_deleted == False
    ).all()
    
    for i, orientation in enumerate(orientations, start=1):
        divisions = db.query(Division).filter(
            Division.orientation_id == orientation.id,
            Division.is_deleted == False
        ).all()
        
        suma = 0
        
        for j, division in enumerate(divisions, start=1):
            yk_360_central = ORIENTACIONES_AZIMUT[orientation.azimut]["azimut_360_considerado"]
            yk_360_division = calculate_yk_360_division(division.division.upper(), yk_360_central)
            yk_360_der = calculate_yk_360_der(yk_360_division, division)
            yk_360_izq = calculate_yk_360_izq(yk_360_division, division)
            a_sol = calculate_a_sol(division)

            df[f"Orientacion_{i}_obstruccion_{j}"] = np.where(
                df["a_sol"] == 0,
                0,
                np.where(
                    (df["azimut_phisol_360"] > yk_360_der) &
                    (df["azimut_phisol_360"] < yk_360_izq) &
                    (df["a_sol"] < a_sol),
                    1,
                    0
                )
            )
            
            suma += df[f"Orientacion_{i}_obstruccion_{j}"] 
        
        df[f"Obstruccion_{orientation.orientation}_{i}"] = suma
        
    return df



def convert_parquet_obstruction_project(
    db: Session,
    project_id: int
) -> Dict[int, Path]:
    """
    1. Busca el fichero base:
         public/parametros_solares/{project_id}_parametros_solares.parquet
    2. Para cada enclosure del proyecto calcula las columnas de obstrucción
       y exporta en:
         public/sol_obstruction/<project_id>/<enclosure_id>_sol_obstruction.parquet
    3. Devuelve {enclosure_id: ruta_parquet}
    """
    try:
        # ── 0. Archivo base con a_sol y azimut_phisol_360 ─────────────
        base_path = (
            Path("public") /
            "parametros_solares" /
            f"{project_id}_parametros_solares.parquet"
        )
        if not base_path.is_file():
            raise FileNotFoundError(f"No existe {base_path}")

        df_base = pd.read_parquet(base_path)

        # ── 1. Recintos del proyecto ─────────────────────────────────
        enclosures: List[EnclosureGenerals] = (
            db.query(EnclosureGenerals)
            .filter(EnclosureGenerals.project_id == project_id)
            .all()
        )
        if not enclosures:
            raise ValueError("El proyecto no tiene recintos")

        # ── 2. Carpeta destino ──────────────────────────────────────
        out_dir = Path("public") / "sol_obstruction" / str(project_id)
        out_dir.mkdir(parents=True, exist_ok=True)

        rutas: Dict[int, Path] = {}

        # ── 3. Procesar cada enclosure ──────────────────────────────
        for enclosure in enclosures:
            enclosure_id = enclosure.id

            # Copia para no contaminar df_base
            df = df_base.copy()

            # Calcular obstrucción
            df_obs = calculate_sol_obstruction(df, enclosure_id, db)

            # Columnas a exportar
            obs_cols = sorted(
                (c for c in df_obs.columns if re.match(r"^Orientacion_\d+_obstruccion_\d+", c)),
                key=lambda s: tuple(map(int, re.findall(r"\d+", s)))
            )
            agg_cols = sorted(
                (c for c in df_obs.columns if re.match(r"^Obstruccion_.+_\d+", c))
            )
            df_out = df_obs[obs_cols + agg_cols].copy()

            # Guardar parquet
            out_path = out_dir / f"{enclosure_id}_sol_obstruction.parquet"
            df_out.to_parquet(out_path, engine="pyarrow", index=False)
            print(f"✅ Obstrucción {enclosure_id} → {out_path}")

            rutas[enclosure_id] = out_path

        return rutas

    except Exception as err:
        print(f"❌ Error en convert_parquet_obstruction_project: {err}")
        raise
    

# db = next(get_db()) 
# resultado = convert_parquet_obstruction_project("public/parametros_solares/chile_peru_arequipa_05_04_2025.processed_promedios_parametros_solares.parquet", 277, db)
# print(resultado)