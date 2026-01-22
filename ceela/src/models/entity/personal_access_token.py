from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from src.models.entity.user_table import UserTable


class PersonalAccessToken(SQLModel, table=True):
    __tablename__='personal_access_token'
    
    id: Optional[int] = Field(default=None,primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    token: str
    token_type: str
    in_used: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    expires_at: datetime
    
    user: "UserTable" = Relationship(back_populates="personal_access_tokens") # type: ignore