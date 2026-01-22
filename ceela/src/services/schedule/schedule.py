from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from sqlalchemy.orm.attributes import flag_modified
from fastapi import HTTPException, status
from src.models.entity.schedule import DailySchedule
from src.models.schemas.schedule.schedule import ScheduleCreate
from src.models.entity.enclosure import Enclosure
from src.models.entity.building_conditions import BuildingCondition

DEFAULT_TYPES = [
    "usuarios",
    "iluminacion verano",
    "iluminacion invierno",
    "equipos"
]

def create_daily_schedule(user_id: int, perfil_id: int, db: Session):
    """
    Crea registros de DailySchedule con horarios por defecto (todas las horas en 0)
    para cada tipo definido en DEFAULT_TYPES, asignando el user_id y el perfil_id.
    Solo se crean si no existe ya un registro para ese perfil y tipo.
    """
    new_records = []
    
    # Consultar la condición de edificio para el perfil (enclosure) del tipo "internal_loads"
    building_condition = (
        db.query(BuildingCondition)
          .filter(
              BuildingCondition.enclosure_id == perfil_id,
              BuildingCondition.type == "internal_loads"
          )
          .first()
    )
    
    # Valor por defecto: todas las horas en 0
    hours = {f"hour_{i}": 0 for i in range(1, 25)}
    
    # Si existe la condición y tiene atributos, se verifica el horario laboral
    if building_condition and building_condition.attributes:
        horario = building_condition.attributes.get("horario", {})
        laboral = horario.get("laboral", {})
        inicio = laboral.get("inicio")
        fin = laboral.get("fin")
        
        # Si se cumple la condición, se asigna 100 en las horas entre inicio y fin (inclusive)
        if inicio == 8 and fin == 18:
            for h in range(inicio, fin + 1):
                hours[f"hour_{h}"] = 100

    # Para cada tipo definido en DEFAULT_TYPES, se crea un registro si no existe ya para ese perfil
    for schedule_type in DEFAULT_TYPES:
        existing = db.query(DailySchedule).filter(
            DailySchedule.type == schedule_type,
            DailySchedule.perfil_id == perfil_id
        ).first()
        if not existing:
            new_record = {
                "type": schedule_type,
                "perfil_id": perfil_id,
                "user_id": user_id,
            }
            # Se agrega una copia de hours para que cada registro tenga su propio diccionario
            new_record.update(hours.copy())
            new_records.append(new_record)
    
    if new_records:
        db.bulk_insert_mappings(DailySchedule, new_records)
        db.commit()
        return {"message": f"Se crearon {len(new_records)} registros de horarios por defecto."}
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existen registros por defecto para este perfil."
        )


def get_daily_schedule(type: str, current_user: dict, perfil_id: int, db: Session):
    """
    Retorna el registro de DailySchedule para el tipo y perfil_id especificados,
    mostrando únicamente aquellos que sean globales (user_id == None) o
    que pertenezcan al usuario actual.
    """
    schedule = db.query(DailySchedule).filter(
        DailySchedule.type == type,
        DailySchedule.perfil_id == perfil_id,
        or_(
            DailySchedule.user_id == current_user["user_id"],
            DailySchedule.user_id.is_(None)
        )
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro no encontrado o sin permisos."
        )
    return schedule


