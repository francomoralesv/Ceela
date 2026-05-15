from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from src.services.schedule.schedule import get_daily_schedule, update_daily_schedule
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.models.entity.schedule import DailySchedule
from src.models.entity.schedule import ScheduleCreate


router_scheule_controllers = APIRouter()


@router_scheule_controllers.get("/{type}/schedule/{perfile_id}", tags=["Schedules"], description="Los posibles valores para 'type' son: usuarios, iluminacion verano, iluminacion invierno y equipos.")
def get_schedule(type: str, perfile_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_daily_schedule(type, current_user, perfile_id, db)


@router_scheule_controllers.patch("/{type}/schedule-update/{perfile_id}", tags=["Schedules"], description="Los posibles valores para 'type' son: usuarios, iluminacion verano, iluminacion invierno y equipos.")
def update_schedule(type: str, perfile_id: int, schedule: ScheduleCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_daily_schedule(type, current_user, perfile_id, schedule, db)

