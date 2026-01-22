from uuid import uuid4
from sqlmodel import UUID, SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON  # Use JSON for compatibility

class WeatherMetadata(SQLModel, table=True):
    __tablename__ = "weather_metadata"
    
    id: int = Field(primary_key=True)
    name: str
    location: str
    version: int
    created_at: datetime
    content_hash: str
    country: str
    city: str = Field(default="")
    district: str = Field(default="")
    extension: str = Field(default="")
    file_size: int = Field(default=0)
    zone: Optional[str] = Field(default="")
    complementary: Optional[str] = Field(default=None)
