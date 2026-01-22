from sqlmodel import SQLModel, Field

class Customization(SQLModel, table=True):
    __tablename__="customizations"
    
    id: int = Field(default=None, primary_key=True)
    primary_color: str
    secondary_color: str 
    background_color: str
    logo_url: str = Field(default=None)  
