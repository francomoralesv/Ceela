from pydantic import BaseModel, field_validator, EmailStr


class Request2FA(BaseModel):
    email: EmailStr
    otp: str
    
    
    @field_validator("email", mode="before")
    def lower_email(cls, value: str) -> str:
        return value.lower() if isinstance(value, str) else value
    
    @field_validator('otp')
    def validate_code(cls, v):
        if len(v) != 6:
            raise ValueError("El codigo debe tener 6 digitos")
        return v
    