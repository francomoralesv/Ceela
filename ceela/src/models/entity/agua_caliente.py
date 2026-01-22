from sqlmodel import Field
from src.models.schemas.agua_caliente.agua_caliente_sanitaria import AguaCalienteSanitariaCreate
from typing import Optional


class AguaCalienteSanitaria(AguaCalienteSanitariaCreate, table=True):
    __tablename__="agua_caliente"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None)
 