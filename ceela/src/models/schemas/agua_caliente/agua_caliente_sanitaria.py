from typing import Any, Dict, List, Optional
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field


class AguaCalienteSanitariaCreate(SQLModel):
    t_acs: float = Field(default=0.0)
    demanda_acs: float = Field(default=0.0)
    combustible: str = Field(default="")
    rendimiento: str = Field(default="")
    sist_distribucion: str = Field(default="")
    sis_control: str = Field(default="")
    consumo_acs: float = Field(default=0.0)
    consumo_energia_primaria: float = Field(default=0.0)
    energia_primaria: float = Field(default=0.0)
    data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )