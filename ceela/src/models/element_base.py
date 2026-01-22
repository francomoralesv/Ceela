from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import field_validator
from typing import Dict, Any
from src.models.schemas.exceptions.exception import CustomValidationError
from src.translation.es import translations


class ElementBase(SQLModel):
    name_element: str
    type: str
    atributs: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    u_marco: float
    fm: float
    
    
    @field_validator("name_element", "type", mode="before")
    def validate_strings(cls, value, info):
        field_name_translated = translations.get(info.field_name, info.field_name)

        if not value or len(value.strip()) == 0:
            raise CustomValidationError(
                code=8,
                message=f"El campo {field_name_translated} no debe estar vacío",
            )

        if len(value) > 50:
            raise CustomValidationError(
                code=9,
                message=f"El campo {field_name_translated} debe contener menos de 50 caracteres",
            )

        return value

    @field_validator("type")
    def validate_type(cls, value):
        field_name_translated = translations.get("type", "type")
        if value not in {"door", "window"}:
            raise CustomValidationError(10, f"El campo {field_name_translated} debe ser 'door' o 'window'")
        return value

    @field_validator("u_marco", "fm", mode="before")
    def validate_positive_numbers(cls, value, info):
        field_name_translated = translations.get(info.field_name, info.field_name)

        if value is None or value < 0:
            raise CustomValidationError(
                code=11,
                message=f"El campo {field_name_translated} debe ser un número positivo",
            )

        return value

    @field_validator("fm", mode="before")
    def validate_fm(cls, value):
        field_name_translated = translations.get("fm", "fm")
        if not (0 <= value <= 100):
            raise CustomValidationError(
                code=12,
                message=f"El campo {field_name_translated} debe estar entre 0 y 100",
            )
        return value