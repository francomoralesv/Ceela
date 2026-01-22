from typing import Dict
from sqlalchemy.orm import Session
from fastapi import Depends
from src.services.database.db_connection import get_db
from src.models.entity.constant import Constant
from src.models.entity.enclosure import Enclosure
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.building_conditions import BuildingCondition


def usage_profile(enclosure_id: int, db: Session) -> dict:
    """
    Calcula y retorna un diccionario con:
      - human_activity: tasa de gr_water_hour según la ocupación
      - num_people: número de usuarios (internal_loads.value['usuarios'])
    Basado en las BuildingCondition asociadas al enclosure.levantar
    """

    # 1) Traer el enclosure y validar que exista
    enclosure = (
        db.query(EnclosureGenerals)
          .filter(EnclosureGenerals.id == enclosure_id)
          .first()
    )
    if enclosure is None:
        raise ValueError(f"No existe EnclosureGenerals con id={enclosure_id}")

    # 2) Traer todas las BuildingCondition vinculadas al perfil de ocupación
    building_conditions = (
        db.query(BuildingCondition)
          .filter(
              BuildingCondition.enclosure_id
              == enclosure.occupation_profile_id
          )
          .all()
    )

    # 3) Extraer la condición de ventilación
    ventilation_flows = next(
        (c for c in building_conditions if c.type == "ventilation_flows"),
        None
    )
    if ventilation_flows is None:
        raise ValueError(f"No existe 'ventilation_flows' para enclosure {enclosure_id}")

    # 4) Extraer la ocupación dentro de caudal_min_salubridad
    flujo = ventilation_flows.attributes.get("cauldal_min_salubridad", {})
    ocupacion = flujo.get("ocupacion")
    if ocupacion is None:
        raise ValueError(
            f"No se encontró 'ocupacion' en caudal_min_salubridad para enclosure {enclosure_id}"
        )

    # 5) Traer la constante de actividad humana y buscar gr_water_hour
    human_activity_object = (
        db.query(Constant)
          .filter(Constant.type == "human_activity")
          .first()
    )
    if human_activity_object is None:
        raise ValueError("No existe Constant con type='human_activity'")

    human_activity = next(
        (
            lvl["gr_water_hour"]
            for lvl in human_activity_object.atributs.get("activity_levels", [])
            if lvl.get("name") == ocupacion
        ),
        None
    )
    if human_activity is None:
        raise ValueError(f"No se encontró nivel '{ocupacion}' en activity_levels")

    # 6) Extraer la condición de cargas internas y número de usuarios
    internal_loads = next(
        (c for c in building_conditions if c.type == "internal_loads"),
        None
    )
    if internal_loads is None:
        raise ValueError(f"No existe 'internal_loads' para enclosure {enclosure_id}")

    heated = next(
        (c for c in building_conditions if c.type == "schedule_weather"),
        None
    )
    print(f"heated {heated}")
    if heated is None:
        raise ValueError(f"No existe 'heated' para enclosure {enclosure_id}")

    usuarios = internal_loads.attributes.get("usuarios")
    if usuarios is None:
        raise ValueError(
            f"No se encontró 'usuarios' en internal_loads para enclosure {enclosure_id}"
        )

    horario = internal_loads.attributes.get("horario", {})
    laboral = horario.get("laboral", {})
    climatizado = heated.attributes.get('recinto', {}).get('climatizado', None)
    if climatizado is None:
        raise ValueError(
            f"No se encontró 'climatizado' en schedule_weather para enclosure {enclosure_id}"
        )
    funcionamiento_semanal = horario.get("funcionamiento_semanal", "")
    
    dia_inicio = 1
    dia_fin = funcionamiento_semanal.split("x")[0]
    print(f"horario {horario}")
    horario_inicio_str = laboral.get("inicio", "0:00")
    horario_fin_str = laboral.get("fin", "0:00")
    print(f"horario_inicio_str {horario_inicio_str}")
    print(f"horario_fin_str {horario_fin_str}")
    try:
        if isinstance(horario_inicio_str, str) and ":" in horario_inicio_str:
            horario_inicio = int(horario_inicio_str.split(":")[0])
        else:
            horario_inicio = int(horario_inicio_str)
    except (ValueError, AttributeError, IndexError, TypeError):
        horario_inicio = 8
        
    try:
        if isinstance(horario_fin_str, str) and ":" in horario_fin_str:
            horario_fin = int(horario_fin_str.split(":")[0])
        else:
            horario_fin = int(horario_fin_str)
    except (ValueError, AttributeError, IndexError, TypeError):
        horario_fin = 16
    # 7) Devolver resultado
    return {
        "human_activity": float(human_activity),
        "num_people":  float(usuarios),
        "hora_inicio":  int(horario_inicio),
        "hora_fin":  int(horario_fin),
        "dia_inicio":  int(dia_inicio),
        "climatizado": str(climatizado).lower()=='si',
        "dia_fin": int(dia_fin)
    }


def calc_humidity_by_project(project_id: int, db: Session) -> Dict[int, dict]:
    """
    Para un project_id dado, calcula la humedad para cada enclosure asociado.
    Retorna un dict { enclosure_id: resultado_de_calc_humidity }.
    """
    # 1) Obtener todos los enclosures del proyecto
    enclosures = (
        db.query(EnclosureGenerals)
          .filter(EnclosureGenerals.project_id == project_id)
          .all()
    )
    if not enclosures:
        raise ValueError(f"No se encontraron EnclosureGenerals para project_id={project_id}")

    resultados: Dict[int, dict] = {}

    # 2) Para cada enclosure, reutilizar la lógica de calc_humidity
    for enclosure in enclosures:
        # Aqui asumimos que existe tu función calc_humidity(enclosure_id, db)
        resultados[enclosure.id] = usage_profile(enclosure.id, db)

    return resultados

