from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional
from typing import Optional
from src.models.detail_base import DetailBase


class Detail(DetailBase, table=True):
    __tablename__="details"
    
    id: Optional[int] = Field(default=None, primary_key=True) 
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id")
    detail_part_id: Optional[int] = Field(nullable=True, default=None)
    is_deleted: bool = Field(default=False)
    created_status: str = Field(default="created")
    