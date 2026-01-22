from sqlmodel import SQLModel, Field
from typing import Optional

# 📌 Modelo para la tabla de Muros
class WallPO(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: Optional[int] = Field(default=None, foreign_key="enclosures_generals.id")
    wall_id: Optional[int] = Field(default=None)
    tipo_muro: str = Field(index=True)  # P01, P02, etc.
    nombre: str
    orientacion: str
    longitud_pt: Optional[float] = None
    categoria_1: str
    categoria_2: Optional[str] = None
    posicion_aislamiento_1: Optional[str] = None
    posicion_aislamiento_2: Optional[str] = None
    e_aislamient0_1: Optional[float] = None
    e_aislamiento_2: Optional[float] = None
    codigo_pt: Optional[str] = None
    pt: Optional[float] = None
    pt_lineal: Optional[float] = None
    espacio_contiguo: Optional[str] = None


# 📌 Modelo para la tabla de Ventanas (independiente de Muros)
class WindowPO(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: Optional[int] = Field(default=None, foreign_key="enclosures_generals.id")
    window_id: Optional[int] = Field(default=None)
    tipo: str  # DVH con 3mm, etc.
    hosted_in: str
    orientacion: str
    altura: float
    ancho: float
    categoria_muro: str
    categoria_ventana: str
    posicion_aislamiento: Optional[str] = None
    e_aislamient0_1: Optional[float] = None
    e_aislamiento_2: Optional[float] = None
    retorno: Optional[str] = None
    posicion_vidrio: Optional[str] = None
    codigo_pt: Optional[str] = None
    pt: Optional[float] = None
    pt_lineal: Optional[float] = None
    espacio_contiguo: Optional[str] = None


# 📌 Modelo para la tabla de Pisos
class FloorPO(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: Optional[int] = Field(default=None, foreign_key="enclosures_generals.id")
    floor_id: Optional[int] = Field(default=None)
    nombre: str
    longitud_pt: Optional[float] = None
    categoria: str
    categoria_1: str
    categoria_2: Optional[str] = None
    posicion_aislamiento: Optional[str] = None
    e_aislamiento_1: Optional[float] = None
    e_aislamiento_2: Optional[float] = None
    codigo_pt: Optional[str] = None
    pt: Optional[float] = None
    pt_lineal: Optional[float] = None
    espacio_contiguo: Optional[str] = None