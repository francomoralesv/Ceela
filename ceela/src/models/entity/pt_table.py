from typing import Optional
from sqlmodel import SQLModel, Field

class PTTable(SQLModel, table=True):
    __tablename__ = "pt_table"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: Optional[int]
    P01: float = Field(default=0.0)
    P02: float = Field(default=0.0)
    P03: float = Field(default=0.0)
    P04: float = Field(default=0.0)
    P05: float = Field(default=0.0)
    P06: float = Field(default=0.0)
    total_pt: float = Field(default=0.0)
    pt_piso_prop: float = Field(default=0.0)
    pt_piso_base: float = Field(default=0.0)
    case: str = Field(default="Propuesto", max_length=50)