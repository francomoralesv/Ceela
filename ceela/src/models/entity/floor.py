from sqlmodel import SQLModel, Field
from typing import Optional
from src.models.schemas.elements_enclosure.floor import FloorEnclosureCreate

class FloorEnclosure(FloorEnclosureCreate, table=True):
    __tablename__="floors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: Optional[int] = Field(default=None, foreign_key="enclosures_generals.id")
    u: float
    po6_l: float
    is_base: Optional[bool] = Field(default=False, nullable=True)
    original_id: Optional[int] = Field(default=None, nullable=True)