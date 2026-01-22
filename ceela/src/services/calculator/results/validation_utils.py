import os
import logging
import traceback

from src.services.datos.materials import WallEnclosure, WindowEnclosure, FloorEnclosure
from sqlalchemy.orm import Session
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.project_table import Project
from src.services.calculator.weather.weather_service import get_weather_data_from_coord_one

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def validate_project_requirements(project_id: int, db: Session, check_climate_file: bool = False):
    """
    Valida que el proyecto tenga al menos 3 muros, 1 ventana y 1 piso.
    Opcionalmente valida que exista un archivo de clima para las coordenadas del proyecto.
    
    Args:
        project_id (int): ID del proyecto
        db (Session): Sesión de base de datos
        check_climate_file (bool, optional): Si es True, verifica la existencia de archivo climático. Default is False.
    
    Returns:
        tuple: (bool, dict, dict) donde:
            - bool indica si cumple con los requerimientos básicos (muros, ventanas, pisos)
            - dict contiene los conteos por recinto
            - dict contiene información adicional, como validación de archivo climático
    """
    # Obtener todos los enclosure_id asociados al proyecto
    enclosures = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.project_id == project_id, EnclosureGenerals.is_deleted == False).all()

    enclosure_ids = [e.id for e in enclosures]
    # Crear un diccionario para mapear id a nombre
    enclosure_names = {e.id: e.name_enclosure for e in enclosures}

    enclosure_counts = {}
    all_valid = True
    for enclosure_id in enclosure_ids:
        wall_count = db.query(WallEnclosure).filter(
            WallEnclosure.enclosure_id == enclosure_id).count()
        window_count = db.query(WindowEnclosure).filter(
            WindowEnclosure.enclosure_id == enclosure_id).count()
        floor_count = db.query(FloorEnclosure).filter(
            FloorEnclosure.enclosure_id == enclosure_id).count()
        enclosure_counts[enclosure_id] = {
            "name": enclosure_names.get(enclosure_id, "Sin nombre"),
            "walls": wall_count,
            "windows": window_count,
            "floors": floor_count
        }
        if wall_count < 3 or window_count < 1 or floor_count < 1:
            all_valid = False
    
    additional_validations = {}
    
    # Validar archivo climático si se solicita
    if check_climate_file:
        climate_valid, climate_info = validate_climate_file_exists(project_id, db)
        additional_validations["climate_file"] = {
            "valid": climate_valid,
            "info": climate_info
        }
        # Si la validación de clima falla, el proyecto no es válido
        if not climate_valid:
            all_valid = False
    
    return (
        all_valid,
        enclosure_counts,
        additional_validations
    )

def validate_climate_file_exists(project_id: int, db: Session):
    """
    Valida que exista un archivo de clima para las coordenadas del proyecto.
    
    Args:
        project_id (int): ID del proyecto
        db (Session): Sesión de base de datos
        
    Returns:
        tuple: (bool, dict) donde bool indica si existe el archivo de clima y dict contiene información adicional
    """
    try:
        # Obtener el proyecto
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or not project.project_metadata:
            return False, {"error": "No se encontró el proyecto o no tiene metadatos"}
        
        # Extraer las coordenadas del proyecto
        latitude = project.latitude
        longitude = project.longitude
        zone = project.project_metadata.get("zone", None)

        if not zone:
            return False, {"error": "El proyecto no tiene zona definida en los metadatos"}

        if not latitude or not longitude:
            return False, {"error": "El proyecto no tiene coordenadas definidas"}
        
        # Buscar el archivo de clima usando las coordenadas
        weather_metadata = get_weather_data_from_coord_one(db, latitude, longitude, zone)
        
        # Verificar si se encontró metadata y si el archivo existe
        if not weather_metadata:
            return False, {"error": "No se encontró archivo climático para estas coordenadas"}
        
        # Verificar si el archivo físico existe
        file_path = weather_metadata.location
        print(f"[CLIMA] Ruta original desde DB: {file_path}")
        print(f"[CLIMA] ¿Es ruta absoluta?: {os.path.isabs(file_path)}")

        if not os.path.isabs(file_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            print(f"[CLIMA] Directorio base calculado: {base_dir}")
            file_path = os.path.join(base_dir, file_path)
            print(f"[CLIMA] Ruta absoluta construida: {file_path}")

        print(f"[CLIMA] Verificando existencia del archivo en: {file_path}")
        file_exists = os.path.exists(file_path)
        print(f"[CLIMA] ¿Archivo existe?: {file_exists}")

        if not file_exists:
            print(f"[CLIMA] ERROR: Archivo NO encontrado - Ruta DB: {weather_metadata.location}, Ruta buscada: {file_path}")
            logger.error(f"[CLIMA] Archivo NO encontrado - Ruta DB: {weather_metadata.location}, Ruta buscada: {file_path}")
            return False, {
                "error": f"El archivo climático existe en la base de datos pero no se encontró en la ruta {weather_metadata.location} (buscado en: {file_path})"
            }

        print(f"[CLIMA] Archivo encontrado exitosamente: {file_path}")
        logger.info(f"[CLIMA] Archivo encontrado exitosamente: {file_path}")
        
        return True, {
            "id": weather_metadata.id,
            "name": weather_metadata.name,
            "country": weather_metadata.country,
            "city": weather_metadata.city,
            "district": weather_metadata.district
        }
    
    except Exception as e:
        logger.error(f"Error validando archivo climático para proyecto {project_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return False, {"error": f"Error validando archivo climático: {str(e)}"}
