from sqlmodel import Field, Relationship
from typing import Optional
from src.models.entity.formulas import Formulas
from src.models.constant_base import ConstantBase


class Constant(ConstantBase, table=True):
    __tablename__="constants"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, nullable=True, foreign_key="users.id")
    create_status: str = Field(default="created")
    is_deleted: bool = Field(default=False)
    code_ifc: Optional[str] = Field(default="", nullable=True)
    