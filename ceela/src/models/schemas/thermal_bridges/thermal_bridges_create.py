from sqlmodel import SQLModel, Field
from typing import Optional, Literal

class ThermalBridgeWallCreate(SQLModel):
    
    po1_length: Optional[float] = Field(default=None, description="Longitud del PO1")
    po1_id_element: Optional[int] = Field(default=None, description="Identificador del elemento en PO1")
    
    po2_length: Optional[float] = Field(default=None, description="Longitud del PO2")
    po2_id_element: Optional[int] = Field(default=None, description="Identificador del elemento en PO2")
    
    po3_length: Optional[float] = Field(default=None, description="Longitud del PO3")
    po3_id_element: Optional[int] = Field(default=None, description="Identificador del elemento en PO3")
    
    po4_length: Optional[float] = Field(default=None, description="Longitud del PO4")
    po4_e_aislacion: Optional[float] = Field(default=None, description="Espesor de aislamiento en PO4")
    po4_id_element: Optional[int] = Field(default=None, description="Identificador del elemento en PO4")
    