from sqlalchemy.orm import Session
from src.models.entity.enclosure import Enclosure
from src.models.entity.schedule import DailySchedule
from src.models.entity.building_conditions import BuildingCondition

from sqlalchemy.orm import Session
from src.models.entity.enclosure import Enclosure
from src.models.entity.schedule import DailySchedule
from src.models.entity.building_conditions import BuildingCondition

def seed_default_daily_schedules(db: Session):
    # Tipos de horarios por defecto a insertar
    default_types = [
        "usuarios",
        "iluminacion verano",
        "iluminacion invierno",
        "equipos"
    ]
    
    # 1. Obtener en bloque todos los IDs de enclosures que ya tienen algún registro en DailySchedule
    scheduled_ids = set(
        row[0] for row in db.query(DailySchedule.perfil_id).distinct().all()
    )
    
    # 2. Consultar los enclosures que aún no tienen ningún registro en DailySchedule
    enclosures_to_seed = (
        db.query(Enclosure)
          .filter(~Enclosure.id.in_(scheduled_ids))
          .all()
    )
    
    # 3. Preparar los registros a insertar para cada enclosure sin registros
    new_records = []
    for enclosure in enclosures_to_seed:
        # Consultar la condición de edificio para este enclosure del tipo "internal_loads"
        building_condition = (
            db.query(BuildingCondition)
              .filter(BuildingCondition.enclosure_id == enclosure.id)
              .filter(BuildingCondition.type == "internal_loads")
              .first()
        )
        
        # Valor por defecto: todas las horas en 0
        hours = {f"hour_{i}": 0 for i in range(1, 25)}
        
        # Si existe building_condition y tiene atributos, se verifica el horario laboral
        if building_condition and building_condition.attributes:
            # Se asume que en attributes se encuentra directamente el JSON con los datos internos
            horario = building_condition.attributes.get("horario", {})
            laboral = horario.get("laboral", {})
            inicio = laboral.get("inicio")
            fin = laboral.get("fin")
            
            # Si se cumple la condición, se asigna 100 en las horas entre inicio y fin (inclusive)
            if inicio == 8 and fin == 18:
                for h in range(inicio, fin + 1):
                    hours[f"hour_{h}"] = 100
        
        # Para cada tipo de schedule, se crea un registro (usamos una copia de hours para evitar referencias compartidas)
        for schedule_type in default_types:
            new_record = {
                "type": schedule_type,
                "perfil_id": enclosure.id,
                "user_id": None,
            }
            new_record.update(hours.copy())
            new_records.append(new_record)
    
    # 4. Bulk insert de los registros nuevos si existen
    if new_records:
        db.bulk_insert_mappings(DailySchedule, new_records)
        db.commit()
        print(f"Seed completado: se insertaron {len(new_records)} registros de horarios por defecto.")
    else:
        print("Seed completado: no se insertaron registros, ya existen todos los horarios por defecto.")
