from typing import Optional
from sqlmodel import Field
from src.models.schemas.indicadores_finales.indicadores_finales import IndicadoresFinalesSave

class IndicadoresFinales(IndicadoresFinalesSave, table=True):
    __tablename__="indicadores_finales"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None)
    type: str = Field(default=None)