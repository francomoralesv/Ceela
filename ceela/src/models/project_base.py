from sqlmodel import SQLModel, Field
from pydantic import field_validator
from sqlalchemy import Column, ARRAY, Integer
from sqlalchemy.dialects.postgresql import JSONB
from typing import Dict, List, Optional
from src.models.schemas.exceptions.exception import CustomValidationError
from src.translation.es import translations


class ProjectBase(SQLModel):
    country: Optional[str] = Field(default=None)
    divisions: Dict[str, str] = Field(default={}, sa_column=Column(JSONB))
    name_project: str
    owner_name: str
    owner_lastname: str
    project_metadata: Dict[str, str] = Field(default={}, sa_column=Column(JSONB, nullable=True))
    residential_type: Optional[str] = Field(default=None)
    created_at: Optional[str] = None

    @field_validator("name_project", "owner_name", "owner_lastname", "country", mode="before")
    def validate_fields(cls, v, info):
        field_name_translated = translations.get(info.field_name, info.field_name)  

        if not v or len(v.strip()) == 0:
            raise CustomValidationError(
                code="005",
                message=f"El campo {field_name_translated} no debe ser nulo",
            )

        if len(v) > 50:
            raise CustomValidationError(
                code="004",
                message=f"El campo {field_name_translated} debe contener menos de 50 caracteres",
            )

        return v