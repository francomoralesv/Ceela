from sqlmodel import SQLModel, Field


class FloorEnclosureCreate(SQLModel):
    floor_id: int
    characteristic: str
    area: float
    parameter: float = Field(default=0.0, nullable=True)
    is_ventilated: str = Field(default="", nullable=True)
    