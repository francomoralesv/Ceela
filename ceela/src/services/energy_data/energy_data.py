from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.entity.energy_data import EnergyData

def get_energy_data(type: str, current_user: dict, db: Session):
    if type not in [
        "combustible", "rendimiento_acs", "distribucion_acs", "control_acs",
        "rendimiento_calef", "rendimiento_ref", "distribucion_hvac", "control_hvac", "co2_eq"
    ]:
        raise HTTPException(
            status_code=400,
            detail="El tipo seleccionado no esta entre los valores indicados"
        )
    
    energy_select = db.query(EnergyData).filter(
        EnergyData.type == type
    ).all()
    
    return [energy.name for energy in energy_select]