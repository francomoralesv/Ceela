from src.models.entity.personal_access_token import PersonalAccessToken
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, Relationship
from src.models.user_base import UserBase


class UserTable(UserBase, table=True):
    __tablename__ = 'users'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    active: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    role_id: int = Field(default=2)
    last_activity: Optional[datetime] = Field(default=None)
    personal_access_tokens: list["PersonalAccessToken"] = Relationship(back_populates="user")
    projects: list["Project"] = Relationship(back_populates="user") # type: ignore

