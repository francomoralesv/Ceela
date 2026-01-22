from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY

class Region(SQLModel, table=True):
    __tablename__="regiones"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre_region: str  # Campo obligatorio, sin default
    comunas: List["Comuna"] = Relationship(back_populates="region")


class Comuna(SQLModel, table=True):
    __tablename__ = "comunas"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre_comuna: str
    latitud: Optional[float] = Field(default=None)
    longitud: Optional[float] = Field(default=None)
    zonas_termicas: Optional[List[str]] = Field(
        default=None, sa_column=Column(ARRAY(String))
    )
    region_id: int = Field(foreign_key="regiones.id")
    region: Optional["Region"] = Relationship(back_populates="comunas")