def update_daily_schedule(type: str, current_user: dict, perfil_id: int, update_data: ScheduleCreate, db: Session):
    # 📍 Obtener el recinto (no eliminado) junto con sus building_conditions
    enclosure = (
        db.query(Enclosure)
        .filter(Enclosure.id == perfil_id, Enclosure.is_deleted == False)
        .options(joinedload(Enclosure.building_conditions))
        .first()
    )
    if not enclosure:
        raise HTTPException(status_code=404, detail="Recinto no encontrado.")

    # 🔄 Si es un recinto global/default sin user_id, lo clonamos para el usuario
    if enclosure.user_id is None and enclosure.created_status in ["default", "global"]:
        enclosure = clone_enclosure(enclosure, current_user, db)
        perfil_id = enclosure.id

    # 📑 Obtener todos los schedules de ese tipo y perfil (propios o genéricos)
    schedules = db.query(DailySchedule).filter(
        DailySchedule.type == type,
        DailySchedule.perfil_id == perfil_id,
        or_(
            DailySchedule.user_id == current_user["user_id"],
            DailySchedule.user_id.is_(None)
        )
    ).all()

    if not schedules:
        raise HTTPException(status_code=404, detail="No se encontraron registros para este tipo.")

    # 🎯 Elegir primero el schedule del usuario, si existe
    schedule_actual = next((s for s in schedules if s.user_id == current_user["user_id"]), None)

    # 🆕 Si no existe uno propio, clonamos el genérico y lo asignamos al usuario
    if schedule_actual is None:
        schedule_template = next((s for s in schedules if s.user_id is None), None)
        if schedule_template:
            data = {
                key: val
                for key, val in schedule_template.__dict__.items()
                if not key.startswith("_")
            }
            data.update(vars(update_data) if isinstance(update_data, dict) else update_data.dict())
            data["user_id"] = current_user["user_id"]
            data["perfil_id"] = perfil_id
            new_schedule = DailySchedule(**data)
            db.add(new_schedule)
            db.commit()
            db.refresh(new_schedule)
            schedule_actual = new_schedule
        else:
            raise HTTPException(status_code=404, detail="No se encontró un registro para actualizar.")

    # 🔧 Aplicar los cambios al schedule existente
    update_dict = vars(update_data) if isinstance(update_data, dict) else update_data.dict()
    for key, value in update_dict.items():
        if hasattr(schedule_actual, key):
            setattr(schedule_actual, key, value)

    db.commit()
    db.refresh(schedule_actual)

    # ✅ Retornamos el schedule actualizado sin tocar hora inicio/fin
    return schedule_actual


def clone_enclosure(enclosure: Enclosure, current_user: dict, db: Session) -> Enclosure:
    """
    Clona un recinto global (user_id == None) y sus building_conditions, así como los registros de DailySchedule,
    para asignarlo al usuario. Se asigna el campo original_id para vincular la copia con el original.
    """
    # Clonar el recinto
    cloned_enclosure = Enclosure(
        name = enclosure.name,
        # Se puede generar un nuevo código si es necesario; en este ejemplo se reutiliza el existente
        code = enclosure.code,
        created_status = "cloned",
        user_id = current_user["user_id"],
        is_deleted = enclosure.is_deleted,
        original_id = enclosure.id  # Campo que relaciona con el recinto original
        # Copia otros campos necesarios...
    )
    
    db.add(cloned_enclosure)
    db.commit()
    db.refresh(cloned_enclosure)
    
    # Clonar las building_conditions
    for bc in enclosure.building_conditions:
        cloned_bc = BuildingCondition(
            enclosure_id = cloned_enclosure.id,
            type = bc.type,
            created_status = bc.created_status,
            attributes = bc.attributes
            # Clona otros campos si es necesario
        )
        db.add(cloned_bc)
    db.commit()
    
    # Clonar los registros de DailySchedule asociados al recinto original
    original_schedules = db.query(DailySchedule).filter(DailySchedule.perfil_id == enclosure.id).all()
    for schedule in original_schedules:
        # Convertir el schedule en un diccionario limpio, omitiendo claves internas
        schedule_data = schedule.__dict__.copy()
        schedule_data.pop("id", None)
        schedule_data.pop("_sa_instance_state", None)
        
        # Actualizar el perfil_id y el user_id para la copia
        schedule_data["perfil_id"] = cloned_enclosure.id
        schedule_data["user_id"] = current_user["user_id"]
        
        new_schedule = DailySchedule(**schedule_data)
        db.add(new_schedule)
    db.commit()
    
    db.refresh(cloned_enclosure)
    return cloned_enclosure