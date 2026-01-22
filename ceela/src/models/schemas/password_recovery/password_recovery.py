from pydantic import BaseModel, EmailStr, field_validator

class PasswordRecoveryRequest(BaseModel):
    email: EmailStr
    
    
class PasswordResetRequest(PasswordRecoveryRequest):
    code: str
    new_password: str
    confirm_new_password: str    
    
    @field_validator('new_password')
    def password_validate(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        
        if len(v) > 50:
            raise ValueError("La contraseña debe tener menos de 20 caracteres")
        return v


    @field_validator('confirm_new_password')
    def passwords_match(cls, v, info):
        password = info.data.get('new_password')
        if password and v != password:
            raise ValueError("Las contraseñas no coinciden.")
        return v