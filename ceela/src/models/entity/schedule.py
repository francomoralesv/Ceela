from typing import Optional
from sqlmodel import SQLModel, Field
from src.models.schemas.schedule.schedule import ScheduleCreate

class DailySchedule(ScheduleCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str = Field(..., description="el tipo de horario asociado")
    perfil_id: int = Field(..., description="ID del enclosure asociado")
    user_id: int = Field(nullable=True, description="ID del usuario dueño del horario")