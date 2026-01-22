from sqlmodel import SQLModel

class RoofEnclosureCreate(SQLModel):
    roof_id: int
    characteristic: str
    area: float