from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from src.models.entity.enclosure_general import EnclosureGenerals
from src.services.datos.materials import get_nodos_area_by_orientation, get_enclosures_by_project
from src.models.entity.project_table import Project
from typing import Dict, Any, List
import numpy as np


CONSTANTS= {           # Factor de sombra (ejemplo)
    "hre": 4.14,         # Coeficiente de transferencia de calor radiante
    "DTsky": 11,  
    "inclinacion": 90    # Diferencia de temperatura del cielo
}

ORIENTATION_DEGREES = {
    "S": 0,
    "SE": 45,
    "E": 90,
    "NE": 135,
    "N": 180,  # Nota: En la versión original "N" aparece para 180 y también para -180.
    "SO": -45,
    "O": -90,
    "NO": -135,
    "HR": 0,
    "CT": 0
}

def get_degrees(orientacion: str) -> int:
    """
    Retorna el valor en grados correspondiente a la orientación dada.
    
    Si la orientación no se encuentra en el mapeo, retorna None (o se puede modificar para que retorne 
    algún valor por defecto).
    """
    return ORIENTATION_DEGREES.get(orientacion, None)




def nuevo_metodo(df: pd.DataFrame, latitud_deg: float, enclosure_id: int, db: Session) -> Dict[str, Any]:
    # 1. Obtener datos base
    data_list: List[Dict[str, Any]] = get_nodos_area_by_orientation(enclosure_id, db) or []
    ignorar = {"IN", "AD", "FL"}
    orientaciones = {o for o in ORIENTATION_DEGREES if o not in ignorar}
    presentes = {d["Orientacion"] for d in data_list if d["Orientacion"] in orientaciones}
    for o in orientaciones - presentes:
        data_list.append({
            "Orientacion": o, "Area": 0,
            "Absorcion": 0, "Temperatura": 0, "Temperatura_Exterior": 0
        })

    for data in data_list:
        CONSTANTS["Fsh"] = 1
        orient = data["Orientacion"]
        if orient in ignorar: 
            continue
        orientation_grados = get_degrees(orient)
        CONSTANTS['absorcion'] = data["Absorcion"]
        CONSTANTS['inclinacion'] = 0 if orient == "HR" else (180 if orient == "CT" else 90)

        # φ_sky (solo la primera vez en df)
        if "phi_sky_vent" not in df.columns:
            fsky = (180 - CONSTANTS['inclinacion']) / 180
            phi_sky = CONSTANTS['hre'] * CONSTANTS['DTsky'] * fsky
            df['phi_sky_vent'] = -phi_sky
        else:
            fsky = (180 - CONSTANTS['inclinacion']) / 180
            phi_sky = CONSTANTS['hre'] * CONSTANTS['DTsky'] * fsky

        # θ_sol
        term1 = np.sin(np.radians(df["delta"])) * np.sin(np.radians(latitud_deg)) * np.cos(np.radians(CONSTANTS["inclinacion"]))
        term2 = np.sin(np.radians(df["delta"])) * np.cos(np.radians(latitud_deg)) * np.sin(np.radians(CONSTANTS["inclinacion"])) * np.cos(np.radians(orientation_grados))
        term3 = np.cos(np.radians(df["delta"])) * np.cos(np.radians(latitud_deg)) * np.cos(np.radians(CONSTANTS["inclinacion"])) * np.cos(np.radians(df["omega"]))
        term4 = np.cos(np.radians(df["delta"])) * np.sin(np.radians(latitud_deg)) * np.sin(np.radians(CONSTANTS["inclinacion"])) * np.cos(np.radians(orientation_grados)) * np.cos(np.radians(df["omega"]))
        term5 = np.cos(np.radians(df["delta"])) * np.sin(np.radians(CONSTANTS["inclinacion"])) * np.sin(np.radians(orientation_grados)) * np.sin(np.radians(df["omega"]))

        valor_coseno = term1 - term2 + term3 + term4 + term5
        theta_sol = np.degrees(np.arccos(valor_coseno))
        df[f"theta_sol_{orient}"] = theta_sol

        # columnas auxiliares
        df[f"l_dir_{orient}"] = np.maximum(df["G_sol_b"] * np.cos(np.radians(theta_sol)), 0)
        df[f"a_{orient}"] = np.maximum(np.cos(np.radians(theta_sol)), 0)

        # cálculos previos a l_dif
        df[f"lcircum_{orient}"] = df["G_sol_d"] * df["F1"] * df[f"a_{orient}"] / df["b"]
        df[f"ldir_tot_{orient}"] = df[f"lcircum_{orient}"] + df[f"l_dir_{orient}"]
        df["idif_90"] = df.get("idif_90", pd.Series(0, index=df.index))

        # Calcular l_dif de abajo hacia arriba
        col = f"l_dif_{orient}"
        df[col] = np.nan
        inc = CONSTANTS["inclinacion"]
        cos_inc = np.cos(np.radians(inc))
        sin_inc = np.sin(np.radians(inc))

        for i in reversed(df.index):
            Gd_i = df.at[i, "G_sol_d"]
            F1_i = df.at[i, "F1"]
            F2_i = df.at[i, "F2"]
            a_i = df.at[i, f"a_{orient}"]
            b_i = df.at[i, "b"]

            P_i = Gd_i * ((1 - F1_i) * (1 + cos_inc) / 2 + F1_i * a_i / b_i + F2_i * sin_inc)
            if P_i < 0:
                if (i + 1) in df.index:
                    next_ldif = df.at[i+1, col]
                    Gd_next = df.at[i+1, "G_sol_d"]
                else:
                    next_ldif = 0
                    Gd_next = 1
                Q_raw = (next_ldif * Gd_i / Gd_next) if Gd_next != 0 else 0
                Q_i = Q_raw if (np.isfinite(Q_raw) and Q_raw >= 0) else 0
                df.at[i, col] = Q_i
            else:
                df.at[i, col] = P_i

        # totales y phi_solar
        if orient == "CT":
            extra = df["idif_180"]
            CONSTANTS["Fsh"] = 0
        elif orient == "HR":
            extra = df["idif_0"]
        else:
            extra = df["idif_90"]

        df[f"ldif_tot_{orient}"] = df[col] - df[f"lcircum_{orient}"] + extra
        df[f"l_tot_{orient}"] = df[f"ldir_tot_{orient}"] + df[f"ldif_tot_{orient}"]
        df[f"phi_solar_total_{orient}"] = CONSTANTS["absorcion"] * (df[f"ldif_tot_{orient}"] + df[f"ldir_tot_{orient}"] * CONSTANTS["Fsh"]) - phi_sky

        if orient != "CT":
            df[f"rad_directa_{orient}"] = df[f"ldir_tot_{orient}"]
            df[f"rad_dif_{orient}"] = df[f"ldif_tot_{orient}"]

    return {"df": df}
        
        

