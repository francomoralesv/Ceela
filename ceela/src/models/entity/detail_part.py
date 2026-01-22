from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from src.models.schemas.details.detail_part_update import DetailPartCreate


class DetailPart(DetailPartCreate, table=True):
    __tablename__="details_part"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(nullable=True, default=None)
    type: str  # Muro, Techo, Piso
    value_u: float = Field(nullable=True, default=0)
    calculations: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    created_status: str = Field(default="created")
    code_ifc: str = Field(default="", nullable=True)
    