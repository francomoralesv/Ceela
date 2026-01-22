import textwrap
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from typing import Optional
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.enclosures.enclosures_services import get_enclosures, create_enclosure_typology, \
    update_building_condition, get_building_conditions_week_details, delete_enclosure_typing, get_enclosure_by_id, \
    clone_enclosures_for_user, get_enclosure_by_code, get_enclosure_ventilation_flows_by_id, get_typing_enclosure_by_id
from src.models.schemas.enclosures.enclosure_create import EnclosureCreate
from src.models.schemas.building_conditions.building_conditions_create import BuildingConditionCreate

router_enclosures_controller = APIRouter()


@router_enclosures_controller.get("/{section}/enclosures-typing/", tags=["Management Enclosures"], summary="Obtener recintos con condiciones de construcción", 
            description="""
### 📌 Descripción  
Este endpoint permite obtener una lista de recintos (**enclosures**) junto con sus **condiciones de construcción**.  

🔹 **Filtrado opcional por tipo (`type`)**  
Puedes filtrar por el tipo de condición de construcción:  
- `ventilation_flows`: Ventilación y caudales  
- `lightning`: Iluminación  
- `internal_loads`: Cargas internas  
- `schedule_weather`: Horario y clima 

⚠️ **Nota:** Si no se proporciona un `type`, se devolverán todas las condiciones de construcción disponibles para cada recinto.
"""
)
def get_enclosures_endpoint(section: str, type: Optional[str] = None, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_enclosures(section, type, current_user, db)



@router_enclosures_controller.get(
    "/{section}/enclosure-typing/{enclosure_typing_id}", tags=["Management Enclosures"],
    response_model=dict,
    summary="Obtener un recinto por ID",
    description=textwrap.dedent("""
    Recupera la información detallada de un recinto (enclosure) a partir de su ID. 
    Incluye sus condiciones de construcción (`building_conditions`) asociadas.

    ### **Parámetros:**
    - **enclosure_typing_id (int)**: ID del tipo de recinto a consultar.

    ### **Retorna:**
    - **200 OK**: Diccionario con la información del recinto y sus condiciones de construcción.
    - **404 Not Found**: Si el recinto no existe o ha sido eliminado.

    ### **Ejemplo de Respuesta Exitosa:**
    ```json
    {
        "id": 1,
        "code": "ENC-001",
        "created_status": "created",
        "is_deleted": false,
        "building_conditions": [
            {
                "id": 10,
                "enclosure_id": 1,
                "type": "ventilation",
                "created_status": "created",
                "details": {"flow_rate": 120, "ventilation_type": "natural"}
            }
        ]
    }
    ```
    """)
)
def get_enclosure_by_id_endpoint(enclosure_typing_id: int, section: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_enclosure_by_id(enclosure_typing_id, section, current_user, db)



@router_enclosures_controller.post("/{section}/enclosures-typing-create/", tags=["Management Enclosures"],
    description = textwrap.dedent("""
    **📌 Crea un nuevo recinto (Enclosure)**

    **✅ Ejemplo de Respuesta Exitosa:**
    ```json
    {
      "message": "Recinto creado exitosamente",
      "id": "123",
      "code": "AB"
    }
    ```

    **🔄 Relación con las Condiciones de Construcción:**
    - Este endpoint **crea el recinto** y agrega automáticamente condiciones de construcción por defecto..
    - El frontend debe usar el `id` del recinto para **asociar posteriormente** las condiciones de construcción.
    """
    )
)
def create_enclosure_typology_endpoint(enclosure: EnclosureCreate, section: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_enclosure_typology(enclosure, section, current_user, db)




@router_enclosures_controller.patch("/building_condition/{enclosure_id}/update", tags=["Management Enclosures"],
    summary="Actualizar una condición de construcción",
    description=textwrap.dedent("""
    Permite actualizar una condición de construcción dentro de todo el campo del usuario en un recinto.

    ⚠️ Nota: Esta operación no actualiza el tipo de recinto dentro de un proyecto, solo las condiciones de construccion. Para ello, habrá un endpoint específico.
    

    **📌 Parámetros:**
    - `type`: Tipo de condición a actualizar (ej. "ventilation_flows", "lightning", "internal_loads", "schedule_weather").
    - `updates`: Datos que se desean actualizar.
    - `enclosure_id`: ID del recinto a modificar.

    ---
    **📌 Ejemplos de solicitud JSON:**

    🔹 **Ejemplo 1: Actualizar ventilación (`ventilation_flows`)**
    - `enclosure_id`: 12
    ```json
    {
        "type": "ventilation_flows",
        "attributes": {
            "cauldal_min_salubridad": {
                "ida": "IDA2",
                "ocupacion": "Sedentario"
            },
            "caudal_impuesto": {
                "vent_noct": 0.0
            },
            "infiltraciones": 0.5,
            "recuperador_calor": 0
        }
    }
    ```

    🔹 **Ejemplo 2: Actualizar iluminación (`lightning`)**
    - `enclosure_id`: 5
    ```json
    {
        "type": "lightning",
        "attributes": {
            "potencia_base": 8.0,
            "estrategia": "Sin estrategia"
        }
    }
    ```

    🔹 **Ejemplo 3: Actualizar cargas internas (`internal_loads`)**
    - `enclosure_id`: 8
    ```json
    {
        "type": "internal_loads",
        "attributes": {
            "usuarios": 0.0,
            "calor_latente": 0.0,
            "calor_sensible": 0.0,
            "equipos": 0.0,
            "horario": {
                "funcionamiento_semanal": "5x2",
                "laboral": {
                    "inicio": 8,
                    "fin": 18
                }
            }
        }
    }
    ```

    🔹 **Ejemplo 4: Actualizar horario y clima (`schedule_weather`)**
    - `enclosure_id`: 3
    ```json
    {
        "type": "schedule_weather",
        "attributes": {
            "recinto": {
                "climatizado": "No",
                "desfase_clima": 0
            }
        }
    }
    ```

    ---
    **📌 Respuesta esperada:**
    ```json
    {
        "message": "ventilation_flows actualizado correctamente"
    }
    ```
    """

    )
)
def update_building_condition_endpoint(updates: BuildingConditionCreate, section: str, enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_building_condition(updates, enclosure_id, section, current_user, db)




@router_enclosures_controller.delete("/enclosures-typing/{enclosures_id}/delete", tags=["Management Enclosures"],
    summary="Eliminar tipología de recinto",
    description="Este endpoint elimina una tipología de recinto, eliminando asi las condiciones de construccion asociadas."
)
def delete_enclosures_endpoint(enclosures_id, section: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_enclosure_typing(enclosures_id, section, current_user, db)



@router_enclosures_controller.post("/enclosures/clone", tags=["Management Enclosures"], summary="Clonar recintos globales para el usuario")
def clone_enclosure_endpoint(db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    return clone_enclosures_for_user(db, current_user)



@router_enclosures_controller.get("/enclosures/{enclosure_id}/weekly-building-conditions", tags=["Management Enclosures"])
def get_building_conditions_week_details_endpoint(enclosure_id: int, section: str, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    return get_building_conditions_week_details(enclosure_id, section, db, current_user)


@router_enclosures_controller.get(
    "/enclosure-typing/by-code/{code}", 
    tags=["Management Enclosures"],
    response_model=dict,
    summary="Obtener un recinto por código",
    description=textwrap.dedent("""
    Recupera la información detallada de un recinto (enclosure) a partir de su código. 
    Incluye sus condiciones de construcción (`building_conditions`) asociadas.

    ### **Parámetros:**
    - **code (str)**: Código del recinto a consultar.
    - **section (str)**: Sección donde se encuentra el recinto.

    ### **Retorna:**
    - **200 OK**: Diccionario con la información del recinto y sus condiciones de construcción.
    - **404 Not Found**: Si el recinto no existe o ha sido eliminado.

    ### **Ejemplo de Respuesta Exitosa:**
    ```json
    {
        "id": 1,
        "code": "ENC-001",
        "created_status": "created",
        "is_deleted": false,
        "building_conditions": [
            {
                "id": 10,
                "enclosure_id": 1,
                "type": "ventilation",
                "created_status": "created",
                "details": {"flow_rate": 120, "ventilation_type": "natural"}
            }
        ]
    }
    ```
    """)
)
def get_enclosure_by_code_endpoint(code: str,  current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_enclosure_by_code(code,  current_user, db)




@router_enclosures_controller.get(
    "/enclosure-typing/{enclosure_id}/ventilation-flows",
    tags=["Management Enclosures"],
    response_model=dict,
    summary="Obtener ventilación y caudales de un recinto por ID",
    description="Recupera los datos de ventilación y caudales asociados a un recinto (enclosure) por su ID."
)
def get_enclosure_ventilation_flows_by_id_endpoint(enclosure_id: int, type: str, db: Session = Depends(get_db)):
    return get_enclosure_ventilation_flows_by_id(enclosure_id, type, db)

@router_enclosures_controller.get(
    "/enclosure-typing-detail/{enclosure_typing_id}", tags=["Management Enclosures"],
    response_model=dict,
    summary="Obtener detalle de una tipologia de recinto",
)
def get_enclosure_by_id_endpoint(enclosure_typing_id: int,  db: Session = Depends(get_db)):
    return get_typing_enclosure_by_id(enclosure_typing_id,  db)