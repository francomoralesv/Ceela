from sqlmodel import SQLModel, Field
from typing import Optional
from src.models.schemas.elements_enclosure.wall_enclosure_create import WallEnclosureCreate

class WallEnclosure(WallEnclosureCreate, table=True):
    __tablename__="walls"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: Optional[int] = Field(default=None, foreign_key="enclosures_generals.id")
    orientation: str
    u: float
    is_base: Optional[bool] = Field(default=False, nullable=True)
    original_id: Optional[int] = Field(default=None, nullable=True)