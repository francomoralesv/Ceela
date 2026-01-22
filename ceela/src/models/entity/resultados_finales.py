from typing import Optional
from sqlmodel import SQLModel, Field
from src.models.schemas.resultados.resultados_por_recinto import ResultadosPorRecintoSave

class ResultadosPorRecinto(ResultadosPorRecintoSave, table=True):
    __tablename__='resultados_por_recinto'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: Optional[int] = Field(default=None)
    perfil_id: Optional[int] = Field(default=None)
    project_id: Optional[int] = Field(default=None)
    type: str