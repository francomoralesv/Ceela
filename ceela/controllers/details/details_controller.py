import textwrap
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from src.external.logging import Log
from src.services.database.db_connection import get_db
from src.utils.security.token.jwt_login import verify_token
from src.models.detail_base import DetailBase
from src.models.schemas.details.detail_part_update import DetailPartUpdate
from src.services.details.detail_service import create_detail, update_detail_part_admin, delete_detail_by_admin, create_detail_v2, get_details_v2, get_details, get_project_detail_by_admin, get_all_details_part_project, get_detail_by_id, update_detail, delete_detail, get_details_part_project, update_detail_part, get_all_detail_part_admin

router_controller_details = APIRouter()

@router_controller_details.post("/details/create", tags=["Management Details"])
def create_details_endpoint(detail: DetailBase, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_detail(detail, current_user, db)
  
  
@router_controller_details.post("/{section}/details/create", tags=["Management Details"])
def create_details_v2_endpoint(detail: DetailBase, section: str, project_id: Optional[int] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    Log.save(detail)
    return create_detail_v2(detail, current_user, db, section, project_id)



@router_controller_details.get("/details/", tags=["Management Details"])
def get_details_endpoint(type: Optional[str] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_details(type, current_user, db)


@router_controller_details.get("/{section}/details/", tags=["Management Details"])
def get_details_endpoint_v2(section: str, project_id: Optional[int] = None, type: Optional[str] = None, current_user: dict = Depends(verify_token),  db: Session = Depends(get_db)):
    return get_details_v2(type, current_user, section, project_id, db)


@router_controller_details.get("/details/{detail_id}", tags=["Management Details"])
def get_details_by_id_endpoint(detail_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_detail_by_id(detail_id, current_user, db)
  
  
  

@router_controller_details.get("/details/all/{type}/", tags=["Management Details"])
def get_all_details_by_admin_endpoint(type: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_all_detail_part_admin(type, current_user, db)




@router_controller_details.put("/{section}/details/{detail_id}/update", tags=["Management Details"])
def update_detail_endpoint(detail_id: int, detail: DetailBase, section: str, project_id: Optional[int] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_detail(detail_id, detail, current_user, db, section, project_id)



@router_controller_details.put("/{detail_id}/details/update/{detail_type}", tags=["Management Details"])
def update_detail_part_admin_endpoint(detail_id: int, detail: DetailPartUpdate, detail_type: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_detail_part_admin(detail_type, detail_id, detail, db, current_user)
  

# hd
@router_controller_details.delete("/{section}/{detail_id}/details/delete", tags=["Management Details"])
def delete_detil_admin_endpoint(detail_id: int, section:str, project_id: Optional[int] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_detail_by_admin(current_user, detail_id, db, section, project_id)



@router_controller_details.delete("/{section}/details/{detail_id}/delete", tags=["Management Details"])
def delete_detil_endpoint(detail_id: int, section:str, project_id: Optional[int] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_detail(current_user, detail_id, db, section, project_id)

@router_controller_details.get("/project/{project_id}/details/{type}", tags=["Management Details"])
def get_details_part_endpoint(project_id: int, type: Optional[str] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_details_part_project(type, project_id, current_user, db)
  
  
@router_controller_details.get("/admin/project/{project_id}/details/{type}", tags=["Management Details"])
def get_details_part_endpoint(project_id: int, type: Optional[str] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_details_part_project(type, project_id, current_user, db)
  

@router_controller_details.get("/project/{project_id}/details", tags=["Management Details"])
def get_all_details_part_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_all_details_part_project(project_id, current_user, db)



@router_controller_details.put(
    "/project/{project_id}/update_details/{detail_type}/{detail_id}",
    tags=["Management Details"],
    summary="Actualizar un detalle de un proyecto",
    description=textwrap.dedent("""
Este endpoint permite actualizar un detalle de un proyecto específico según su tipo.

### 📌 Tipos de detalles (detail_type) admitidos:
- **Muro** y **Techo**: Se puede actualizar el color de la superficie (`surface_color`).
- **Piso**: Se pueden actualizar otras propiedades excepto `surface_color`.

### ⚠️ Validaciones:
- Se verifica que el proyecto exista.
- Solo el propietario del proyecto puede modificarlo.
- Se aplica una conversión automática de colores de superficie en muros y techos.

### 📤 Request Body (Ejemplo para **Muro/Techo**):
```json
{
  "info": {
    "surface_color": {
      "interior": {
        "name": "Oscuro"
      },
      "exterior": {
        "name": "Claro"
      }
    }
  }
}
```
### 📤 Request Body (Ejemplo para **Piso**):
```json
{
  "info": {
    "ref_aisl_vertical": {
      "d": 10,
      "e_aisl": 5,
      "lambda": 0.035
    },
    "ref_aisl_horizontal": {
      "d": 15,
      "e_aisl": 7,
      "lambda": 0.04
    }
  }
}
```
""")
)
def update_detail_part_endpoint(detail_type: str, project_id: int, detail_id: int, detail_update: DetailPartUpdate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_detail_part(detail_type, project_id, detail_id, detail_update, db, current_user)