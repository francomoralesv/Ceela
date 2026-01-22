from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models.entity.heating_config import HeatingConfig
from src.models.entity.project_table import Project
from src.services.calculator.heating_config_service import HeatingConfigService
from src.services.database.db_connection import get_db
from src.utils.security.token.jwt_login import verify_token


class HeatingConfigCreate(BaseModel):
    project_id: int
    combustible_codigo: str
    combustible_valor: float
    rendimiento_codigo: Optional[str] = None
    rendimiento_valor: Optional[float] = None
    caldera_codigo: Optional[str] = None
    caldera_valor: Optional[float] = None
    distribucion_codigo: Optional[str] = None
    distribucion_valor: Optional[float] = None
    control_codigo: Optional[str] = None
    control_valor: Optional[float] = None


heating_config_router = APIRouter()


@heating_config_router.post("/heating-config/by-project/{project_id}", response_model=HeatingConfig, tags=["HeatingConfig"])
def create_heating_config(
    project_id: int,
    config: HeatingConfigCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    # Validar que el proyecto exista
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    data = config.dict()
    data["project_id"] = project_id
    return HeatingConfigService.create_heating_config(project_id, data, db)


@heating_config_router.get("/heating-config/by-project/{project_id}", response_model=HeatingConfig, tags=["HeatingConfig"])
def get_heating_config_by_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    config = HeatingConfigService.get_heating_config(project_id, db)
    if not config:
        raise HTTPException(
            status_code=404, detail="No heating config found for this project")
    return config
