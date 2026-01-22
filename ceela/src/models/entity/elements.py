from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from src.models.element_base import ElementBase

class Element(ElementBase, table=True):
    __tablename__="elements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, nullable=True, foreign_key="users.id")
    created_status: str = Field(default="created")
    is_deleted: bool = Field(default=False)
    calculations: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    code_ifc: Optional[str] = Field(default="", nullable=True)