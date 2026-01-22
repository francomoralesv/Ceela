from sqlmodel import SQLModel, Field
from pydantic import field_validator
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any
from src.models.detail_base import DetailBase


class DetailCreate(DetailBase):
    interior_color: Optional[str] = None
    exterior_color: Optional[str] = None
    floor_insulation_details: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    @field_validator("interior_color", "exterior_color", mode="before")
    def validate_colors(cls, value, info):
        location = info.data.get("scantilon_location")

        if location in ["Muro", "Techo"]:
            if value is None:
                raise ValueError(f"{info.field_name} es obligatorio para {location}")

        elif location == "Piso":
            return None  

        return value

    @field_validator("floor_insulation_details", mode="before")
    def validate_floor_details(cls, value, info):
        location = info.data.get("scantilon_location")

        if location == "Piso":
            required_fields = [
                "vertical_lambda", "vertical_e_aisl", "vertical_d",
                "horizontal_lambda", "horizontal_e_aisl", "horizontal_d"
            ]
            if not isinstance(value, dict):
                raise ValueError("floor_insulation_details debe ser un diccionario")

            missing_fields = [field for field in required_fields if field not in value]

            if missing_fields:
                raise ValueError(f"Faltan los siguientes campos en floor_insulation_details: {', '.join(missing_fields)}")

        return value
