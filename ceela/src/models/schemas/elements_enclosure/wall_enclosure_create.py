from sqlmodel import SQLModel, Field

class WallEnclosureCreate(SQLModel):
    wall_id: int
    characteristics: str
    angulo_azimut: str
    area: float = Field(default=0)
    