from sqlmodel import SQLModel

class OrientationCreate(SQLModel):
    azimut: str
    
    
class DivisionCreate(SQLModel):
    division: str
    a: float
    b: float
    d: float