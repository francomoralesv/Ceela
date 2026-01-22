from typing import Union
from fastapi import HTTPException
from src.models.entity.thermal_bridges import ThermalBridgeWall
from src.models.entity.wall import WallEnclosure
from src.models.entity.door import DoorEnclosure
from src.models.entity.roof import RoofEnclosure
from src.models.entity.window import WindowEnclosure
from src.models.entity.floor import FloorEnclosure
from src.models.entity.caso_base import CasoBase
from sqlalchemy.orm import Session


def create_caso_base(
    enclosure: Union[WallEnclosure, DoorEnclosure, RoofEnclosure, WindowEnclosure, FloorEnclosure],
    db: Session
):
    item_id = 0
    data = {}
    type = None
    enclosure_id = enclosure.enclosure_id

    if isinstance(enclosure, WallEnclosure):
        type = "wall"
        item_id = enclosure.id

        # Si existe, actualizar en lugar de crear nuevo
        caso_existente = db.query(CasoBase).filter_by(type="wall", item_id=item_id).first()
        if caso_existente:
            print(f"[INFO] Ya existe un CasoBase para muro con item_id={item_id}, se reemplazará.")
            db.delete(caso_existente)
            db.commit()

        data = {
            "name": "Muro Base",
            "angulo_azimut": enclosure.angulo_azimut,
            "area": enclosure.area,
            "orientacion": enclosure.orientation,
        }

        # Verificar si hay puente térmico
        print("YA CASI")
        bridge = db.query(ThermalBridgeWall).filter_by(wall_id=item_id).first()
        print('WALL_ID', item_id)
        if bridge:
            print("ENTRO")
            data["thermal_bridge"] = {
                "po1": {"length": bridge.po1_length, "element": "Muro Base"},
                "po2": {"length": bridge.po2_length, "element": "Muro Base"},
                "po3": {"length": bridge.po3_length, "element": "Muro Base"},
                "po4": {
                    "length": bridge.po4_length,
                    "element": "Muro Base",
                    "e_aislacion": bridge.po4_e_aislacion
                },
                "enclosure_id": bridge.enclosure_id
            }

    elif isinstance(enclosure, DoorEnclosure):
        type = "door"
        item_id = enclosure.id
        data = {
            "name": "P Base",
            "angulo_azimut": enclosure.angulo_azimut,
            "alto": enclosure.high,
            "ancho": enclosure.broad,
            "orientacion": enclosure.orientation,
        }

    elif isinstance(enclosure, RoofEnclosure):
        type = "roof"
        item_id = enclosure.id
        data = {
            "name": "Techo Base",
            "area": enclosure.area,
        }

    elif isinstance(enclosure, WindowEnclosure):
        type = "window"
        item_id = enclosure.id
        data = {
            "name": "V Base",
            "angulo_azimut": enclosure.angulo_azimut,
            "alto": enclosure.high,
            "ancho": enclosure.broad,
            "con_retorno": "Sin",
            "housed_in": "Muro Base",
            "orientacion": enclosure.orientation,
            "tipo_cierre": enclosure.clousure_type
        }

    elif isinstance(enclosure, FloorEnclosure):
        type = "floor"
        item_id = enclosure.id
        data = {
            "name": "Piso Base",
            "parameter": enclosure.parameter,
            "area": enclosure.area,
            "es_ventilado": "Ventilado",
            "po6": enclosure.po6_l
        }

    else:
        raise ValueError("Tipo de enclosure no válido")

    # Crear nuevo CasoBase (o reemplazado si era muro)
    caso_base = CasoBase(
        type=type,
        characteristic='Exterior',
        item_id=item_id,
        enclosure_id=enclosure_id,
        data=data
    )

    db.add(caso_base)
    db.commit()
    db.refresh(caso_base)
    print(f"[OK] CasoBase {'reemplazado' if type == 'wall' and caso_existente else 'creado'} para {type} con ID {caso_base.id}")







def obtener_casos_base_filtrados(enclosure_id: int, db: Session, type: str = None):
    query = db.query(CasoBase).filter(CasoBase.enclosure_id == enclosure_id)

    if type:
        query = query.filter(CasoBase.type == type)

    casos = query.all()

    if not casos:
        raise HTTPException(status_code=404, detail="No se encontraron CasoBase con los filtros proporcionados")
    
    return casos




def eliminar_caso_base_por_type_y_item(type: str, item_id: int, db: Session):
    caso = db.query(CasoBase).filter(
        CasoBase.type == type,
        CasoBase.item_id == item_id
    ).first()

    if not caso:
        raise ValueError(f"No se encontró el CasoBase con type '{type}' y item_id '{item_id}'")
    
    db.delete(caso)
    db.commit()
    
    print(f"CasoBase eliminado: type={type}, item_id={item_id}")