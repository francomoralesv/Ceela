from sqlmodel import SQLModel, Field

class Level(SQLModel, table=True):
    __tablename__ = "levels"
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=True)
    description: str | None = Field(nullable=True, default=None)

