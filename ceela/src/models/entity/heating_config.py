from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .project_table import Project


class HeatingConfig(SQLModel, table=True):
    __tablename__ = 'heating_config'
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", unique=True)
    combustible_codigo: str
    combustible_valor: float
    rendimiento_codigo: Optional[str] = None
    rendimiento_valor: Optional[float] = None
    caldera_codigo: Optional[str] = None
    caldera_valor: Optional[float] = None
    distribucion_codigo: Optional[str] = None
    distribucion_valor: Optional[float] = None
    control_codigo: Optional[str] = None
    control_valor: Optional[float] = None
    project: Optional["Project"] = Relationship(
        back_populates="heating_config")
