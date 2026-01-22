from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional
from typing import Dict, Any


class Calculation(SQLModel, table=True):
    __tablename__="calculations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(nullable=True, default=None)
    reference_id: Optional[int] = Field(default=None)
    type: str
    name: str
    formula: Optional[str] = Field(default=None)
    values: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))