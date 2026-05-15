from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.energy_data.energy_data import get_energy_data

router_controller_energy_data = APIRouter()


@router_controller_energy_data.get(
    "/{type}/energy-data",
    tags=["Energy-Data"],
    summary="Obtener Energy Data por tipo",
    description="""
Endpoint para obtener datos de EnergyData filtrados por tipo.

**Tipos permitidos en el parametro "type"**:

- **combustible**
- **rendimiento_acs**
- **distribucion_acs**
- **control_acs**
- **rendimiento_calef**
- **rendimiento_ref**
- **distribucion_hvac**:
- **control_hvac**
- **co2_eq**
    """
)
def get_energy_data_endpoint(
    type: str, 
    currente_user: dict = Depends(verify_token), 
    db: Session = Depends(get_db)
):
    return get_energy_data(type=type, current_user=currente_user, db=db)