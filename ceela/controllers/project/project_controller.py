import textwrap
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Optional
from src.services.database.db_connection import get_db
from src.models.schemas.projects.project_create import ProjectCreate
from src.models.schemas.projects.projects_update import ProjectUpdate
from src.services.project.project_service import create_project, list_projects, update_project_status, delete_project, update_current_user_project, get_project_by_id, add_material_to_project, add_details_to_project, add_elements_door_to_project, add_elements_windows_to_project, add_enclosure_type_to_project
from src.utils.security.token.jwt_login import verify_token
from src.models.schemas.projects.projects_update import ProjectStatus
from src.services.constants.constants_service import get_project_constants
from src.services.details.detail_service import get_project_detail
from src.services.elements.elements import get_project_elements
from src.services.constants.constants_service import delete_parameter_in_project
from src.services.enclosures.enclosures_services import get_enclosure_type_from_project



router_project_controller = APIRouter()



# Endpoint para obtener proyectos
@router_project_controller.get("/{section}/projects/", tags=["Management Projects"], 
                               description=""" 
                               - **Admin**: Lista todos los proyectos de todos los usuarios.
                               - **Usuario**: Lista solo sus propios proyectos.
                               """)
def get_projects_endpoint(section: str, value: Optional[str] = None, limit: int = 5, num_pag: int = 1, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return list_projects(section, value, limit, num_pag, current_user, db)


@router_project_controller.get("/projects/{project_id}", tags=["Management Projects"], 
                               description=""" 
                               - **Admin**: Puede obtener cualquier proyecto.
                               - **Usuario**: Puede obtener solo el proyecto relacionado a su id.
                               """)
def get_projects_by_id(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_project_by_id(current_user, project_id, db)



@router_project_controller.get("/projects/{project_id}/constants", tags=["Management Projects"])
def get_project_constants_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_project_constants(current_user, project_id, db)




@router_project_controller.post("/projects/{project_id}/constants/select", tags=["Management Projects"])
def add_materials(project_id: int, constants_ids: list[int] = Body(), current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return add_material_to_project(project_id, constants_ids, current_user, db)




@router_project_controller.get("/projects/{project_id}/details", tags=["Management Projects"])
def get_project_details_endpoint(project_id: int, type: Optional[str] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_project_detail(type, project_id, current_user, db)




@router_project_controller.post("/projects/{project_id}/details/select", tags=["Management Projects"])
def add_details(project_id: int, details_ids: list[int] = Body(), current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return add_details_to_project(project_id, details_ids, current_user, db)




@router_project_controller.get("/projects/{project_id}/elements", tags=["Management Projects"])
def get_project_elements_endpoint(project_id: int, type: Optional[str] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_project_elements(type, project_id, current_user, db)




@router_project_controller.post("/projects/{project_id}/elements/windows/select", tags=["Management Projects"])
def add_elements_windows(project_id: int, windows_ids: list[int] = Body(), current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return add_elements_windows_to_project(project_id, windows_ids, current_user, db)




@router_project_controller.post("/projects/{project_id}/elements/doors/select", tags=["Management Projects"])
def add_elements_door(project_id: int, doors_ids: list[int] = Body(), current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return add_elements_door_to_project(project_id, doors_ids, current_user, db)




@router_project_controller.post("/projects/{project_id}/enclosure-type/select", tags=["Management Projects"])
def add_enclosures_type_endpoint(project_id: int, enclosure_ids: list[int] = Body(), current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return add_enclosure_type_to_project(project_id, enclosure_ids, current_user, db)



@router_project_controller.get("/projects/{project_id}/enclosures-type", tags=["Management Projects"])
def get_project_enclosures_type_endpoint(project_id: int, type: Optional[str] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_enclosure_type_from_project(type, project_id, current_user, db)



# Endpoint para crear un proyecto
@router_project_controller.post("/projects/create", tags=["Management Projects"], 
                                description="Crea un nuevo proyecto.")
def create_project_endpoint(project: ProjectCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_project(current_user, project, db)



# Endpoint para actualizar el estado de un proyecto
@router_project_controller.put("/project/{project_id}/status", tags=["Management Projects"], 
                               description=""" 
                               - **Admin**: Puede cambiar el estado del proyecto.
                               - **Usuario**: No tiene permisos para realizar esta acción.
                               """)
def update_project_status_endpoint(project_id: int, new_status: ProjectStatus, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_project_status(project_id, new_status, current_user, db)



# Endpoint para actualizar un proyecto del usuario
@router_project_controller.put("/my-projects/{project_id}/update", tags=["Management Projects"], 
                               description="- **Usuario**: Puede actualizar su propia información del proyecto.")
def update_current_user_project_endpoint(project_id: int, project_update: ProjectUpdate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_current_user_project(project_id, project_update, current_user, db)



# Endpoint para eliminar un proyecto
@router_project_controller.delete("/project/{project_id}/delete", tags=["Management Projects"], 
                                  description=""" 
                                  - **Usuario**: Puede borrar su propio proyecto.
                                  - **Admin**: Puede borrar cualquier proyecto.
                                  """)
def delete_project_endpoint(project_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_project(project_id, current_user, db)



@router_project_controller.delete(
    "/project/{project_id}/{type}/{reference_id}",
    tags=["Management Projects"],
    summary="Eliminar un parámetro del proyecto",
    description=textwrap.dedent("""
    **Elimina un parámetro específico de un proyecto.**

    🚀 **Funcionamiento:**  
    - Verifica que el usuario tenga permisos sobre el proyecto.  
    - Busca la relación entre el proyecto y el elemento referenciado (`reference_id`).  
    - Si existe, lo elimina de la base de datos.  
    - Si no existe, retorna un error 404.  

    🔒 **Restricciones:**  
    - Solo el propietario del proyecto puede eliminar parámetros.  
    - Si el `reference_id` no existe en el proyecto, la solicitud será rechazada.  

    📌 **Parámetros:**  
    - `project_id` (int): ID del proyecto del que se quiere eliminar un parámetro.  
    - `type` (str): Tipo del parámetro a eliminar. Debe ser uno de los siguientes valores:  
      - `"materials"` → Materiales utilizados en el proyecto.  
      - `"details"` → Detalles adicionales del proyecto.  
      - `"elements"` → Elementos estructurales o componentes del proyecto.  
    - `reference_id` (int): ID del elemento dentro del proyecto que se quiere eliminar.  
      - **Nota:** El `reference_id` debe corresponder a un elemento del tipo indicado en `type`.  
        - Ejemplo: Si `type = "materials"`, entonces `reference_id` debe ser el ID de un material registrado en el proyecto. 

    📤 **Respuestas:**  
    - ✅ `200`: Eliminación exitosa.  
    - ❌ `403`: No tienes permisos para modificar este proyecto.  
    - ❌ `404`: El objeto no se encontró en el proyecto.  
    - ❌ `500`: Error interno del servidor.  

    📘 **Ejemplo de uso:**  
    ```bash
    DELETE /project/1/materials/12
    DELETE /project/2/details/5
    DELETE /project/3/elements/8
    ```
    """
    )
)
def delete_parameter_endpoint(project_id: int, reference_id: int, type: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_parameter_in_project(project_id, reference_id, type, current_user, db)