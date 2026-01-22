from pathlib import Path
import pandas as pd
import numpy as np
import os
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.models.entity.project_table import Project
from src.utils.constants import TZ

# Diccionario base sin el valor de "lext"
LEXT_DATA_BASE = {
    "Enero": {"mes": "Enero", "dias_repre": "17-ene", "nday": 17},
    "Febrero": {"mes": "Febrero", "dias_repre": "16-feb", "nday": 47},
    "Marzo": {"mes": "Marzo", "dias_repre": "05-mar", "nday": 64},
    "Abril": {"mes": "Abril", "dias_repre": "15-abr", "nday": 105},
    "Mayo": {"mes": "Mayo", "dias_repre": "15-may", "nday": 135},
    "Junio": {"mes": "Junio", "dias_repre": "11-jun", "nday": 162},
    "Julio": {"mes": "Julio", "dias_repre": "17-jul", "nday": 198},
    "Agosto": {"mes": "Agosto", "dias_repre": "16-ago", "nday": 228},
    "Septiembre": {"mes": "Septiembre", "dias_repre": "15-sep", "nday": 258},
    "Octubre": {"mes": "Octubre", "dias_repre": "15-oct", "nday": 288},
    "Noviembre": {"mes": "Noviembre", "dias_repre": "14-nov", "nday": 318},
    "Diciembre": {"mes": "Diciembre", "dias_repre": "10-dic", "nday": 344}
}

CONSTANTES = {
    "tz": TZ,
    "albedo": 0.20,
    "gsol": 1370.0
}

TABLE_CONSTANTS = [
    {
        "min": float('-inf'),
        "max": 1.07,
        "ind": 1,
        "f11": -0.008,
        "f12": 0.588,
        "f13": -0.062,
        "f21": -0.06,
        "f22": 0.072,
        "f23": -0.022,
    },
    {
        "min": 1.07,
        "max": 1.23,
        "ind": 2,
        "f11": 0.13,
        "f12": 0.683,
        "f13": -0.151,
        "f21": 0.019,
        "f22": 0.066,
        "f23": -0.029,
    },
    {
        "min": 1.23,
        "max": 1.50,
        "ind": 3,
        "f11": 0.33,
        "f12": 0.487,
        "f13": -0.221,
        "f21": 0.055,
        "f22": -0.064,
        "f23": -0.026,
    },
    {
        "min": 1.50,
        "max": 1.95,
        "ind": 4,
        "f11": 0.568,
        "f12": 0.187,
        "f13": -0.295,
        "f21": 0.109,
        "f22": 0.152,
        "f23": -0.014,
    },
    {
        "min": 1.95,
        "max": 2.80,
        "ind": 5,
        "f11": 0.873,
        "f12": -0.392,
        "f13": -0.362,
        "f21": 0.226,
        "f22": -0.462,
        "f23": 0.001,
    },
    {
        "min": 2.80,
        "max": 4.50,
        "ind": 6,
        "f11": 1.132,
        "f12": -1.237,
        "f13": -0.412,
        "f21": 0.288,
        "f22": -0.823,
        "f23": 0.056,
    },
    {
        "min": 4.50,
        "max": 6.20,
        "ind": 7,
        "f11": 1.06,
        "f12": -1.6,
        "f13": -0.359,
        "f21": 0.264,
        "f22": -1.127,
        "f23": 0.131,
    },
    {
        "min": 6.20,
        "max": float('inf'),
        "ind": 8,
        "f11": 0.678,
        "f12": -0.327,
        "f13": -0.25,
        "f21": 0.156,
        "f22": -1.377,
        "f23": 0.251,
    },
]

def build_lext_data(constantes, base_data):
    """
    A partir del diccionario base de LEXT_DATA (sin 'lext'),
    calcula y agrega la clave 'lext' para cada mes usando la fórmula:
    
        lext = gsol * (1 + 0.033 * cos(radians(360/365 * nday)))
        
    Retorna un nuevo diccionario con los datos completos.
    """
    lext_data = {}
    for mes, data in base_data.items():
        nday = data["nday"]
        lext = constantes["gsol"] * (1 + 0.033 * np.cos(np.radians((360/365) * nday)))
        new_data = data.copy()
        new_data["lext"] = lext
        lext_data[mes] = new_data
    return lext_data

