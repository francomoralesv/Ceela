from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from typing import Dict, Any


class DetailPartUpdate(SQLModel):
    name_detail: str = Field(nullable=True, default=None)
    info: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    
class DetailPartCreate(DetailPartUpdate):
    pass