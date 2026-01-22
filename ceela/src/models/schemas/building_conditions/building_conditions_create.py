from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Dict, Any

class BuildingConditionCreate(SQLModel):
    
    type: str
    attributes: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))