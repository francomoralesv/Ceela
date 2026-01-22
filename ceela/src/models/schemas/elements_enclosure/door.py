from sqlmodel import SQLModel, Field

class DoorEnclosureCreate(SQLModel):
    door_id: int
    characteristics: str
    angulo_azimut: str
    high: float
    broad: float
    