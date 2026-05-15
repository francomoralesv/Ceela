from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.security.token.jwt_login import verify_token
from src.services.database.db_connection import get_db
from src.services.elements_enclosure.thermal_bridges_wall import create_thermal_bridge_wall, get_thermal_bridge_walls, update_thermal_bridge_wall, delete_thermal_bridge_wall
from src.models.entity.thermal_bridges import ThermalBridgeWall
from src.models.schemas.thermal_bridges.thermal_bridges_create import ThermalBridgeWallCreate


router_thermals_bridges_controller = APIRouter()


@router_thermals_bridges_controller.post("/thermal-bridge-create/{enclosure_id}", tags=["Thermal-Bridge-Wall"])
def create_thermal_bridge_wall_endpoint(enclosure_id: int, bridge_wall: ThermalBridgeWallCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return create_thermal_bridge_wall(enclosure_id, bridge_wall, current_user, db)


@router_thermals_bridges_controller.get("/thermal-bridge/{enclosure_id}", tags=["Thermal-Bridge-Wall"])
def get_thermal_bridge_wall_endpoint(enclosure_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return get_thermal_bridge_walls(enclosure_id, current_user, db)



@router_thermals_bridges_controller.put("/thermal-bridge-update/{wall_id}", tags=["Thermal-Bridge-Wall"])
def update_thermal_bridge_wall_endpoint(wall_id: int, bridge_wall: ThermalBridgeWallCreate, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return update_thermal_bridge_wall(wall_id, bridge_wall, current_user, db)



@router_thermals_bridges_controller.delete("/thermal-bridge-delete/{wall_id}", tags=["Thermal-Bridge-Wall"])
def delete_thermal_bridge_wall_endpoint(wall_id: int, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    return delete_thermal_bridge_wall(wall_id, current_user, db)



