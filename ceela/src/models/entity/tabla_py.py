from sqlmodel import SQLModel, Field
from sqlalchemy.orm import Session
from typing import Optional

class TablaPy(SQLModel, table=True):
    __tablename__="tabla_py"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: int
    item_id: Optional[int] = Field(default=None)
    name: str
    type: str
    orientation: str
    nodos_emisividad: float
    nodos_area: float
    r_puro: float
    emisividad_x_sup: float
    r_a_atot: float
    