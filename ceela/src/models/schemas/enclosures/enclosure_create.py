from sqlmodel import SQLModel, Field


class EnclosureCreate(SQLModel):
    
    name: str = Field(nullable=False)