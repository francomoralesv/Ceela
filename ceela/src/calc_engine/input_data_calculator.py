import logging
import os

from fastapi import HTTPException

from src.services.calculator.weather.weather_service import get_weather_data_from_coord_one
from src.services.datos.materials import get_enclosures_by_project
from src.services.project.project_service import get_project_by_id_only
from src.services.sol.promedio import read_parquet_and_export_radiations
from src.services.sol.sol import calcular_parametros_solares_parquet
from src.services.sol.sol_elements import convert_parquet_window_project
from src.services.sol.sol_obstruction import convert_parquet_obstruction_project
from src.services.sol.sol_recinto import calcular_parametros_solares_recinto_parquet
from src.utils.processor import read_parquet_file

logger = logging.getLogger(__name__)


class InputDataCalculator:
    def __init__(self, project_id=None, db=None):
        self.sol_file_parquet = None
        self.project_id = project_id
        self.db = db
        self.project = get_project_by_id_only(self.project_id, self.db)

        if self.project.project_metadata is None:
            raise HTTPException(
                status_code=400, detail="No se ha seleccionado una zona correctamente.")
        zone = self.project.project_metadata.get("zone")
        weather_metadata = get_weather_data_from_coord_one(
            db, self.project.latitude, self.project.longitude, zone)
        weather_path = weather_metadata.location
        print("☁️ weather_path: ", weather_path)
        self.weather_processed_df = read_parquet_file(weather_path)
        self.monthly_processed_data_df = read_parquet_file(weather_metadata.complementary)
        try:
            read_parquet_and_export_radiations(weather_path)
            calcular_parametros_solares_parquet(weather_path, db, project_id)
            calcular_parametros_solares_recinto_parquet(db, project_id)
            convert_parquet_obstruction_project(db, project_id)
            convert_parquet_window_project(db, project_id)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise Exception('Error fatal al calcular los parametros solares')
        self.enclosures = get_enclosures_by_project(
            project_id, db=db)

    def get_sol_parquet_file(self, enclosure_id):
        route_sol = f"public/sol_recinto/{self.project_id}/"
        self.sol_file_parquet = os.path.join(route_sol, f"{enclosure_id}_sol_recinto.parquet")
        if not os.path.exists(self.sol_file_parquet):
            raise HTTPException(
                status_code=404, detail=f"Archivo SOL parquet {self.sol_file_parquet} no encontrado.")
        return self.sol_file_parquet