from src.services.elements.elements import get_element_by_code_ifc

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from src.models.element_base import ElementBase
from src.services.elements.room_structured_data import process_structured_payload
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.elements.elements import create_elements, get_elements, get_element_by_id, update_element, delete_element
from src.models.element_base import ElementBase


router_elements_controller = APIRouter()


@router_elements_controller.post("/{section}/elements/create", tags=["Management Elements"])
def create_element_endpoint(section: str, element: ElementBase, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_elements(section, element, current_user, db)


@router_elements_controller.get("/{section}/elements/", tags=["Management Elements"])
def get_elements_endpoint(section: str, type: Optional[str] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_elements(section, type, current_user, db)


@router_elements_controller.get("/{section}/elements/{element_id}", tags=["Management Elements"])
def get_elements_by_id_endpoint(section: str, element_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_element_by_id(section, element_id, current_user, db)


@router_elements_controller.put("/{section}/elements/{element_id}/update", tags=["Management Elements"])
def update_element_endpoint(section: str, element_id: int, element: ElementBase, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_element(section, element_id, element, current_user, db)


@router_elements_controller.delete("/{section}/elements/{element_id}/delete", tags=["Management Elements"])
def delete_element_endpoint(section: str, element_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_element(section, current_user, element_id, db)


@router_elements_controller.get("/{section}/elements/by_code_ifc/{code_ifc}", tags=["Management Elements"])
def get_element_by_code_ifc_endpoint(section: str, code_ifc: str, db: Session = Depends(get_db)):
    return get_element_by_code_ifc(section, code_ifc,  db=db)


@router_elements_controller.post("/structured/room/{project_id}", tags=["Management Elements"])
async def create_structured_room_endpoint(project_id: int, request: Request, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Recibe un payload estructurado (con rooms, elements, etc.) y crea los recintos y elementos asociados en la base de datos para un proyecto específico.

    Ejemplo de payload esperado:
    {
        "buildingStructure": [
            {
                "name": "AU",
                "constructionDetails": {
                    "walls": [
                        {"code": "MURO_01", "elements": [{"name": "Muro básico", "material": "MATERIAL_001", ...}]}
                    ],
                    "floors": [ ... ],
                    "ceilings": [ ... ],
                    "doors": [ ... ],
                    "windows": [ ... ]
                }
            },
            ...
        ]
    }
    """
    payload = await request.json()
    return process_structured_payload(payload, current_user, db, project_id)

