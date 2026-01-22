from sqlmodel import SQLModel, Field
from typing import Optional

class EnergyData(SQLModel, table=True):
    __tablename__="energy_data"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    name: str
    value: float