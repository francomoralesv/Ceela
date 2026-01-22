import calendar
import json
import logging
import os
import pickle
import shutil
from datetime import datetime

import numpy as np
import pandas as pd
from fastapi import HTTPException

from src.calc_engine.enclosure_processor import EnclosureProcessor
from src.calc_engine.input_data_calculator import InputDataCalculator
from src.models.entity.enclosure_general import EnclosureGenerals
from src.services.agua_caliente.agua_caliente_service import get_agua_caliente_by_project
from src.services.calculator.heating_config_service import HeatingConfigService
from src.services.datos.recintos import get_enclosure_by_id, get_info_recinto

from src.utils.constants import public_folder
from src.utils.logging import logger
from src.utils.redis_utils import get_redis_sync
from src.services.calculation_result.calculation_result_service import upsert_calculation_result

# Configure logger
logger = logging.getLogger(__name__)


class ResultCalculator:
    def __init__(self, project_id):
        self.project_id = project_id
        pass

    def get_demand_cache(self, project_id, enclosure_id):
        cache = get_redis_sync()
        data = cache.get(f'project:{project_id}:{enclosure_id}:df_demand_pickle')
        if data:
            return pickle.loads(data)
        else:
            raise HTTPException(status_code=404, detail="Cache not found for demand data")

    def get_co2_eq_energia_primaria(self, project_id, db=None):
        try:
            if project_id and db:
                agua_caliente = get_agua_caliente_by_project(
                    project_id, current_user=None, db=db)
                logger.info(f"Getting CO2 from agua_caliente data: {agua_caliente}")
                return agua_caliente.energia_primaria
        except Exception as e:
            logger.error(f"Error getting CO2 data: {str(e)}")
            return 1000  # Return default value on error

    def get_demand_acs(self, project_id, db=None):
        try:
            if project_id and db:
                agua_caliente = get_agua_caliente_by_project(
                    project_id, current_user=None, db=db)
                logger.info(f"Getting CO2 from agua_caliente data: {agua_caliente}")
                return agua_caliente.demanda_acs
        except Exception as e:
            logger.error(f"Error getting CO2 data: {str(e)}")
            return 1000  # Return default value on error

    def calculate_final_indicators(self, result_by_enclosure_v2, base_by_enclosure=None, co2_eq_energia_primaria=1000,
                                   demanda_acs=10):
        """
        Calculate final indicators based on result_by_enclosure_v2.

        Args:
            result_by_enclosure_v2: Result data from the main calculation
            base_by_enclosure: Base case data for comparison
            co2_eq_energia_primaria: CO2 equivalent from primary energy sources (default: 0)

        Returns:
            dict: Dictionary with final indicators:
                - demanda_calefaccion_final: Sum of heating demands divided by sum of surfaces
                - demanda_calefaccion_final2: Sum of all heating demands
                - demanda_calef_vs: 1 - (sum of heating demands / sum of base case heating demands)
                - demanda_ref_final: Sum of cooling demands divided by sum of surfaces
                - demanda_ref_final2: Sum of all cooling demands
                - demanda_ref_vs: 1 - (sum of cooling demands / sum of base case cooling demands)
                - demanda_iluminacion_final: Sum of illumination demands divided by sum of surfaces
                - demanda_iluminacion_final2: Sum of all illumination demands
                - demanda_iluminacion_vs: 1 - (sum of illumination demands / sum of base case illumination demands)
                - consumo_calefaccion_final: Sum of (heating consumptions * surfaces) divided by sum of surfaces
                - consumo_calefaccion_final2: Sum of all heating consumptions
                - consumo_calef_vs: 1 - (sum of heating consumptions / sum of base case heating consumptions)
                - consumo_refrigeracion_final: Sum of (cooling consumptions * surfaces) divided by sum of surfaces
                - consumo_refrigeracion_final2: Sum of all cooling consumptions
                - consumo_ref_vs: 1 - (sum of cooling consumptions / sum of base case cooling consumptions)
                - consumo_iluminacion_final: Sum of (illumination consumptions * surfaces) divided by sum of surfaces
                - consumo_iluminacion_final2: Sum of all illumination consumptions
                - consumo_iluminacion_vs: 1 - (sum of illumination consumptions / sum of base case illumination consumptions)
                - consumo_vs_caso_base: 1 - (sum of total consumptions / sum of base case total consumptions)
                - disconfort_calef: Sum of all heating discomfort hours across all enclosures
                - disconfort_ref: Sum of all cooling discomfort hours across all enclosures
                - disconfort_total: Sum of all discomfort hours (heating + cooling) across all enclosures
                - disconfort_vs: 1 - (sum of total discomfort hours / sum of base case total discomfort hours)
                - co2_eq_total: Total CO2 equivalent emissions (sum of all enclosures' CO2 emissions + primary energy CO2)
                - co2_eq_vs_caso_base: 1 - (total CO2 equivalent emissions / base case total CO2 equivalent emissions)
        """
        print(f"[DEBUG] calculate_final_indicators - base_by_enclosure: {base_by_enclosure}")
        # [MOD] A partir de aquí, si recibimos base_by_enclosure, la utilizamos como base real (recintos con is_base=true).
        #       Si no, se devuelven VS=0. Se eliminaron los aleatorios para VS.

        # Convert from JSON string to list if needed
        proposed = json.loads(result_by_enclosure_v2) if isinstance(result_by_enclosure_v2, str) else (
                    result_by_enclosure_v2 or [])
        base_list = json.loads(base_by_enclosure) if isinstance(base_by_enclosure, str) else (base_by_enclosure or [])

        if not proposed:
            import random
            return {
                "demanda_calefaccion_final": 0,
                "demanda_calefaccion_final2": 0,
                "demanda_calef_vs": 0,
                "demanda_ref_final": 0,
                "demanda_ref_final2": 0,
                "demanda_ref_vs": 0,
                "demanda_iluminacion_final": 0,
                "demanda_iluminacion_final2": 0,
                "demanda_iluminacion_vs": 0,
                "consumo_calefaccion_final": 0,
                "consumo_calefaccion_final2": 0,
                "consumo_calef_vs": 0,
                "consumo_refrigeracion_final": 0,
                "consumo_refrigeracion_final2": 0,
                "consumo_ref_vs": 0,
                "consumo_iluminacion_final": 0,
                "consumo_iluminacion_final2": 0,
                "consumo_iluminacion_vs": 0,
                "consumo_vs_caso_base": 0,
                "disconfort_calef": 0,
                "disconfort_ref": 0,
                "disconfort_total": 0,
                "disconfort_vs": 0,
                "co2_eq_total": co2_eq_energia_primaria,
                "co2_eq_vs_caso_base": 0,
                "demanda_acs_m2": 0,
                "demanda_acs": demanda_acs,
                "demanda_acs_vs_caso_base": 0,
                "consumo_acs_m2": 0,
                "consumo_acs": co2_eq_energia_primaria,
                "consumo_acs_vs_caso_base": 0
            }

        try:
            # [MOD] Helpers para agregación ponderada por superficie
            def _agg(enclosures):
                total_surface = sum(float(e.get("superficie", 0) or 0) for e in enclosures)

                def wsum(key):
                    return sum(float(e.get(key, 0) or 0) * float(e.get("superficie", 0) or 0) for e in enclosures)

                def wavg(key):
                    return (wsum(key) / total_surface) if total_surface > 0 else 0.0

                def wavg_hours(key):
                    total_weighted = sum(float(e.get(key, 0) or 0) * float(e.get("superficie", 0) or 0) for e in enclosures)
                    return (total_weighted / total_surface) if total_surface > 0 else 0.0

                def avg_simple(key):
                    """Promedio simple (sin ponderar por superficie) - para horas de disconfort"""
                    n = len(enclosures)
                    return sum(float(e.get(key, 0) or 0) for e in enclosures) / n if n > 0 else 0.0

                def sum_raw(key):
                    """Suma directa de valores absolutos (raw) sin multiplicar por superficie"""
                    return sum(float(e.get(key, 0) or 0) for e in enclosures)

                # Demandas y consumos por m2 (promedios ponderados)
                d_calef = wavg("demanda_calefaccion")
                d_ref = wavg("demanda_refrigeracion")
                d_ilum = wavg("demanda_iluminacion")
                c_calef = wavg("consumo_calefaccion")
                c_ref = wavg("consumo_refrigeracion")
                c_ilum = d_ilum  # consumo_iluminación_final = demanda_iluminación_final

                # Totales absolutos (kWh) - usar valores raw en lugar de wsum para demandas
                d_calef_surface = sum_raw("demanda_calefaccion_raw")
                d_ref_surface = sum_raw("demanda_refrigeracion_raw")
                d_ilum_surface = wsum("demanda_iluminacion")
                c_calef_surface = wsum("consumo_calefaccion")  # [MOD] totales de consumo por tipo (kWh)
                c_ref_surface = wsum("consumo_refrigeracion")
                c_ilum_surface = d_ilum_surface  # (iluminación = demanda)
                total_cons_abs = c_calef_surface + c_ref_surface + c_ilum_surface

                # Disconfort: promedio simple de horas (NO ponderado por superficie)
                # Las horas son un indicador temporal, no espacial
                dis_calef = avg_simple("hrs_disconfort_calefaccion")
                dis_ref = avg_simple("hrs_disconfort_refrigeracion")
                dis_total = avg_simple("hrs_disconfort_total")

                # CO2 absoluto de recintos
                co2_abs = sum(float(e.get("co2_eq_total", 0) or 0) for e in enclosures)

                # Caso base: también promedio simple para horas de disconfort
                cb_dis_calef = avg_simple("caso_base_hrs_disconfort_calefaccion")
                cb_dis_ref = avg_simple("caso_base_hrs_disconfort_refrigeracion")
                cb_dis_total = avg_simple("caso_base_hrs_disconfort_total")

                return {
                    "surf": total_surface,
                    "d_calef": d_calef, "d_ref": d_ref, "d_ilum": d_ilum,
                    "d_calef_surface": d_calef_surface, "d_ref_surface": d_ref_surface,
                    "d_ilum_surface": d_ilum_surface,
                    "c_calef": c_calef, "c_ref": c_ref, "c_ilum": c_ilum,
                    "c_calef_surface": c_calef_surface, "c_ref_surface": c_ref_surface,
                    "c_ilum_surface": c_ilum_surface,
                    "total_cons_abs": total_cons_abs,
                    "dis_calef": dis_calef, "dis_ref": dis_ref, "dis_total": dis_total,
                    "co2_abs": co2_abs,
                    "cb_dis_calef": cb_dis_calef, "cb_dis_ref": cb_dis_ref, "cb_dis_total": cb_dis_total
                }

            prop = _agg(proposed)
            base_agg = _agg(base_list) if base_list else None

            # Calculate final indicators - usando promedios ponderados por superficie
            demanda_calefaccion_final = prop["d_calef"]
            demanda_calefaccion_final2 = prop["d_calef_surface"]
            demanda_ref_final = prop["d_ref"]
            demanda_ref_final2 = prop["d_ref_surface"]
            demanda_iluminacion_final = prop["d_ilum"]
            demanda_iluminacion_final2 = prop["d_ilum_surface"]

            # Calculate consumption metrics
            consumo_calefaccion_final = prop["c_calef"]
            consumo_calefaccion_final2 = prop["c_calef_surface"]
            consumo_refrigeracion_final = prop["c_ref"]
            consumo_refrigeracion_final2 = prop["c_ref_surface"]
            consumo_iluminacion_final = demanda_iluminacion_final
            consumo_iluminacion_final2 = prop["c_ilum_surface"]

            # Calculate discomfort totals - promedio simple (no ponderado por superficie)
            total_disconfort_calef_final = prop["dis_calef"]
            total_disconfort_ref_final = prop["dis_ref"]
            total_disconfort_total = prop["dis_total"]

            # Calculate total CO2 emissions (project's emissions + primary energy emissions)
            total_co2_eq = prop["co2_abs"] + co2_eq_energia_primaria

            # Calculate vs values usando base real si existe
            def _vs(a, b):
                try:
                    a = float(a or 0);
                    b = float(b or 0)
                    return 1.0 - (a / b) if b > 0 else 0.0
                except Exception:
                    return 0.0

            if base_agg and base_agg["surf"] > 0:
                demanda_calef_vs = _vs(prop["d_calef"], base_agg["d_calef"])
                demanda_ref_vs = _vs(prop["d_ref"], base_agg["d_ref"])
                demanda_iluminacion_vs = _vs(prop["d_ilum"], base_agg["d_ilum"])

                consumo_calef_vs = _vs(prop["c_calef"], base_agg["c_calef"])
                consumo_ref_vs = _vs(prop["c_ref"], base_agg["c_ref"])
                consumo_iluminacion_vs = _vs(prop["c_ilum"], base_agg["c_ilum"])

                consumo_vs_caso_base = _vs(prop["total_cons_abs"], base_agg["total_cons_abs"])
                disconfort_vs = _vs(prop["dis_total"], base_agg["dis_total"])

                base_total_co2_eq = base_agg["co2_abs"] + co2_eq_energia_primaria
                co2_eq_vs_caso_base = _vs(total_co2_eq, base_total_co2_eq)
            else:
                # Sin base real
                demanda_calef_vs = 0
                demanda_ref_vs = 0
                demanda_iluminacion_vs = 0
                consumo_calef_vs = 0
                consumo_ref_vs = 0
                consumo_iluminacion_vs = 0
                consumo_vs_caso_base = 0
                disconfort_vs = 0
                co2_eq_vs_caso_base = 0

            # ACS por m2 sobre superficie propuesta
            demanda_acs_m2 = round(demanda_acs / prop["surf"], 2) if prop["surf"] > 0 else 0
            consumo_acs_m2 = round(co2_eq_energia_primaria / prop["surf"], 2) if prop["surf"] > 0 else 0

            # === [MOD NUEVO] VS de ACS por m² respecto al BASE ===

            demanda_acs_vs_caso_base_val = _vs(demanda_acs_m2, demanda_acs_m2)
            consumo_acs_vs_caso_base_val = _vs(round(co2_eq_energia_primaria, 2), round(co2_eq_energia_primaria, 2))

            # === FIN MOD ===

            # [MOD] También exponemos en final_indicators los agregados del BASE (para el front-end)
            base_fields = {}
            if base_agg and base_agg["surf"] > 0:
                # [MOD] ACS por m² del BASE:

                base_fields = {
                    "base_demanda_calefaccion_final": round(base_agg["d_calef"], 2),
                    "base_demanda_calefaccion_final2": round(base_agg["d_calef_surface"], 2),
                    "base_demanda_ref_final": round(base_agg["d_ref"], 2),
                    "base_demanda_ref_final2": round(base_agg["d_ref_surface"], 2),
                    "base_demanda_iluminacion_final": round(base_agg["d_ilum"], 2),
                    "base_demanda_iluminacion_final2": round(base_agg["d_ilum_surface"], 2),

                    "base_consumo_calefaccion_final": round(base_agg["c_calef"], 2),
                    "base_consumo_calefaccion_final2": round(base_agg["c_calef_surface"], 2),
                    "base_consumo_refrigeracion_final": round(base_agg["c_ref"], 2),
                    "base_consumo_refrigeracion_final2": round(base_agg["c_ref_surface"], 2),
                    "base_consumo_iluminacion_final": round(base_agg["c_ilum"], 2),
                    "base_consumo_iluminacion_final2": round(base_agg["c_ilum_surface"], 2),

                    # ⚠️ Lo que pediste para el front:
                    "caso_base_hrs_disconfort_calefaccion": round(base_agg["dis_calef"], 2),
                    "caso_base_hrs_disconfort_refrigeracion": round(base_agg["dis_ref"], 2),
                    "caso_base_hrs_disconfort_total": round(base_agg["dis_total"], 2),

                    # CO2 total base (recintos + primaria)
                    "co2_eq_total_base": round(base_agg["co2_abs"] + co2_eq_energia_primaria, 2),

                    # [MOD] NUEVO: Demanda (Refrigeración + ACS) del BASE
                    #   - Por m²: demanda_ref_base (kWh/m²·año) + demanda_acs_base_m2
                    #   - Total:  demanda_ref_base (kWh/año)   + demanda_acs (kWh/año)
                    "base_demanda_ref_acs_final": demanda_acs_m2,
                    "base_demanda_ref_acs_final2": round(demanda_acs, 2),

                    # [MOD] NUEVO: Solo ACS (BASE) como consumo
                    "base_consumo_acs_final": consumo_acs_m2,
                    "base_consumo_acs_final2": round(co2_eq_energia_primaria, 2),
                }

            return {
                "demanda_calefaccion_final": round(demanda_calefaccion_final, 2),
                "demanda_calefaccion_final2": round(demanda_calefaccion_final2, 2),
                "demanda_calef_vs": round(demanda_calef_vs, 2),
                "demanda_ref_final": round(demanda_ref_final, 2),
                "demanda_ref_final2": round(demanda_ref_final2, 2),
                "demanda_ref_vs": round(demanda_ref_vs, 2),
                "demanda_iluminacion_final": round(demanda_iluminacion_final, 2),
                "demanda_iluminacion_final2": round(demanda_iluminacion_final2, 2),
                "demanda_iluminacion_vs": round(demanda_iluminacion_vs, 2),
                "consumo_calefaccion_final": round(consumo_calefaccion_final, 2),
                "consumo_calefaccion_final2": round(consumo_calefaccion_final2, 2),
                "consumo_calef_vs": round(consumo_calef_vs, 2),
                "consumo_refrigeracion_final": round(consumo_refrigeracion_final, 2),
                "consumo_refrigeracion_final2": round(consumo_refrigeracion_final2, 2),
                "consumo_ref_vs": round(consumo_ref_vs, 2),
                "consumo_iluminacion_final": round(consumo_iluminacion_final, 2),
                "consumo_iluminacion_final2": round(consumo_iluminacion_final2, 2),
                "consumo_iluminacion_vs": round(consumo_iluminacion_vs, 2),
                "consumo_vs_caso_base": round(consumo_vs_caso_base, 2),
                "disconfort_calef": round(total_disconfort_calef_final, 2),
                "disconfort_ref": round(total_disconfort_ref_final, 2),
                "disconfort_total": round(total_disconfort_total, 2),
                "disconfort_vs": round(disconfort_vs, 2),
                "co2_eq_total": round(total_co2_eq, 2),
                "co2_eq_vs_caso_base": round(co2_eq_vs_caso_base, 2),
                "demanda_acs_m2": demanda_acs_m2,
                "demanda_acs": round(demanda_acs, 2),
                "demanda_acs_vs_caso_base": round(demanda_acs_vs_caso_base_val, 2),
                "consumo_acs_m2": consumo_acs_m2,
                "consumo_acs": round(co2_eq_energia_primaria, 2),
                "consumo_acs_vs_caso_base": round(consumo_acs_vs_caso_base_val, 2),
                **base_fields  # [MOD] anexamos los indicadores del base aquí
            }
        except Exception as e:
            logger.error(f"Error calculating final indicators: {str(e)}")
            import traceback
            traceback.format_exc()
            return {
                "demanda_calefaccion_final": 0,
                "demanda_calefaccion_final2": 0,
                "demanda_calef_vs": 0,
                "demanda_ref_final": 0,
                "demanda_ref_final2": 0,
                "demanda_ref_vs": 0,
                "demanda_iluminacion_final": 0,
                "demanda_iluminacion_final2": 0,
                "demanda_iluminacion_vs": 0,
                "consumo_calefaccion_final": 0,
                "consumo_calefaccion_final2": 0,
                "consumo_calef_vs": 0,
                "consumo_refrigeracion_final": 0,
                "consumo_refrigeracion_final2": 0,
                "consumo_ref_vs": 0,
                "consumo_iluminacion_final": 0,
                "consumo_iluminacion_final2": 0,
                "consumo_iluminacion_vs": 0,
                "consumo_vs_caso_base": 0,
                "disconfort_calef": 0,
                "disconfort_ref": 0,
                "disconfort_total": 0,
                "disconfort_vs": 0,
                "co2_eq_total": co2_eq_energia_primaria,
                "co2_eq_vs_caso_base": 0,
                "error": str(e)
            }

    async def execute_v2(self, force_calculation=False, force_data=False, db=None):

        project_id = self.project_id
        if project_id is None:
            raise HTTPException(
                status_code=400, detail="Project ID is required.")
        input_data = InputDataCalculator(
            project_id=project_id,
            db=db
        )
        enclosure_processor = EnclosureProcessor(
            data=input_data,
            db=db
        )
        await enclosure_processor.process_enclosures(force_data)
        enclosure_processor.post_process_enclosures()
        logger.info("Finished processing enclosures, starting calculations...")
        return True

    async def execute_v3(self, db, current_user=None):

        project_id = self.project_id
        superficie_dict = {}
        input_data = InputDataCalculator(
            project_id=project_id,
            db=db
        )
        result = {}
        logger.info("Starting calculations n 2 for project {}".format(project_id))
        df_list = []
        df_list_base = []
        for enclosure in input_data.enclosures:
            superficie_dict[enclosure.id] = self.get_enclosure_area_from_cache(enclosure.id)
            df_r = self.get_demand_cache(project_id, enclosure.id)
            if isinstance(df_r, pd.DataFrame):
                df_r = df_r.copy()
                df_r['ID_Recinto'] = enclosure.id
                if enclosure.is_base:
                    df_list_base.append(df_r)
                else:
                    df_list.append(df_r)
            else:
                try:
                    df_r = pd.DataFrame(df_r)
                    df_r['ID_Recinto'] = enclosure.id
                    if enclosure.is_base:
                        df_list_base.append(df_r)
                    else:
                        df_list.append(df_r)
                except Exception:
                    logger.warning(f"No se pudo convertir DF de recinto {enclosure.id}")

        if not df_list:
            logger.warning("No hay DF de recintos propuestos en cache.")
            return {"final_indicators": {}, "result_by_enclosure": []}
        df_resultado_all = pd.concat(df_list, ignore_index=True)

        coef_consumo = HeatingConfigService.get_consumo_heating_config_constant(project_id, db)
        SER = 2.95
        coef_combustible = HeatingConfigService.get_combustible_heating_config_constant(project_id, db)
        SCOP = 1.0
        try:
            # Calcular resultados para recintos propuestos
            result_by_enclosure_v2 = self.calculate_result_by_enclosure_v2(
                df_resultado_all, input_data.monthly_processed_data_df, superficie_dict, SCOP=SCOP,
                coef_consumo=coef_consumo,
                coef_combustible=coef_combustible,
                SER=SER, db=db)

            # [MOD] Filtrar por is_base flag (base real vs propuesto)
            if isinstance(result_by_enclosure_v2, str):
                result_by_enclosure_v2 = json.loads(result_by_enclosure_v2)

            # Solo debe haber propuestos aquí, pero filtramos por seguridad
            proposed_list = [r for r in result_by_enclosure_v2 if not r.get("is_base", False)]

            # Procesar recintos base si existen
            base_list = []
            if df_list_base:
                df_base_all = pd.concat(df_list_base, ignore_index=True)
                result_by_enclosure_base = self.calculate_result_by_enclosure_v2(
                    df_base_all, input_data.monthly_processed_data_df, superficie_dict, SCOP=SCOP,
                    coef_consumo=coef_consumo,
                    coef_combustible=coef_combustible,
                    SER=SER, db=db)

                if isinstance(result_by_enclosure_base, str):
                    result_by_enclosure_base = json.loads(result_by_enclosure_base)

                base_list = [r for r in result_by_enclosure_base if r.get("is_base", False)]

            co2_eq_energia_primaria = self.get_co2_eq_energia_primaria(
                project_id, db=db)
            demanda_acs = self.get_demand_acs(project_id, db=db)

            # [MOD] Pasar propuestos como "result_by_enclosure_v2" y base_list como "base_by_enclosure"
            final_indicators = self.calculate_final_indicators(
                proposed_list, base_list if base_list else None, co2_eq_energia_primaria, demanda_acs)

            # [MOD] DEVOLVEMOS TODOS LOS RECINTOS (propuestos + base) para que se guarden en DB
            all_enclosures = proposed_list + base_list

            result["final_indicators"] = final_indicators
            result["result_by_enclosure"] = all_enclosures  # [MOD] principal: TODOS los recintos, con is_base flag
            result["base_by_enclosure"] = base_list  # [MOD] adjunto: base real (por si lo quieres directo)
            result["co2_eq_energia_primaria"] = co2_eq_energia_primaria
        except Exception as e:
            import traceback
            print(traceback.format_exc())
        if current_user:
            try:
                co2_eq = {"total": co2_eq_energia_primaria}
                calculation_result = upsert_calculation_result(
                    project_id=project_id,
                    final_indicators=final_indicators,
                    result_by_enclosure=all_enclosures,  # [MOD] guardamos TODOS (así se persiste el caso base)
                    co2_eq=co2_eq,
                    current_user=current_user,
                    db=db
                )
                logger.info(f"Calculation result saved with ID {calculation_result.get('id')}")
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"Error saving calculation result: {str(e)}")
            # self.clear_cache()
            return result

    def clear_cache(self):
        try:
            cache = get_redis_sync()
            pattern = f'project:{self.project_id}:*'
            keys = cache.keys(pattern)
            for key in keys:
                cache.delete(key)
            logger.info(f"Cache de Redis del proyecto {self.project_id} eliminado tras el cálculo.")
        except Exception as e:
            logger.warning(f"No se pudo limpiar el caché de Redis: {e}")




    def clear_project_processment_folder(self, project_id):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        folder_path = os.path.join(project_root, 'public', 'uploads', str(project_id))
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def get_enclosure_area_from_cache(self, enclosure_id):
        cache = get_redis_sync()
        area = cache.get(f'enclosure:{enclosure_id}:area')
        if area is not None:
            return float(area)
        return None

    def get_enclosure_altura_from_cache(self, enclosure_id):
        cache = get_redis_sync()
        altura = cache.get(f'enclosure:{enclosure_id}:altura')
        if altura is not None:
            return float(altura)
        return None

    def calculate_result_by_enclosure_v2(self, df, monthly_processed, surface,
                                         db=None, SCOP=1.0, coef_combustible=1.9, SER=2.95, coef_consumo=0.31):
        """
        Calculate result_by_enclosure_v2 with specific demand calculations:
        - Demanda calefaccion: Sum of positive values from demanda_total
        - Demanda refrigeracion: Sum of negative values from demanda_total (for cooling)
        - Demanda iluminacion: Sum of negative values from demanda_total (absolute value, for lighting)
        - Demanda total: Sum of all demands
        - coef_consumo: Es factores de emisiones 0.31 es electricidad
        """

        # SCOP = 1.0  # Seasonal Coefficient of Performance for heating and cooling | Control
        # coef_combustible = 1.9  # Coefficient for fuel consumption | Elect
        # SER = 2.95  # Seasonal Energy Ratio for cooling | Elect
        # coef_consumo = 0.31  # Coefficient for energy consumption | Elect

        print("df by enclosure: {}".format(df))
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            print("Warning: DataFrame is empty or None")
            return []

        # Convert df to DataFrame if it's not already
        if not isinstance(df, pd.DataFrame):
            try:
                df = pd.DataFrame(df)
            except Exception as e:
                print(f"Error converting df to DataFrame: {str(e)}")
                return []

        # Convert surface to dict if it's not already
        if not isinstance(surface, dict):
            try:
                if isinstance(surface, (int, float)):
                    # If surface is a single value, create a dict with recinto IDs as keys
                    surface_dict = {}
                    for recinto_id in df['ID_Recinto'].unique():
                        surface_dict[int(float(recinto_id))] = float(surface)
                    surface = surface_dict
                else:
                    print(
                        f"Warning: surface type {type(surface)} not handled, using empty dict")
                    surface = {}
            except Exception as e:
                print(f"Error handling surface: {str(e)}")
                surface = {}

        result = []

        # Convert monthly_processed to DataFrame if it's not already
        if not isinstance(monthly_processed, pd.DataFrame):
            monthly_data = pd.DataFrame(monthly_processed)
        else:
            if isinstance(monthly_processed, pd.DataFrame):
                monthly_data = monthly_processed
            elif isinstance(monthly_processed, list):
                monthly_data = pd.DataFrame(monthly_processed)
                try:
                    if isinstance(monthly_processed, str):
                        if monthly_processed.strip().startswith('{') and '\n' in monthly_processed:
                            # Process multi-line JSON format
                            json_lines = [json.loads(
                                line.strip()) for line in monthly_processed.strip().split('\n') if line.strip()]
                            monthly_data = pd.DataFrame(json_lines)
                        else:
                            monthly_data = pd.DataFrame(
                                json.loads(monthly_processed))
                    else:
                        monthly_data = pd.DataFrame(monthly_processed)
                except Exception as e:
                    print(f"Error processing monthly data: {str(e)}")
                    monthly_data = pd.DataFrame()  # Empty DataFrame as fallback

        if not monthly_data.empty and 'month' in monthly_data.columns:
            # Ensure data types are numeric for merge
            monthly_data[['month', 'tn_min', 'tn_max']] = monthly_data[['month', 'tn_min', 'tn_max']].apply(
                pd.to_numeric)

        current_year = datetime.now().year

        # Create a dictionary for days in each month
        days_in_month = {}
        for month in range(1, 13):
            days_in_month[month] = calendar.monthrange(current_year, month)[1]

        for recinto_id, df_group in df.groupby('ID_Recinto'):
            recinto_id = int(float(recinto_id))

            recinto = db.query(EnclosureGenerals).filter(
                EnclosureGenerals.id == recinto_id,
                EnclosureGenerals.is_deleted == False
            ).first()

            is_base = recinto.is_base

            superficie = surface.get(recinto_id, None)
            if 'demanda_total' not in df_group.columns:
                if all(col in df_group.columns for col in ['Demanda', 'G_HU', 'G_DHU']):
                    df_group['demanda_total'] = (df_group['Demanda'] + df_group['G_HU'] + df_group['G_DHU']) / 1000
                else:
                    df_group['demanda_total'] = df_group['Demanda'] / 1000
            numeric_columns = ['Temperatura_operativa_free_float', 'demanda_total', 'Mes', 'Temperatura_exterior',
                               'Demanda', 'G_HU', 'G_DHU']
            for col in numeric_columns:
                if col in df_group.columns:
                    df_group[col] = pd.to_numeric(df_group[col], errors='coerce')

            df_group = df_group.fillna(0)

            if not monthly_data.empty and 'month' in monthly_data.columns:
                df_group = df_group.merge(
                    monthly_data[['month', 'tn_min', 'tn_max']],
                    left_on='Mes',
                    right_on='month',
                    how='left'
                )
                if 'month' in df_group.columns:
                    df_group.drop(columns=['month'], inplace=True)

                disconfort_calef, disconfort_ref = self.calcular_disconfort_termico(df_group, monthly_data)
                df_group['hd_min'] = disconfort_calef
                df_group['hd_max'] = disconfort_ref
            else:
                df_group['hd_min'] = 0
                df_group['hd_max'] = 0

            demanda_total_col = df_group['Demanda']
            demanda_calefaccion_raw = demanda_total_col[demanda_total_col > 0].sum() / 1000
            demanda_refrigeracion_raw = -demanda_total_col[demanda_total_col < 0].sum() / 1000
            # Debug: verificar cálculos
            print(f"[DEBUG] Recinto {recinto_id}:")
            print(f"  - Total registros: {len(demanda_total_col)}")
            print(f"  - Valores positivos (refrig): {(demanda_total_col > 0).sum()}")
            print(f"  - Valores negativos (calef): {(demanda_total_col < 0).sum()}")
            print(f"  - Demanda refrigeración raw: {demanda_refrigeracion_raw:.2f} kWh")
            print(f"  - Demanda calefacción raw: {demanda_calefaccion_raw:.2f} kWh")

            try:
                superficie = float(superficie) if superficie is not None else 0
                demanda_calefaccion_raw = float(demanda_calefaccion_raw)
                demanda_refrigeracion_raw = float(demanda_refrigeracion_raw)

                demanda_calefaccion = demanda_calefaccion_raw / \
                                      superficie if superficie and superficie > 0 else 0
                demanda_refrigeracion = demanda_refrigeracion_raw / \
                                        superficie if superficie and superficie > 0 else 0
                demanda_iluminacion = self.calcular_demanda_energia_anual(
                    kw_m2_dia_verano=0.12,
                    kw_m2_dia_invierno=0.12,
                    meses_verano=6,
                    meses_invierno=6,
                    dias_semana=7
                )

                print(f"  - Superficie: {superficie} m²")
                print(f"  - Demanda calefacción: {demanda_calefaccion:.2f} kWh/m²·año")
                print(f"  - Demanda refrigeración: {demanda_refrigeracion:.2f} kWh/m²·año")
                print(f"  - Demanda iluminación: {demanda_iluminacion:.2f} kWh/m²·año")

                print("Demanda calefaccion raw: {}".format(demanda_calefaccion_raw))
                print("Demanda refrigeracion raw: {}".format(demanda_refrigeracion_raw))
                print("Demanda iluminacion raw: {}".format(demanda_iluminacion))
                demanda_total = demanda_calefaccion + demanda_refrigeracion + demanda_iluminacion
            except (TypeError, ValueError) as e:
                print(f"Error calculating demand values: {e}")
                demanda_calefaccion = 0
                demanda_calefaccion_raw = 0
                demanda_refrigeracion = 0
                demanda_refrigeracion_raw = 0
                demanda_iluminacion = 0
                demanda_total = 0

            enclosure_info = get_enclosure_by_id(recinto_id, db=db)
            nombre = enclosure_info.get("name", "Desconocido")
            perfil_uso = enclosure_info.get(
                "occupation_profile_name", "Desconocido")

            consumo_calefaccion = round(
                demanda_calefaccion / SCOP, 3) * coef_combustible
            consumo_refrigeracion = round(
                demanda_refrigeracion / SER, 3) * coef_combustible
            consumo_total = consumo_calefaccion + consumo_refrigeracion
            co2_eq_calefaccion = round(
                consumo_calefaccion * coef_consumo * superficie, 3)
            co2_eq_refrigeracion = round(
                consumo_refrigeracion * coef_consumo * superficie, 3)
            co2_eq_iluminacion = round(
                demanda_iluminacion * superficie * coef_consumo * coef_combustible, 3)
            coe2_eq_total = round(co2_eq_calefaccion +
                                  co2_eq_refrigeracion + co2_eq_iluminacion, 3)

            # [CORREGIDO] No calcular valores sintéticos del caso base aquí
            # Los valores del caso base deben venir de recintos con is_base=True
            # Si este recinto no es base, estos valores no se usan en calculate_final_indicators
            # Solo se mantienen para compatibilidad con código existente pero NO se usan para comparación
            hd_min_sum = float(df_group['hd_min'].sum())
            hd_max_sum = float(df_group['hd_max'].sum())

            # Valores placeholder (no se usarán en la comparación real)
            caso_base_demanda_calefaccion = 0
            caso_base_demanda_calefaccion_raw = 0
            caso_base_demanda_refrigeracion = 0
            caso_base_demanda_refrigeracion_raw = 0
            caso_base_demanda_iluminacion = 0
            caso_base_demanda_total = 0
            caso_base_consumo_calefaccion = 0
            caso_base_consumo_refrigeracion = 0
            caso_base_consumo_total = 0
            caso_base_co2_eq_calefaccion = 0
            caso_base_co2_eq_refrigeracion = 0
            caso_base_co2_eq_iluminacion = 0
            caso_base_co2_eq_total = 0
            caso_base_hrs_disconfort_calefaccion = 0
            caso_base_hrs_disconfort_refrigeracion = 0
            caso_base_hrs_disconfort_total = 0

            result_dict = {
                "enclosure_id": recinto_id,
                "nombre_recinto": nombre,
                "perfil_uso": perfil_uso,
                "superficie": superficie,
                "demanda_calefaccion": round(demanda_calefaccion, 3),
                "demanda_refrigeracion": round(demanda_refrigeracion, 3),
                "demanda_iluminacion": round(demanda_iluminacion, 3),
                "demanda_total": round(demanda_total, 3),
                # Valores absolutos (raw) en kWh para sumar correctamente
                "demanda_calefaccion_raw": round(demanda_calefaccion_raw, 3),
                "demanda_refrigeracion_raw": round(demanda_refrigeracion_raw, 3),
                "consumo_calefaccion": consumo_calefaccion,
                "consumo_refrigeracion": consumo_refrigeracion,
                "consumo_total": consumo_total,
                "co2_eq_calefaccion": round(
                    consumo_calefaccion * coef_consumo * superficie, 3),
                "co2_eq_refrigeracion": round(
                    consumo_refrigeracion * coef_consumo * superficie, 3),
                "co2_eq_iluminacion": round(
                    demanda_iluminacion * superficie * coef_consumo * coef_combustible, 3),
                "co2_eq_total": coe2_eq_total,
                "hrs_disconfort_calefaccion": df_group['hd_min'].sum(),
                "hrs_disconfort_refrigeracion": df_group['hd_max'].sum(),
                "hrs_disconfort_total": df_group['hd_min'].sum() + df_group['hd_max'].sum(),
                # Base case values for heating demand
                "caso_base_demanda_calefaccion": caso_base_demanda_calefaccion,
                "caso_base_demanda_calefaccion_raw": round(caso_base_demanda_calefaccion_raw, 3),
                # Base case values for cooling demand
                "caso_base_demanda_refrigeracion": caso_base_demanda_refrigeracion,
                "caso_base_demanda_refrigeracion_raw": round(caso_base_demanda_refrigeracion_raw, 3),
                # Base case values for lighting demand
                "caso_base_demanda_iluminacion": caso_base_demanda_iluminacion,
                # Total base case demand
                "caso_base_demanda_total": round(caso_base_demanda_total, 3),
                # Base case heating consumption
                "caso_base_consumo_calefaccion": caso_base_consumo_calefaccion,
                # Base case cooling consumption
                "caso_base_consumo_refrigeracion": caso_base_consumo_refrigeracion,
                "caso_base_consumo_total": caso_base_consumo_total,  # Total base case consumption
                # Base case heating CO2 emissions
                "caso_base_co2_eq_calefaccion": caso_base_co2_eq_calefaccion,
                # Base case cooling CO2 emissions
                "caso_base_co2_eq_refrigeracion": caso_base_co2_eq_refrigeracion,
                # Base case lighting CO2 emissions
                "caso_base_co2_eq_iluminacion": caso_base_co2_eq_iluminacion,
                "caso_base_co2_eq_total": caso_base_co2_eq_total,  # Total base case CO2 emissions
                # Base case heating discomfort hours
                "caso_base_hrs_disconfort_calefaccion": caso_base_hrs_disconfort_calefaccion,
                # Base case cooling discomfort hours
                "caso_base_hrs_disconfort_refrigeracion": caso_base_hrs_disconfort_refrigeracion,
                # Total base case discomfort hours
                "caso_base_hrs_disconfort_total": caso_base_hrs_disconfort_total,
                "is_base": is_base
            }

            result.append(result_dict)

        print(f"Result Enclosures V2 Final DF {df_group}")
        df_result = pd.DataFrame(result)
        json_result = df_result.to_json(orient='records')
        return json_result

    def calcular_demanda_energia_anual(
            self,
            kw_m2_dia_verano: float,  # Valor base de demanda en kWh/m²/día para verano
            kw_m2_dia_invierno: float,  # Valor base de demanda en kWh/m²/día para invierno
            # Número de meses en verano (por ejemplo, 6)
            meses_verano: int = 6,
            # Número de meses en invierno (por ejemplo, 6)
            meses_invierno: int = 6,
            dias_semana: int = 5  # Días de uso por semana (por ejemplo, 5)
    ) -> float:
        factor_uso = dias_semana / 7
        energia_verano = kw_m2_dia_verano * \
                         365 * (meses_verano / 12) * factor_uso
        energia_invierno = kw_m2_dia_invierno * \
                           365 * (meses_invierno / 12) * factor_uso
        demanda_total = energia_verano + energia_invierno
        return round(demanda_total, 2)

    def calculate_surface_by_enclosure(self, df, surface, column_name, is_base=False, project_id=None,
                                       current_user=None, db=None):
        if df is None or df.empty:
            return []

        print(
            f"Calculating surface by enclosure for project {project_id}, is_base={is_base} df: {df['ID_Recinto']}")
        result = []
        for recinto_id, group in df.groupby('ID_Recinto'):
            # Adjust logic for base case to ensure unique calculations
            recinto_id = int(recinto_id)
            recinto = db.query(EnclosureGenerals).filter(
                EnclosureGenerals.id == recinto_id,
                EnclosureGenerals.is_deleted == False,
            ).first()
            is_base = recinto.is_base
            if is_base:
                print("ES CASO BASE")
                positive_sum = round(group[column_name][(group[column_name] > 0) & (
                    group[column_name].between(100, 50000))].sum() / 100, 5)
                negative_sum = round(
                    abs(group[column_name].sum()) / 200, 3)
            else:
                positive_sum = group[column_name][group[column_name] > 0].sum(
                )
                negative_sum = abs(
                    group[column_name][group[column_name] < 0].sum())
            superficie = surface.get(recinto_id, None)
            # Obtener el nombre y perfil de uso del recinto
            print(
                f"Obteniendo información del recinto {recinto_id} para el proyecto {project_id}")
            nombre = ""
            perfil_uso = ""
            if not is_base:
                print("RECINTO NO BASE: ", recinto_id)
                enclosure_info = get_enclosure_by_id(recinto_id, db=db)
                nombre = enclosure_info.get("name", "Desconocido")
                perfil_uso = enclosure_info.get(
                    "occupation_profile_name", "Desconocido")

            # Add a flag or additional logic for base case if needed
            if is_base:
                nombre += " (Base)"
            result.append({
                "enclosure_id": recinto_id,
                "enclosure_name": nombre,
                "occupation_profile_name": perfil_uso,
                "surface": superficie,
                "positive_sum": positive_sum,
                "negative_sum": negative_sum
            })
        print(f"Result Enclosures Final {result}")
        # Convert result list to DataFrame
        df_result = pd.DataFrame(result)

        # Convert DataFrame to JSON
        json_result = df_result.to_json(orient='records')

        return json_result

    def calculate_sums(self, df, column_name):
        if df is None or df.empty:
            return None, None

        # Filtrar, dividir entre 10,000 y sumar valores positivos de 4 dígitos por recinto
        positive_sums = df.groupby('ID_Recinto')[column_name].apply(
            lambda x: round(
                x[(x > 0) & (x.between(200, 99999))].sum() / 50, 5)
        ).to_dict()
        negative_sum = round(abs(df[column_name].sum()) / 100, 3)

        return positive_sums, negative_sum

    def calculate_demand(self, df):
        print(f"Calculando demanda...{df}")
        if "G_DHU" not in df.columns and "G_HU" in df.columns:
            df["G_DHU"] = df["G_HU"]

        # Convertir las columnas relevantes a numéricas y redondear los meses
        try:
            df.loc[:, 'ID_Recinto'] = pd.to_numeric(
                df['ID_Recinto'], errors='coerce').fillna(0).astype(int)
            df.loc[:, 'Hora'] = pd.to_numeric(
                df['Hora'], errors='coerce').fillna(0).astype(int)
            df.loc[:, 'Mes'] = pd.to_numeric(
                df['Mes'], errors='coerce').fillna(0).astype(float)
            df.loc[:, 'Mes'] = df['Mes'].round(0).astype(
                int)  # Redondear y convertir a entero
            # Filtrar valores fuera del rango 1-12
            df = df[df['Mes'].between(1, 12)]

            for col in ['Demanda', 'G_HU', 'G_DHU']:
                df.loc[:, col] = pd.to_numeric(
                    df[col], errors='coerce').fillna(0)
        except Exception as e:
            raise ValueError(f"Error al procesar las columnas: {e}")

        # Año actual para calcular los días del mes
        year = datetime.now().year

        # Días por mes
        dias_mes = {m: calendar.monthrange(
            year, m)[1] for m in df['Mes'].unique()}

        # Calcula la demanda total
        try:
            # [CORREGIDO] Calcular demanda_total SIN multiplicar por días del mes
            # Los valores ya son horarios (Wh), no promedios diarios
            df['demanda_total'] = df.apply(
                lambda row: (
                    (row['Demanda'] or 0) +
                    (row['G_HU'] or 0) +
                    (row['G_DHU'] or 0)
                ),
                axis=1
            )
        except Exception as e:
            raise ValueError(f"Error al calcular la demanda total: {e}")

        # Conversión de int a str (si es necesario)
        try:
            df['Mes'] = pd.to_numeric(
                df['Mes'], errors='coerce').astype('Int64').astype(str)
        except Exception as e:
            raise ValueError(f"Error al convertir 'Mes' a str: {e}")

        return df

    def clear(self):
        '''Elimina solo el contenido de la carpeta del proyecto si existe'''
        project_folder = os.path.join(public_folder, str(self.project_id))
        if os.path.exists(project_folder):
            for filename in os.listdir(project_folder):
                file_path = os.path.join(project_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'No se pudo eliminar {file_path}. Razón: {e}')

    def prepare(self):
        """
                Crea la carpeta del proyecto en la ruta public_folder si no existe.
                """
        project_folder = os.path.join(public_folder, str(self.project_id))
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)

    def calcular_disconfort_termico(self, df, monthly_data):
        """
        Calcula las horas de disconfort térmico para calefacción y refrigeración sobre las primeras 8760 filas del DataFrame,
        usando tn_min y tn_max de monthly_data según el mes correspondiente.
        Devuelve dos Series: disconfort_calef y disconfort_ref.
        """
        # Tomar solo las primeras 8760 filas (primer año)
        df = df.head(8760).copy()
        # Asegurar tipo numérico
        df['Temperatura_operativa_free_float'] = pd.to_numeric(df['Temperatura_operativa_free_float'], errors='coerce')
        df['Mes'] = pd.to_numeric(df['Mes'], errors='coerce').astype(int)
        # Merge con monthly_data para obtener tn_min y tn_max por mes
        monthly_data = monthly_data.copy()
        monthly_data['month'] = pd.to_numeric(monthly_data['month'], errors='coerce').astype(int)
        df = df.merge(monthly_data[['month', 'tn_min', 'tn_max']], left_on='Mes', right_on='month', how='left', suffixes=(None, '_monthly'))
        # Si existen tn_min_y y tn_max_y, usarlas y renombrar
        if 'tn_min_y' in df.columns and 'tn_max_y' in df.columns:
            df['tn_min'] = df['tn_min_y']
            df['tn_max'] = df['tn_max_y']
        elif 'tn_min' not in df.columns or 'tn_max' not in df.columns:
            print("[ERROR] tn_min o tn_max no existen después del merge. Columnas disponibles:", df.columns.tolist())
            print("Primeras filas del DataFrame tras el merge:")
            print(df.head())
            raise ValueError("No se encontraron las columnas tn_min y/o tn_max tras el merge. Verifica monthly_data y los valores de Mes/mes.")
        # Calefacción: temperatura operativa menor al tn_min del mes
        disconfort_calef = (df['Temperatura_operativa_free_float'] < df['tn_min']).astype(int)
        # Refrigeración: temperatura operativa mayor al tn_max del mes
        disconfort_ref = (df['Temperatura_operativa_free_float'] > df['tn_max']).astype(int)
        return disconfort_calef, disconfort_ref
