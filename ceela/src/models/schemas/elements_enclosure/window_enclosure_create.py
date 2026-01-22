from sqlmodel import SQLModel

class WindowEnclosureCreate(SQLModel):
    window_id: int
    characteristics: str
    angulo_azimut: str
    housed_in: int
    position: str
    with_no_return: str
    high: float
    broad: float