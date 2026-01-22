from sqlmodel import SQLModel, Field
from typing import Optional
from src.models.schemas.enclosures_generals.enclosure_create import EnclosureGeneralsCreate


class EnclosureGenerals(EnclosureGeneralsCreate, table=True):
    __tablename__="enclosures_generals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(foreign_key="projects.id")
    is_deleted: Optional[bool] = Field(default=False, nullable=True)
    is_base: Optional[bool] = Field(default=False, nullable=True)
    original_enclosure_id: Optional[int] = Field(default=None, nullable=True)