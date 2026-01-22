from sqlmodel import SQLModel, Field
from typing import Optional

class EnclosureGeneralsCreate(SQLModel):
    name_enclosure: str
    occupation_profile_id: Optional[int] = Field(foreign_key="enclosures.id")
    height: float
    co2_sensor: str
    level_id: Optional[int] = Field(default=None, nullable=True)