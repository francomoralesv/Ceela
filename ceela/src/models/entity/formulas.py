from sqlmodel import SQLModel, Field
from typing import Dict, Any
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Formulas(SQLModel, table=True):
    __tablename__="formulas"
    
    id: int = Field(default=None, primary_key=True)
    project_id: int = Field(default=None, nullable=True, foreign_key="projects.id")
    item_id: int 
    type: str 
    name: str
    atributs: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    is_deleted: bool = Field(default=False)
    