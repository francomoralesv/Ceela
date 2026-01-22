from pydantic import field_validator
from src.models.project_base import ProjectBase
from src.models.schemas.exceptions.exception import CustomValidationError
from src.translation.es import translations

class ProjectCreate(ProjectBase):
    building_type: str
    main_use_type: str
    number_levels: int
    number_homes_per_level: int
    built_surface: float
    latitude: float
    longitude: float
    building_name: str | None = None
    
    @field_validator("building_type",  mode="before")
    def validate_strings(cls, v, info):
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

    # Validación para valores numéricos positivos
    @field_validator("number_levels", "number_homes_per_level", "built_surface", mode="before")
    def validate_positive_numbers(cls, v, info):
        field_name_translated = translations.get(info.field_name, info.field_name)

        if v < 0:
            raise CustomValidationError(
                code="006",
                message=f"El campo {field_name_translated} debe ser un número positivo",
            )

        return v