def get_row_for_m_air_mass(m_value, table=TABLE_CONSTANTS):
    """
    Recorre table y devuelve el primer diccionario
    cuyo rango [min, max) contiene m_value.
    Si no encuentra ninguno, devuelve None.
    """
    for row in table:
        if row["min"] <= m_value < row["max"]:
            return row
    return None

# ========================
# 1) CÁLCULO POR FILA
# ========================
def calcular_parametros_solares(df: pd.DataFrame,
                                latitud_deg: float,
                                longitud_deg: float) -> pd.DataFrame:
    """
    Calcula todos los parámetros solares necesarios a partir de un DataFrame
    que contiene al menos las columnas 'mes' y 'hora'.
    (… no se ha modificado nada en esta función …)
    """
    # ------------------------------------------------------------------
    # -------------  TODA TU LÓGICA ORIGINAL SE QUEDA IGUAL ------------
    # ------------------------------------------------------------------
    LEXT_DATA = build_lext_data(CONSTANTES, LEXT_DATA_BASE)

    tf = TimezoneFinder()
    
    tz_name = tf.timezone_at(lat=latitud_deg, lng=longitud_deg)
    tz = ZoneInfo(tz_name)
    
    now_utc   = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(tz)

    offset_horas = now_local.utcoffset().total_seconds() / 3600
    print("Offset Horas: ", offset_horas)
    
    CONSTANTES['tz'] = offset_horas
    
    t_shift = CONSTANTES["tz"] - longitud_deg / 15
    lat_rad = np.radians(latitud_deg)

    df['nday'] = df['mes'].map(lambda m: LEXT_DATA.get(m, {}).get('nday'))
    if df['nday'].isnull().any():
        raise ValueError("Algunos meses no se han mapeado correctamente a nday.")

    df['Rdc'] = 360 / 365 * df['nday']
    df['delta'] = (
        0.33281
        - 22.984 * np.cos(np.radians(df['Rdc']))
        - 0.3499 * np.cos(np.radians(2 * df['Rdc']))
        - 0.1398 * np.cos(np.radians(3 * df['Rdc']))
        + 3.7872 * np.sin(np.radians(df['Rdc']))
        + 0.03205 * np.sin(np.radians(2 * df['Rdc']))
        + 0.07187 * np.sin(np.radians(3 * df['Rdc']))
    )

    # --- teq ---
    def calcular_teq(nday):
        if nday < 21:
            return 2.6 + 0.44 * nday
        elif 21 <= nday < 136:
            return 5.2 + 9 * np.cos(np.radians((nday - 43) * 0.0357 * 180 / np.pi))
        elif 136 <= nday < 241:
            return 1.4 - 5 * np.cos(np.radians((nday - 135) * 0.0449 * 180 / np.pi))
        elif 241 <= nday < 336:
            return -6.3 - 10 * np.cos(np.radians((nday - 306) * 0.036 * 180 / np.pi))
        else:
            return 0.45 * (nday - 359)

    df['teq'] = df['nday'].apply(calcular_teq)

    df['t_sol'] = df['hora'] - df['teq'] / 60 - t_shift

    omega_val = 180 / 12 * (12.5 - df['t_sol'])
    df['omega'] = np.where(
        omega_val > 180, omega_val - 360,
        np.where(omega_val < -180, omega_val + 360, omega_val)
    )

    df['alt'] = np.degrees(np.arcsin(
        np.sin(np.radians(df['delta'])) * np.sin(lat_rad) +
        np.cos(np.radians(df['delta'])) * np.cos(lat_rad) * np.cos(np.radians(df['omega']))
    ))

    df['a_sol'] = df['alt'].apply(lambda x: 0 if x < 0.0001 else x)

    # ================= NUEVAS COLUMNAS DE EXCEL (sin cambios) =========
    df['theta_z_asol'] = 90 - df['alt']
    df['theta_z'] = 90 - df['a_sol']
    df['sin_phisol_aux1'] = (
        np.cos(np.radians(df['delta'])) *
        np.sin(np.radians(180 - df['omega']))
    ) / np.cos(np.arcsin(np.sin(np.radians(df['a_sol']))))
    df['cos_phisol_aux1'] = (
        np.cos(np.radians(latitud_deg)) * np.sin(np.radians(df['delta'])) +
        np.sin(np.radians(latitud_deg)) * np.cos(np.radians(df['delta'])) *
        np.cos(np.radians(180 - df['omega']))
    ) / np.cos(np.arcsin(np.sin(np.radians(df['a_sol']))))
    df['phisol_aux2'] = (
        np.degrees(
            np.arcsin(
                np.cos(np.radians(df['delta'])) *
                np.sin(np.radians(180 - df['omega']))
            )
        )
    ) / np.cos(np.arcsin(np.sin(np.radians(df['a_sol']))))
    df['azimut_libro'] = (
        np.sign(df['omega']) *
        np.abs(
            np.degrees(
                np.arccos(
                    (
                        np.cos(np.radians(df['theta_z_asol'])) * np.sin(np.radians(latitud_deg))
                        - np.sin(np.radians(df['delta']))
                    ) / (
                        np.sin(np.radians(df['theta_z_asol'])) * np.cos(np.radians(latitud_deg))
                    )
                )
            )
        )
    )

    df['m_air_mass'] = np.where(
        df['a_sol'] >= 10,
        1 / np.sin(np.radians(df['a_sol'])),
        1 / (np.sin(np.radians(df['a_sol'])) + 0.15 * ((df['a_sol'] + 3.885) ** (-1.253)))
    )

    df['b'] = np.maximum(np.cos(np.radians(85)), np.cos(np.radians(df['theta_z_asol'])))

    df['e'] = np.where(
        df['G_sol_d'] == 0,
        999,
        ((df['G_sol_d'] + df['G_sol_b']) / df['G_sol_d'] + 1.014 * ((np.pi/180 * df['alt'])**3)) /
        (1 + 1.014 * ((np.pi/180 * df['alt'])**3))
    )

    lext_map = {m: d["lext"] for m, d in LEXT_DATA.items()}
    df['Delta'] = df['m_air_mass'] * df['G_sol_d'] / df['mes'].map(lext_map)

    df["table_row"] = df["e"].apply(get_row_for_m_air_mass)
    df["f11"] = df["table_row"].apply(lambda x: x["f11"] if x else np.nan)
    df["f12"] = df["table_row"].apply(lambda x: x["f12"] if x else np.nan)
    df["f13"] = df["table_row"].apply(lambda x: x["f13"] if x else np.nan)
    df["f21"] = df["table_row"].apply(lambda x: x["f21"] if x else np.nan)
    df["f22"] = df["table_row"].apply(lambda x: x["f22"] if x else np.nan)
    df["f23"] = df["table_row"].apply(lambda x: x["f23"] if x else np.nan)

    df["F1"] = np.maximum(0, df["f11"] + df["f12"] * df["Delta"] +
                             df['f13'] * (np.pi * df['theta_z'] / 180))
    df["F2"] = df["f21"] + df["f22"] * df["Delta"] + \
               df["f23"] * (np.pi * df['theta_z'] / 180)

    df.drop(columns=["table_row"], inplace=True)

    df['idif_90'] = (df['G_sol_d'] + df['G_sol_b'] *
                     np.sin(np.radians(df['a_sol']))) * CONSTANTES['albedo'] * (1 - np.cos(np.radians(90))) / 2
    df['idif_0'] = (df['G_sol_d'] + df['G_sol_b'] *
                    np.sin(np.radians(df['a_sol']))) * CONSTANTES['albedo'] * (1 - np.cos(np.radians(0))) / 2
    df['idif_180'] = (df['G_sol_d'] + df['G_sol_b'] *
                      np.sin(np.radians(df['a_sol']))) * CONSTANTES['albedo'] * (1 - np.cos(np.radians(180))) / 2

    df["azimut_phisol_360"] = np.where(
        df["azimut_libro"] < 0,
        df["azimut_libro"] + 360,
        df["azimut_libro"]
    )

    return df


