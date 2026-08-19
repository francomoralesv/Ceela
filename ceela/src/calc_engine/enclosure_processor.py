import calendar
import logging
import os
import pickle
import traceback
from datetime import datetime

import pandas as pd
from fastapi import HTTPException

from src.calc_engine.input_data_calculator import InputDataCalculator
from src.calc_engine.original.ejecutable_iso import ejecutable_iso
from src.calc_engine.ztu import ZtuBuilder
from src.services.calculator.python.process_python_input import PyProcessInput
from src.services.calculator.utils import convert_walls_to_df
from src.services.datos.materials import get_material_details, get_nodos_area_by_orientation, \
    get_translucent_window_area_by_enclosure
from src.services.datos.recintos import get_info_recinto
from src.services.datos.suma_puentes import get_htr_wk_by_project
from src.services.datos.suma_puentes import get_htr_wk_by_enclosure_id
from src.services.project.project_service import update_project
from src.services.sol.sol_recinto import calcular_parametros_solares_recinto_parquet
from src.utils.constants import public_folder
from src.utils.processor import txt_to_df
from src.utils.redis_utils import get_redis_sync

logger = logging.getLogger(__name__)

class EnclosureProcessor:
    def __init__(self, data: InputDataCalculator, db=None):
        self.db = db
        self.data = data
        self.output_processed_files={}
        self.demand_results = {}   # in-memory: {enclosure_id: df_demand}
        self.area_results = {}     # in-memory: {enclosure_id: area}

    def __calculate_demand(self, df: pd.DataFrame) -> pd.DataFrame:
        if "G_DHU" not in df.columns and "G_HU" in df.columns:
            df["G_DHU"] = df["G_HU"]
        try:
            df.loc[:, 'ID_Recinto'] = pd.to_numeric(
                df['ID_Recinto'], errors='coerce').fillna(0).astype(int)
            df.loc[:, 'Hora'] = pd.to_numeric(
                df['Hora'], errors='coerce').fillna(0).astype(int)
            df.loc[:, 'Mes'] = pd.to_numeric(
                df['Mes'], errors='coerce').fillna(0).astype(float)
            df.loc[:, 'Mes'] = df['Mes'].round(0).astype(
                int)
            df = df[df['Mes'].between(1, 12)]
            for col in ['Demanda', 'G_HU', 'G_DHU']:
                df.loc[:, col] = pd.to_numeric(
                    df[col], errors='coerce').fillna(0)
        except Exception as e:
            raise ValueError(f"Error al procesar las columnas: {e}")
        year = datetime.now().year
        dias_mes = {m: calendar.monthrange(
            year, m)[1] for m in df['Mes'].unique()}
        try:
            # [CORREGIDO] Calcular demanda_total SIN multiplicar por días del mes
            # Los valores ya son horarios (Wh), no promedios diarios
            # La división por 1000 se hace después en result_calculator.py
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
        df['Mes'] = pd.to_numeric(
            df['Mes'], errors='coerce').astype('Int64').astype(str)
        return df

    async def process_enclosures(self, force_data=None):
        logger.info("Force data is: {}".format(force_data))
        for enclosure in self.data.enclosures:
            try:
                calcular_parametros_solares_recinto_parquet(
                    self.data.db, self.data.project_id)
                walls_for_py = get_material_details(
                    enclosure.id, db=self.db)
                areas_for_py = get_nodos_area_by_orientation(
                    enclosure.id, db=self.db)
                self.data.get_sol_parquet_file(enclosure.id)
                window_total_for_areas_py = get_translucent_window_area_by_enclosure(enclosure.id,
                                                                                     db=self.db)
                enclosure_info = get_info_recinto(self.data.project_id, db=self.db,
                                                  enclosure_id=enclosure.id)
                enclosure_info = enclosure_info[0]
                area_recinto = float(enclosure_info.get("area"))
                altura = float(enclosure_info.get("altura"))
                self.cache_enclosure_area_altura(enclosure.id, area_recinto, altura)
                areas_for_py = pd.DataFrame(areas_for_py).drop(columns=["Absorcion", "item_id", "type"],
                                                               errors="ignore")
                if force_data is False:
                    py_process_input = PyProcessInput(
                        self.data.project, enclosure.id, self.data.weather_processed_df,
                        self.data.monthly_processed_data_df,
                        walls_for_py=convert_walls_to_df(walls_for_py),
                        areas_for_py=areas_for_py,
                        window_total_for_areas_py=window_total_for_areas_py,
                        sol_file=self.data.get_sol_parquet_file(enclosure.id),
                        thermal_bridges_sum=get_htr_wk_by_enclosure_id(
                            enclosure.id, self.db) + 0.001,
                        area=area_recinto, altura=altura, db=self.db)
                    py_process_input.prepare()
                    clima_df=py_process_input.clima_df
                    if clima_df is None:
                        raise ValueError("clima_df is None")
                    ztu = ZtuBuilder(project_id=self.data.project_id, db=self.db, enclosures=self.data.enclosures, current_user=None,clima_df=clima_df)
                    ztu.build()
                    ztu_df=ztu.get_result_by_enclosure(enclosure.id)
                    py_process_input.run(ztu_df)
                    output_py_process_file = py_process_input.save() # public/uploads/10/500.data.xlsx
                else:
                    output_py_process_file=self.get_output_file_data(enclosure.id)
                logger.info(f"output_py_process_file {output_py_process_file}")
                self.output_processed_files[enclosure.id]=output_py_process_file
                #Ejecutar ztu builder
            except Exception as e:
                logger.error(f"Error processing enclosure {enclosure.id}: {str(e)}")

    def post_process_enclosures(self):
        logger.info("post_process_enclosures")
        processed_enclosures = []
        for enclosure in self.data.enclosures:
                try:
                    #Ejecutar ztu builder
                    output_file =self.get_output_file_data(enclosure.id)
                    logger.info(f"🤷‍♂️ output_file {output_file}")
                    ejecutable_iso(self.data.project.id,
                                   output_file,
                                   self.get_output_folder_path(self.data.project_id))
                    self.data.project.are_files_processed = True
                    update_project(self.data.project_id, self.data.project, db=self.db)
                    result_df,txt_path = self.process_output_simple(self.data.project_id)
                    df_demand = self.process_demand(result_df,txt_path)
                    logger.info(f"🚀Processed enclosure  [df_demand] [{df_demand}]")
                    self.demand_results[enclosure.id] = df_demand  # in-memory
                    self.put_demand_cache(enclosure.id, df_demand)
                    processed_enclosures.append(True)
                except Exception as e:
                    traceback.print_exc()
                    logger.error(f"Error processing enclosure {enclosure.id}: {str(e)}")
                    processed_enclosures.append(False)
    def get_weather_processed_data(self, enclosure_id):
        cache = get_redis_sync()
        return pickle.loads(cache.get(f"project:climate_results:{enclosure_id}"))
    def save_cache(self,key,value):
        cache = get_redis_sync()
        cache.set(key, value)
    def cache_enclosure_area_altura(self, enclosure_id, area, altura):
        self.area_results[enclosure_id] = area  # in-memory
        cache = get_redis_sync()
        cache.set(f'enclosure:{enclosure_id}:area', area)
        cache.set(f'enclosure:{enclosure_id}:altura', altura)
    def put_demand_cache(self, enclosure_id, data):
        cache = get_redis_sync()
        cache.set(f'project:{self.data.project_id}:{enclosure_id}:df_demand_pickle', pickle.dumps(data))

    def get_demand_cache(self, enclosure_id):
        cache = get_redis_sync()
        data = cache.get(f'project:{self.data.project_id}:{enclosure_id}:df_demand_pickle')
        if data:
            return pickle.loads(data)
        else:
            raise HTTPException(status_code=404, detail="Cache not found for demand data")
    def get_output_file_data(self, enclosure_id):
        folder = os.path.join(public_folder, str(self.data.project_id), f"{enclosure_id}.data.xlsx")
        logger.info("get_output_file_data {}".format(folder))
        return folder
    def get_output_folder_path(self, project_id):
        return os.path.join(public_folder, str(project_id))

    def process_output_simple_avg(self, project_id: str) -> pd.DataFrame:
        txt_path = os.path.join("public", "uploads", str(
            project_id), f"{project_id}.output_simple_promedios.txt")
        df = txt_to_df(txt_path)
        return df,txt_path

    def process_output_simple(self, project_id: str) -> pd.DataFrame:
        txt_path = os.path.join("public", "uploads", str(
            project_id), f"{project_id}.output_simple.txt")
        df = txt_to_df(txt_path)
        return df,txt_path

    def process_demand(self, df_output_simple_avg, txt_path):
        df_resultado = self.__calculate_demand(df_output_simple_avg)
        df_resultado.to_csv(txt_path.replace('.txt', '_demanda.csv'), index=False)
        return df_resultado

