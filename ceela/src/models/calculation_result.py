from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from typing import TYPE_CHECKING

# Import Project only for type checking to avoid circular imports
if TYPE_CHECKING:
    from src.models.entity.project_table import Project


class CalculationResult(SQLModel, table=True):
    __tablename__ = 'calculation_results'

    id: Optional[int] = Field(default=None, primary_key=True)
    final_indicators: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    result_by_enclosure: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    co2_eq: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        sa_column_kwargs={
            "server_default": func.now(),
            "nullable": False
        }
    )
    project_id: int = Field(foreign_key="projects.id", nullable=False)
    
    # Use string reference to avoid circular import
    project: Optional["Project"] = Relationship(back_populates="calculation_results", sa_relationship_kwargs={"cascade": "all, delete"})