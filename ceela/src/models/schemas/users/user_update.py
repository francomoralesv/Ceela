from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from src.models.schemas.exceptions.exception import CustomValidationError
from src.translation.es import translations


class UserUpdate(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    number_phone: Optional[str] = None
    country: Optional[str] = None
    ubigeo: Optional[str] = None
    proffesion: Optional[str] = None
    
    @field_validator('name', 'lastname', 'number_phone', 'country', 'ubigeo', mode="before")
    def validate_length_1(cls, v, info):
        if v and len(v) > 50:
            field_name_translated = translations.get(info.field_name, info.field_name) 
            raise CustomValidationError(
                code="004", 
                message=f"El campo {field_name_translated} debe contener menos de 50 caracteres",
            )
        return v

    # Validación para campos no nfdsfulos
    @field_validator('name', 'lastname', 'number_phone','country', mode="before")
    def validate_length_2(cls, v, info):
        if len(v) == 0:
            field_name_translated = translations.get(info.field_name, info.field_name)  
            raise CustomValidationError(
                code="005", 
                message=f"El campo {field_name_translated} no debe ser nulo",
            )
        return v
    
class UserUpdateAdminRole(BaseModel):
    role_id: int = Field(le=2, ge=1)
    
    
class UserUpdateAdminActive(BaseModel):
    active: bool = Field(default=True)