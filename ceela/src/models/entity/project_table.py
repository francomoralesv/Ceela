from sqlmodel import Field, Relationship
from datetime import datetime, timezone
from typing import Optional, List
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.calculation_result import CalculationResult
from src.models.entity.user_table import UserTable 
from src.models.entity.heating_config import HeatingConfig

from src.models.schemas.projects.project_create import ProjectCreate
from src.models.schemas.projects.projects_update import ProjectStatus

# Import the string reference for runtime relationship resolution
from src.models.calculation_result import CalculationResult


class Project(ProjectStatus, ProjectCreate, table=True):
    __tablename__="projects"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    are_files_processed: Optional[bool] = Field(default=False)
    building_name: Optional[str] = Field(default=None)
    user: Optional["UserTable"] = Relationship(back_populates="projects") # type: ignore
    heating_config: Optional["HeatingConfig"] = Relationship(back_populates="project")
    calculation_results: List["CalculationResult"] = Relationship(sa_relationship_kwargs={"back_populates": "project", "cascade": "all, delete"})