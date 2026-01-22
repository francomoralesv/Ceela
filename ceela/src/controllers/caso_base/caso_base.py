from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.base.caso_base import obtener_casos_base_filtrados

router_caso_base = APIRouter()


@router_caso_base.get("/caso-base/{enclosure_id}", tags=["CASO BASE"])
def get_caso_base(enclosure_id: int, type: Optional[str] = None, db: Session = Depends(get_db)):
    return obtener_casos_base_filtrados(enclosure_id, db, type)