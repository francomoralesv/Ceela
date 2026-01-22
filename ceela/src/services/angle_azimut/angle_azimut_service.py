from sqlalchemy.orm import Session
from src.models.entity.constant import Constant

def get_angulos_azimut(current_user: dict, db: Session):
    azimut = db.query(Constant).filter(
        Constant.type == "orientation",
        Constant.name == "Azimut Table"
    ).first()
    
    orientations = azimut.atributs["orientations"]
    angles = []
    
    for angulo in orientations:
        angles.append(angulo["range_az"])
        
    return angles


def get_angulos_azimut_and_orientation(current_user: dict, db: Session):
    azimut = db.query(Constant).filter(
        Constant.type == "orientation",
        Constant.name == "Azimut Table"
    ).first()
    
    orientations = azimut.atributs["orientations"]
    angles = []
    
    for angulo in orientations:
        angles.append({"range_az": angulo["range_az"], "orientation": angulo["orientation"]})
        
    return angles