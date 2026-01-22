from pydantic import BaseModel, EmailStr, field_validator

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator("email", mode="before")
    def lower_email(cls, value: str) -> str:
        return value.lower() if isinstance(value, str) else value