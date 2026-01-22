from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.elements_enclosure.wall_service import create_wall_enclosure, get_wall_enclosures, update_wall_enclosure, delete_wall_enclosure
from src.services.elements_enclosure.window_service import create_window_enclosures, get_window_enclosures, update_window_enclosure, delete_window_enclosure
from src.services.elements_enclosure.door import create_door_enclosure, get_door_enclosures, update_door_enclosure, delete_door_enclosure
from src.services.elements_enclosure.fav import create_fav_enclosure, get_favs_by_enclosure, update_fav, delete_fav
from src.services.elements_enclosure.roof import create_roof_enclosure, get_roof_enclosures, update_roof_enclosure, delete_roof_enclosure
from src.services.elements_enclosure.floor import create_floor_enclosure, get_floor_enclosures, update_floor_enclosure, delete_floor_enclosure
from src.models.schemas.elements_enclosure.wall_enclosure_create import WallEnclosureCreate
from src.models.schemas.elements_enclosure.window_enclosure_create import WindowEnclosureCreate
from src.models.schemas.elements_enclosure.door import DoorEnclosureCreate
from src.models.schemas.elements_enclosure.fav_create import FavCreate
from src.models.schemas.elements_enclosure.roof import RoofEnclosureCreate
from src.models.schemas.elements_enclosure.floor import FloorEnclosureCreate


