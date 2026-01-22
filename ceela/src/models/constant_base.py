from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Dict, Any


class ConstantBase(SQLModel):
    atributs: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    name: str = Field(index=True)
    type: str