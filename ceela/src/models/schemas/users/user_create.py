from sqlmodel import Field
from src.models.user_base import UserBase
from pydantic import field_validator
from src.models.schemas.exceptions.exception import CustomValidationError

class UserCreate(UserBase):
    password: str
    confirm_password: str
    
   
    @field_validator('password')
    def password_validate(cls, v):
        if len(v) < 8:
            raise CustomValidationError(
                code="001", 
                message="La contraseña debe tener al menos 8 caracteres",
            )
        if len(v) > 50:
            raise CustomValidationError(
                code="002", 
                message="La contraseña debe tener menos de 50 caracteres",
            )
        return v


    # Validador para confifdsfddrmar la contraseña
    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        password = info.data.get('password')
        if password and v != password:
            raise CustomValidationError(
                code="003", 
                message="Las contraseñas no coinciden.",
            )
        return v
    
    
class UserCreateAdmin(UserCreate):
    role_id: int = Field(default=2)
    