from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.entity.regiones_comunas import Region, Comuna


def get_regiones(current_user: dict, db: Session):
    regiones = db.query(Region).all()
    
    return regiones


    
def get_comunas_by_region(region_id: int, current_user: dict, db: Session):
    comunas = db.query(Comuna).filter(
        Comuna.region_id == region_id
    ).all()
    
    if not comunas:
        raise HTTPException(
            status_code=400,
            detail=f"No existen comunas para el id de region {region_id}"
        )
    
    return [comuna.model_dump() for comuna in comunas]



def get_zona_termicas(comuna_id: int, current_user: dict, db: Session):
    comuna = db.query(Comuna).filter(
        Comuna.id == comuna_id
    ).first()
    
    if not comuna:
        raise HTTPException(
            status_code=400,
            detail=f"No existe comuna"
        )
        
    zone = comuna.zonas_termicas
    
    return zone