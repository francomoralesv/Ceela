from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Any


class ThermalBridge(SQLModel, table=True):
    __tablename__="thermal_bridges"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code_pt: str
    type_pt: str
    element_1: str
    element_2: str
    position_insulation: str
    insulation_thickness: float
    return_insulation: Any = Field(default=None, sa_column=Column(JSONB))
    position_window: Any = Field(default=None, sa_column=Column(JSONB))
    value_pt: float