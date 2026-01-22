from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from src.services.database.db_connection import get_db
from src.models.constant_base import ConstantBase
from src.services.constants.constants_service import create_constant, get_constants, get_constant, update_constant, \
    delete_constant, get_constant_by_id, get_material_by_code_ifc, update_energy_systems_consumos_por_fuente_de_energia
from src.utils.security.token.jwt_login import verify_token


router_constants_controller = APIRouter()


@router_constants_controller.post("/{section}/constants/create", tags=["Management Materials"])
def create(constant: ConstantBase, section: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_constant(section, current_user, constant, db)


@router_constants_controller.get("/{section}/constants/", tags=["Management Materials"])
def get_constant_endpoint(section: str, name: str = None, type: str = None, page: int = 1, per_page: int = 5, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_constants(section, current_user, db, name, type, page, per_page)


@router_constants_controller.get("/{section}/constants/{constants_id}/", tags=["Management Materials"])
def get_constant_by_id_endpoint(section: str, constant_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_constant_by_id(section, constant_id, current_user, db)


@router_constants_controller.put("/{section}/constant/{constant_id}/update", tags=["Management Materials"])
def update_constant_endpoint(section: str, constant_id: int, constant_update: ConstantBase, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_constant(section, current_user, constant_id, constant_update, db)


@router_constants_controller.delete("/{section}/constant/{constant_id}/delete", tags=["Management Materials"])
def delete_constant_endpoint(section: str, constant_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_constant(section, current_user, constant_id, db)


@router_constants_controller.get("/constants", tags=["Management Materials"])
def search_constants(type: Optional[str] = None, name: Optional[str] = None, db: Session = Depends(get_db)):
    return get_constant(db, name, type)


@router_constants_controller.get('/constants-code_ifc', tags=["Management Materials"])
def get_material_code_ifc(code_ifc: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_material_by_code_ifc(current_user, db, code_ifc)

from pydantic import BaseModel
from typing import List, Any
class ConsumosPorFuenteDeEnergiaModel(BaseModel):
    consumos_por_fuente_de_energia: List[Any]
@router_constants_controller.put('/update_energy_systems_consumos_por_fuente_de_energia', tags=["Management Materials"])
def update_energy_systems_consumos_por_fuente_de_energia_endpoint(
    data: ConsumosPorFuenteDeEnergiaModel,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    print(f"update_energy_systems_consumos_por_fuente_de_energia_endpoint")
    return update_energy_systems_consumos_por_fuente_de_energia(
        db, data.consumos_por_fuente_de_energia, current_user
    )