router_elements_enclosures_controller = APIRouter()

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Wall >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@router_elements_enclosures_controller.post("/wall-enclosures-create/{enclosure_id}", tags=["Elements-Enclosures-Wall"])
def create_wall_enclosure_endpoint(enclosure_id: int, wall: WallEnclosureCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_wall_enclosure(enclosure_id, wall, current_user, db)


@router_elements_enclosures_controller.get("/wall-enclosures/{enclosure_id}", tags=["Elements-Enclosures-Wall"])
def get_wall_enclosure_endpoint(enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_wall_enclosures(enclosure_id, current_user, db)


@router_elements_enclosures_controller.put("/wall-enclosures-update/{wall_id}", tags=["Elements-Enclosures-Wall"])
def update_wall_enclosure_endpoint(wall_id: int, wall: WallEnclosureCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_wall_enclosure(wall_id, wall, current_user, db)


@router_elements_enclosures_controller.delete("/wall-enclosures-delete/{wall_id}", tags=["Elements-Enclosures-Wall"])
def delete_wall_enclosure_endpoint(wall_id: int,  current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_wall_enclosure(wall_id, current_user, db)


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Window >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@router_elements_enclosures_controller.post("/window-enclosures-create/{enclosure_id}", tags=["Elements-Enclosures-Window"])
def create_windows_enclosure_endpoint(enclosure_id: int, window: WindowEnclosureCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_window_enclosures(enclosure_id, window, current_user, db)


@router_elements_enclosures_controller.get("/window-enclosures/{enclosure_id}", tags=["Elements-Enclosures-Window"])
def get_window_enclosure_endpoint(enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_window_enclosures(enclosure_id, current_user, db)


@router_elements_enclosures_controller.put("/window-enclosures-update/{window_id}", tags=["Elements-Enclosures-Window"])
def update_window_enclosure_endpoint(window_id: int, wall: WindowEnclosureCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_window_enclosure(window_id, wall, current_user, db)


@router_elements_enclosures_controller.delete("/window-enclosures-delete/{window_id}", tags=["Elements-Enclosures-Window"])
def delete_window_enclosure_endpoint(window_id: int,  current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_window_enclosure(window_id, current_user, db)


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Door >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
 
@router_elements_enclosures_controller.post("/door-enclosures-create/{enclosure_id}", tags=["Elements-Enclosures-Door"])
def create_door_enclosure_endpoint(enclosure_id: int, door: DoorEnclosureCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_door_enclosure(enclosure_id, door, current_user, db)


@router_elements_enclosures_controller.get("/door-enclosures/{enclosure_id}", tags=["Elements-Enclosures-Door"])
def get_door_enclosure_endpoint(enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_door_enclosures(enclosure_id, current_user, db)


@router_elements_enclosures_controller.put("/door-enclosures-update/{door_id}", tags=["Elements-Enclosures-Door"])
def update_door_enclosure_endpoint(door_id: int, door: DoorEnclosureCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_door_enclosure(door_id, door, current_user, db)


@router_elements_enclosures_controller.delete("/door-enclosures-delete/{door_id}", tags=["Elements-Enclosures-Door"])
def delete_door_enclosure_endpoint(door_id: int,  current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_door_enclosure(door_id, current_user, db)


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@router_elements_enclosures_controller.post("/{type}/fav-enclosures-create/{enclosure_id}/{item_id}", tags=["Elements-Enclosures-Fav"])
def create_fav_enclosure_endpoint(type: str, item_id: int, enclosure_id: int, fav: FavCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_fav_enclosure(type, item_id, enclosure_id, fav, current_user, db)


@router_elements_enclosures_controller.get("/{fav_type}/fav-enclosures/{enclosure_id}/", tags=["Elements-Enclosures-Fav"])
def get_fav_enclosure_endpoint(enclosure_id: int, fav_type: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_favs_by_enclosure(enclosure_id, fav_type, current_user, db)


@router_elements_enclosures_controller.put("/{fav_type}/fav-enclosures-update/{fav_id}", tags=["Elements-Enclosures-Fav"])
def update_fav_enclosure_endpoint(fav_id: int, fav_type: str, fav: FavCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_fav(fav_id, fav_type, fav, current_user, db)


@router_elements_enclosures_controller.delete("/{fav_type}/fav-enclosures-delete/{enclosure_id}/{item_id}", tags=["Elements-Enclosures-Fav"])
def delete_roof_enclosure_endpoint(fav_id: int, fav_type: str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_fav(fav_id, fav_type, current_user, db)

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Roof >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
 
@router_elements_enclosures_controller.post("/roof-enclosures-create/{enclosure_id}", tags=["Elements-Enclosures-Roof"])
def create_roof_enclosure_endpoint(enclosure_id: int, roof: RoofEnclosureCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_roof_enclosure(enclosure_id, roof, current_user, db)


@router_elements_enclosures_controller.get("/roof-enclosures/{enclosure_id}", tags=["Elements-Enclosures-Roof"])
def get_roof_enclosure_endpoint(enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_roof_enclosures(enclosure_id, current_user, db)


@router_elements_enclosures_controller.put("/roof-enclosures-update/{roof_id}", tags=["Elements-Enclosures-Roof"])
def update_roof_enclosure_endpoint(roof_id: int, roof: RoofEnclosureCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_roof_enclosure(roof_id, roof, current_user, db)


@router_elements_enclosures_controller.delete("/roof-enclosures-delete/{roof_id}", tags=["Elements-Enclosures-Roof"])
def delete_roof_enclosure_endpoint(roof_id: int,  current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_roof_enclosure(roof_id, current_user, db)

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Floor >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
 
@router_elements_enclosures_controller.post("/floor-enclosures-create/{enclosure_id}", tags=["Elements-Enclosures-Floor"])
def create_floor_enclosure_endpoint(enclosure_id: int, floor: FloorEnclosureCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_floor_enclosure(enclosure_id, floor, current_user, db)


@router_elements_enclosures_controller.get("/floor-enclosures/{enclosure_id}", tags=["Elements-Enclosures-Floor"])
def get_floor_enclosure_endpoint(enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_floor_enclosures(enclosure_id, current_user, db)


@router_elements_enclosures_controller.put("/floor-enclosures-update/{floor_id}", tags=["Elements-Enclosures-Floor"])
def update_floor_enclosure_endpoint(floor_id: int, floor: FloorEnclosureCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_floor_enclosure(floor_id, floor, current_user, db)


@router_elements_enclosures_controller.delete("/floor-enclosures-delete/{floor_id}", tags=["Elements-Enclosures-Floor"])
def delete_floor_enclosure_endpoint(floor_id: int,  current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_floor_enclosure(floor_id, current_user, db)