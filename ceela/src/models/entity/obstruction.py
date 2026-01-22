from sqlmodel import Field
from typing import Optional
from src.models.schemas.obstruction.obstruction import OrientationCreate, DivisionCreate


class Orientation(OrientationCreate, table=True):
    __tablename__="orientations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: Optional[int] = Field(default=None, foreign_key="enclosures_generals.id")
    orientation: str
    is_deleted: bool = Field(default=False)



class Division(DivisionCreate, table=True):
    __tablename__="divisions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    orientation_id: Optional[int] = Field(default=None, foreign_key="orientations.id")
    is_deleted: bool = Field(default=False)
    num_orientation: Optional[int] = Field(default=None, nullable=True)