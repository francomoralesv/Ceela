from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.services.database.db_connection import get_db
from src.utils.security.token.jwt_login import verify_token
from src.models.schemas.details.details_create import DetailBase
from src.models.schemas.details.detail_part_update import DetailPartUpdate, DetailPartCreate
from src.services.details.details_v2 import create_detail_part, create_detail_v2, update_detail, get_detail_part_by_id, \
    get_details_by_detail_part, delete_details, get_detail_part_by_name

router_detail_part_controller = APIRouter()

@router_detail_part_controller.post("/{section}/{type}/detail-part-create", tags=["Management DetailPart"])
def create_detail_part_endpoint(type: str, detail_create: DetailPartCreate, section: str, project_id: int = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_detail_part(db, detail_create, type, project_id, current_user, section)


@router_detail_part_controller.post("/{section}/detail-create/{detail_part_id}", tags=["Management DetailPart"])
def create_detail_part_endpoint(detail_create: DetailBase, section: str, detail_part_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_detail_v2(detail_create, current_user, db, section, detail_part_id)


@router_detail_part_controller.patch("/{section}/detail-update/{detail_id}", tags=["Management DetailPart"])
def update_detail_endpoint(detail_id: int, detail_update: DetailBase, section: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_detail(detail_id, detail_update, current_user, db, section)


@router_detail_part_controller.get("/{section}/detail-part/{detail_id}", tags=["Management DetailPart"])
def get_detail_part_endpoint(detail_id: str, section: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_detail_part_by_id(db, detail_id, current_user, section)


@router_detail_part_controller.get("/{section}/detail-part-by-name/{name}", tags=["Management DetailPart"])
def get_detail_part_by_name_endpoint(name: str, section: str, project_id: int = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Obtiene un DetailPart por su nombre.

    Parámetros:
    - name: Nombre del DetailPart a buscar.
    - section: Sección ('user' o 'admin').
    - project_id: ID del proyecto (opcional).
    - current_user: Información del usuario actual.
    - db: Sesión de base de datos.

    Retorna:
    - Objeto DetailPart encontrado.
    """
    return get_detail_part_by_name(db, name, current_user, section, project_id)


@router_detail_part_controller.get("/detail-part/{detail_part_id}", tags=["Management DetailPart"])
def get_details_by_detail_part_endpoint(detail_part_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Obtiene todos los detalles asociados a un DetailPart específico.

    Es para capas.

    Parámetros:
    - detail_part_id: ID del DetailPart padre.
    - current_user: Información del usuario actual.
    - db: Sesión de base de datos.

    Retorna:
    - Lista de objetos Detail asociados al DetailPart.
    """
    return get_details_by_detail_part(db, detail_part_id, current_user)

@router_detail_part_controller.delete("/detail-general/{detail_id}/{is_layer}", tags=["Management DetailPart"])
def delete_detail_part_endpoint(detail_id: int, is_layer: bool = True,  db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    return delete_details(detail_id,is_layer,db, current_user)
