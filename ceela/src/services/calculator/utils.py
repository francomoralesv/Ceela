import pandas as pd
import logging


def convert_walls_to_df(walls_data):
    logger = logging.getLogger("convert_walls_to_df")
    logger.info(
        "[convert_walls_to_df] Iniciando conversión de walls_data a DataFrame. Total elementos: %d", len(walls_data))
    table = []
    for idx, wall in enumerate(walls_data):
        try:
            material_info = wall.get("material_info", {})

            row = {
                "Capa": wall.get("capa", ""),
                "Variables": material_info.get("name", ""),
                "ρ [kg/m³]": material_info.get("p", 1),
                "λ [W/mK]": material_info.get("lambda", 1),
                "d [m]": material_info.get("d", 0.1),
                "R [m²K/W]": material_info.get("R", 1),
                "c [J/kg K]": material_info.get("c", 1),
                "Nd": material_info.get("Nd", 1),
            }
            logger.debug(f"[convert_walls_to_df] Wall #{idx}: {row}")
            table.append(row)
        except Exception as e:
            logger.error(
                f"[convert_walls_to_df] Error procesando wall #{idx}: {wall} - {e}", exc_info=True)
            raise
    df = pd.DataFrame(table)
    logger.info(
        f"[convert_walls_to_df] DataFrame creado con shape: {df.shape}")
    return df
