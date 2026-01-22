from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Dict, Any


class FavCreate(SQLModel):
    fav1: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    fav2_izq: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    fav2_der: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    fav3: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))