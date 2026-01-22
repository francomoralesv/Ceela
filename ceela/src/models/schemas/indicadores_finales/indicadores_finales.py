from sqlmodel import SQLModel, Field
from typing import Any, Dict, List, Optional
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class IndicadoresFinalesSave(SQLModel):
    data: Dict[str, str] = Field(default={}, sa_column=Column(JSONB, nullable=True))
    