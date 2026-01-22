from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator
from datetime import date
from typing import Optional
from src.models.schemas.exceptions.exception import CustomValidationError
from src.translation.es import translations

class UserBase(SQLModel):
    name: str 
    lastname: str
    email: EmailStr
    number_phone: str
    birthdate: Optional[date] = Field(default=None)
    country: str 
    ubigeo: Optional[str] = Field(default=None)
    proffesion: Optional[str] = Field(default=None, nullable=True)
    direccion: Optional[str] = Field(default=None, nullable=True)
    
    
    
    @field_validator("email", mode="before")
    def lower_email(cls, value: str) -> str:
        return value.lower() if isinstance(value, str) else value
    
    
    @field_validator('email', mode="before")
    def validate_email(cls, v):
        if len(v) > 50:
            raise CustomValidationError(
                code="003", 
                message="El correo electrónico debe contener menos de 50 caracteres",
            )
        return v

    # Validación para campos como name, lastname, etc.
    @field_validator('name', 'lastname', 'number_phone', 'country', 'ubigeo', mode="before")
    def validate_length_1(cls, v, info):
        if v and len(v) > 50:
            field_name_translated = translations.get(info.field_name, info.field_name) 
            raise CustomValidationError(
                code="004", 
                message=f"El campo {field_name_translated} debe contener menos de 50 caracteres",
            )
        return v

    # Validación para campos no nulos
    @field_validator('name', 'lastname', 'number_phone', 'email', 'country', mode="before")
    def validate_length_2(cls, v, info):
        if len(v) == 0:
            field_name_translated = translations.get(info.field_name, info.field_name)  
            raise CustomValidationError(
                code="005", 
                message=f"El campo {field_name_translated} no debe ser nulo",
            )
        return v
    