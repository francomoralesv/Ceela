from sqlmodel import SQLModel, Field
from typing import Optional
from src.models.schemas.thermal_bridges.thermal_bridges_create import ThermalBridgeWallCreate


class ThermalBridgeWall(ThermalBridgeWallCreate, table=True):
    __tablename__="thermals_bridges_walls"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    wall_id: Optional[int] = Field(default=None, nullable=True)
    enclosure_id: Optional[int] = Field(foreign_key="enclosures_generals.id")