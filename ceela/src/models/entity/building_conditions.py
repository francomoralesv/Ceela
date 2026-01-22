from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from src.models.schemas.building_conditions.building_conditions_create import BuildingConditionCreate


class BuildingCondition(BuildingConditionCreate, table=True):
    __tablename__="building_conditions"
    
    id: Optional[int] =  Field(default=None, primary_key=True)
    enclosure_id: Optional[int] = Field(foreign_key="enclosures.id")
    created_status: str = Field(default="created")
    
    
    enclosure: Optional["Enclosure"] = Relationship(back_populates="building_conditions") # type: ignore 