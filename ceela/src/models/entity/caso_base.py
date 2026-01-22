from sqlmodel import SQLModel, Field
from typing import Dict, Optional, Any
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class CasoBase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: Optional[int] = Field(default=None)
    type: Optional[str] = Field(default="")
    characteristic: Optional[str] = Field(default="")
    item_id: Optional[int] = Field(default=None)
    data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))