def calcular_parametros_solares_recinto_parquet(
    db: Session,
    project_id: int
):
    """
    Para cada enclosure del proyecto:
      1. Lee el Parquet base de parámetros solares:
           public/parametros_solares/{project_id}_parametros_solares.parquet
      2. Ejecuta `nuevo_metodo` con la latitud del proyecto y el enclosure_id.
      3. Exporta solo las columnas dinámicas a:
           public/sol_recinto/<project_id>/<enclosure_id>_sol_recinto.parquet
      4. Devuelve {enclosure_id: DataFrame}  (opcional, útil para tests)
    """
    try:
        # ── 0. Datos del proyecto ───────────────────────────────────
        project: Project | None = (
            db.query(Project).filter(Project.id == project_id).first()
        )
        if project is None:
            raise ValueError(f"Project id={project_id} no existe")

        if project.latitude is None:
            raise ValueError("El proyecto no tiene definida la latitud")

        latitud_deg = float(project.latitude)

        # ── 1. Archivo Parquet base ─────────────────────────────────
        base_path = Path("public") / "parametros_solares" / f"{project_id}_parametros_solares.parquet"
        if not base_path.is_file():
            raise FileNotFoundError(f"No existe {base_path}")
        df_radiaciones = pd.read_parquet(base_path)

        # ── 2. Recintos del proyecto ────────────────────────────────
        enclosures: List[EnclosureGenerals] = get_enclosures_by_project(
            project_id, db=db)
        if not enclosures:
            raise ValueError("El proyecto no tiene recintos asociados")

        # ── 3. Carpeta de salida ────────────────────────────────────
        project_dir = Path("public") / "sol_recinto" / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)

        resultados: Dict[int, pd.DataFrame] = {}

        # ── 4. Procesar cada recinto ────────────────────────────────
        for enclosure in enclosures:
            enclosure_id = enclosure.id

            # Copia para no contaminar df_radiaciones
            df_enclosure = df_radiaciones.copy()

            procesado = nuevo_metodo(
                df_enclosure,
                latitud_deg=latitud_deg,
                enclosure_id=enclosure_id,
                db=db,
            )
            df_actualizado = procesado.get("df", df_enclosure)

            # Solo columnas dinámicas
            dyn_cols = [
                c for c in df_actualizado.columns
                if c == "phi_sky_vent" or c.startswith((
                    "mes", "hora", "theta_sol_", "l_dir_", "a_", "l_dif_",
                    "lcircum_", "ldir_tot_", "ldif_tot_",
                    "l_tot_", "phi_solar_total_", "rad_directa_",
                    "rad_dif_"
                ))
            ]
            df_final = df_actualizado[dyn_cols].copy()

            # Guardar
            out_path = project_dir / f"{enclosure_id}_sol_recinto.parquet"
            df_final.to_parquet(out_path, index=False)
            print(f"✅ Parametros solares recinto  {enclosure_id}: exportado en {out_path}")
            resultados[enclosure_id] = df_final

        return {"message": "success"}

    except Exception as err:
        print(f"❌ Error en cálculo solar por recinto: {err}")
        raise
