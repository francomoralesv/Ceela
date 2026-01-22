from pydantic import BaseModel
from uuid import UUID, uuid4

class User(BaseModel):
    id: UUID = uuid4()
    username: str
    email: str
