from typing import Any, Dict, List, Optional
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlmodel import Field, SQLModel

class ResultadosPorRecintoSave(SQLModel):
    recinto: str
    perfil_uso: str
    superficie: float
    categorias: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )