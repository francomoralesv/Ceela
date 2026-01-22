from sqlmodel import SQLModel, Field
from typing import Optional
from src.models.schemas.elements_enclosure.door import DoorEnclosureCreate


class DoorEnclosure(DoorEnclosureCreate, table=True):
    __tablename__="doors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: Optional[int] = Field(foreign_key="enclosures_generals.id")
    orientation: str
    is_base: Optional[bool] = Field(default=False, nullable=True)
    original_id: Optional[int] = Field(default=None, nullable=True)