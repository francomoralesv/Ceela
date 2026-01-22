from pydantic import BaseModel
from datetime import datetime
from uuid import UUID, uuid4
from .user import User

class Zone(BaseModel):
    country: str
    city: str
    district: str

class FileMetadata(BaseModel):
    id: UUID = uuid4()
    name: str
    location: str
    version: int
    created_at: datetime
    zone: Zone
    # uploaded_by: UUID  # Reference to User.id
    file_format: str = "parquet"
    content_hash: str  # To verify file uniqueness
