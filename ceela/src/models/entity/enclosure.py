from sqlmodel import SQLModel, Field, Relationship
from typing import List
from sqlalchemy.orm import Session
from typing import Optional
from src.models.schemas.enclosures.enclosure_create import EnclosureCreate


class Enclosure(EnclosureCreate, table=True):
    __tablename__="enclosures"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(nullable=True, default=None)
    original_id: Optional[int] = Field(nullable=True, default=None)
    code: str = Field(nullable=False, index=True)
    created_status: str = Field(default="created")
    is_deleted: bool = Field(default=False)
    code_ifc: Optional[str] = Field(default="", nullable=True)
    
    
    building_conditions: List["BuildingCondition"] = Relationship(back_populates="enclosure", sa_relationship_kwargs={"lazy": "selectin"}) # type: ignore
    
    def generate_code(self, db: Session):
        if not self.name or len(self.name) < 2:
            raise ValueError("El nombre debe tener al menos dos caracteres")

        clean_name = self.name.replace(" ", "")  

        existing_enclosure = db.query(Enclosure).filter(Enclosure.name == self.name).first()

        if existing_enclosure:
            base_code = existing_enclosure.code
            number = 1  
            if base_code[-1].isdigit(): 
                number = int(base_code[-1]) + 1
                real_code = base_code[:-1] + str(number)
            else:
                real_code = base_code + '2'
            
            while db.query(Enclosure).filter(Enclosure.code == real_code).first():
                number += 1
                real_code = base_code[:-1] + str(number) if base_code[-1].isdigit() else base_code + str(number)
            
            return real_code

        index = 1
        max_length = len(clean_name)

        while index < max_length:
            base_code = (clean_name[0] + clean_name[index]).upper()
      
            exist_code = db.query(Enclosure).filter(Enclosure.code == base_code).first()
            
            if not exist_code:
                return base_code
            
            index += 1

        number = 1  
        while True:
            numeric_code = f"{clean_name[0].upper()}{number}"

            exist_code = db.query(Enclosure).filter(Enclosure.code == numeric_code).first()
            
            if not exist_code:
                return numeric_code
            
            number += 1