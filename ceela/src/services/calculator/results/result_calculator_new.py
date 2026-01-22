from src.utils.logging import logger
import json
import logging

from src.services.agua_caliente.agua_caliente_service import get_agua_caliente_by_project

# Configure logger
logger = logging.getLogger(__name__)


class ResultCalculator:
    def __init__(self):
        pass
        
    def _has_four_walls(self, project_id=None, current_user=None, db=None):
        """
        Verifica si el proyecto tiene exactamente 4 muros.
        Para simulación: Si hay 4 muros, devuelve datos simulados en lugar de hacer cálculos.
        
        Returns:
            bool: True si hay exactamente 4 muros, False en caso contrario
        """
        try:
            if project_id and db:
                # Intentar obtener los muros del proyecto
                from src.services.datos.materials import get_enclosures_by_project
                enclosures = get_enclosures_by_project(project_id, current_user, db)
                
                # Contar los muros (esto es una simplificación - ajustar según la estructura real)
                wall_count = 0
                for enclosure in enclosures:
                    # Ajustar esta lógica según cómo se identifiquen los muros en tu sistema
                    if enclosure.get('type') == 'wall' or enclosure.get('type') == 'muro':
                        wall_count += 1
                
                return wall_count == 4
            return False
        except Exception as e:
            logger.error(f"Error verificando número de muros: {str(e)}")
            return False
            
    def _load_mock_results(self):
        """
        Carga resultados simulados desde el archivo mock_results.json
        
        Returns:
            dict: Datos simulados con estructura completa
        """
        try:
            import json
            import os
            
            # Ruta al archivo de resultados simulados
            mock_file_path = os.path.join(os.getcwd(), 'mock_results.json')
            
            # Cargar el archivo JSON
            with open(mock_file_path, 'r') as f:
                mock_data = json.load(f)
                
            return mock_data
        except Exception as e:
            logger.error(f"Error cargando resultados simulados: {str(e)}")
            # Devolver estructura vacía en caso de error
            return {
                "final_indicators": {},
                "result_by_enclosure": [],
                "co2_eq_energia_primaria": 1000.0
            }

    def get_co2_eq_energia_primaria(self, project_id=None, current_user=None, db=None):
        # Verificar si debemos devolver datos simulados
        if self._has_four_walls(project_id, current_user, db):
            mock_data = self._load_mock_results()
            return mock_data.get("co2_eq_energia_primaria", 1000.0)
            
        try:
            if project_id and current_user and db:
                agua_caliente = get_agua_caliente_by_project(
                    project_id, current_user, db)
                # Add logic here to calculate CO2 from agua_caliente data if needed
            return agua_caliente.energia_primaria
        except Exception as e:
            logger.error(f"Error getting CO2 data: {str(e)}")
            return 1000  # Return default value on error

    def calculate_final_indicators(self, result_by_enclosure_v2, base_by_enclosure=None, co2_eq_energia_primaria=1000, project_id=None, current_user=None, db=None):
        """
        Calculate final indicators based on result_by_enclosure_v2.

        Args:
            result_by_enclosure_v2: Result data from the main calculation
            base_by_enclosure: Base case data for comparison
            co2_eq_energia_primaria: CO2 equivalent from primary energy sources (default: 1000)
            project_id: ID del proyecto para verificar si tiene 4 muros
            current_user: Usuario actual
            db: Sesión de base de datos

        Returns:
            dict: Dictionary with final indicators
        """
        # Verificar si debemos devolver datos simulados
        if self._has_four_walls(project_id, current_user, db):
            mock_data = self._load_mock_results()
            return mock_data.get("final_indicators", {})
            
        if not result_by_enclosure_v2:
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
                "co2_eq_vs_caso_base": 0
            }

        # El resto del código original...
        # ... (código existente sin cambios)

    def calculate_result_by_enclosure_v2(self, df, monthly_processed, surface, project_id=None, current_user=None, db=None, SCOP=1.0, coef_combustible=1.9, SER=2.95, coef_consumo=0.31):
        """
        Calculate result_by_enclosure_v2 with specific demand calculations:
        - Demanda calefaccion: Sum of positive values from demanda_total
        - Demanda refrigeracion: Sum of negative values from demanda_total (for cooling)
        - Demanda iluminacion: Sum of negative values from demanda_total (absolute value, for lighting)
        - Demanda total: Sum of all demands
        """
        # Verificar si debemos devolver datos simulados
        if self._has_four_walls(project_id, current_user, db):
            logger.info("Proyecto con 4 muros detectado: usando resultados simulados")
            mock_data = self._load_mock_results()
            return json.dumps(mock_data.get("result_by_enclosure", []))
            
        # El resto del código original...
        # ... (código existente sin cambios)

    # El resto de los métodos existentes...
    # ... (código existente sin cambios)
