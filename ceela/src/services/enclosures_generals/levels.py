from sqlalchemy.orm import Session
from src.models.entity.levels  import Level


def get_levels(db: Session, current_user: dict):
    levels = db.query(Level).all()
    return levels