# ========================
# 2) PROCESO COMPLETO PARQUET
# ========================
def calcular_parametros_solares_parquet(file_path: str,
                                        db: Session,
                                        project_id: int):
    """
    Lee un Parquet de radiaciones, obtiene lat/long del proyecto indicado
    y genera un nuevo Parquet con los parámetros solares calculados.
    """
    try:
        file_path = Path(file_path)
        if "uploads" in file_path.parts:
            parts = list(file_path.parts)
            idx = parts.index("uploads")
            parts[idx] = "radiaciones"
            file_path = Path(*parts)

        # Cambiar sufijo .processed.parquet → .processed_promedios.parquet
        if file_path.name.endswith(".processed.parquet"):
            file_path = file_path.with_name(
                file_path.name.replace(".processed.parquet", ".processed_promedios.parquet")
            )

        # Convertir a string si lo necesitas
        file_path = str(file_path)
        print("File Path: ", file_path)
        file_path = os.path.normpath(file_path)
        if os.sep == '\\':
            # Adaptación para Windows: usar separadores propios de Windows
            file_path = file_path.replace(os.path.normpath("public/uploads") + os.sep, os.path.normpath("public/radiaciones") + os.sep)
        else:
            # Adaptación para Linux/Unix: se usan '/'
            file_path = file_path.replace("public/uploads/", "public/radiaciones/")
        file_path = file_path.replace(".processed.parquet", ".processed_promedios.parquet")
        print("File Path after adaptation: ", file_path)
        # ────────────── 1. Cargar radiaciones ──────────────
        df = pd.read_parquet(file_path)
        required_cols = ['mes', 'hora', 'rad GH']
        faltantes = [c for c in required_cols if c not in df.columns]
        if faltantes:
            raise ValueError(f"Faltan columnas requeridas: {faltantes}")

        # ────────────── 2. Obtener latitud y longitud del proyecto ──────────────
        project: Project | None = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise ValueError(f"No existe un Project con id={project_id}")

        if project.latitude is None or project.longitude is None:
            raise ValueError("El proyecto no tiene definidos latitude / longitude")

        latitud_deg = float(project.latitude)
        longitud_deg = float(project.longitude)

        # ────────────── 3. Normalizar nombre del mes ──────────────
        df['mes'] = df['mes'].astype(str).str.capitalize()

        # ────────────── 4. Calcular parámetros solares ──────────────
        df = calcular_parametros_solares(df, latitud_deg, longitud_deg)

        # ────────────── 5. Seleccionar columnas finales ──────────────
        final_cols = [
            'mes', 'hora', 'G_sol_b', 'G_sol_d', 'nday', 'Rdc', 'delta', 'teq', 't_sol',
            'omega', 'alt', 'a_sol', 'theta_z', 'theta_z_asol', 'sin_phisol_aux1',
            'cos_phisol_aux1', 'phisol_aux2', 'azimut_libro', 'm_air_mass',
            'b', 'e', 'Delta', 'F1', 'F2', 'f11', 'f12', 'f13',
            'f21', 'f22', 'f23', 'idif_90', 'idif_0', 'idif_180', 'azimut_phisol_360'
        ]
        df_final = df[final_cols].copy()

        # ────────────── 6. Guardar Parquet ──────────────
        output_dir = os.path.join("public", "parametros_solares")
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"{project_id}_parametros_solares.parquet")

        df_final.to_parquet(output_path, index=False)
        print(f"✅ Parametros solares exitosamente en: {output_path}")
        return df_final.to_dict(orient="records")

    except Exception as err:
        print(f"❌ Error al procesar el archivo: {err}")
        return None
