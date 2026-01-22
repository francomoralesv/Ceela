from sqlmodel import SQLModel

class DetailBase(SQLModel):
    scantilon_location: str 
    name_detail: str
    material_id: int
    layer_thickness: float
    
   