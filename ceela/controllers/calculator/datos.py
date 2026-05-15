import pandas as pd
import os
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.wall import WallEnclosure

#

def get_all_walls_with_layers(db: Session, project_id: int):
    """
    Retrieves all walls with their layers for a given project ID using WallEnclosure and EnclosureGenerals.

    Args:
        db: Database session.
        project_id: The ID of the project to filter walls.

    Returns:
        A list of dictionaries containing wall information and their layers.
    """
    # Query EnclosureGenerals to get all enclosures for the project
    enclosures = db.query(EnclosureGenerals).filter(EnclosureGenerals.project_id == project_id).all()
    walls_with_layers = []
    for enclosure in enclosures:
        walls = db.query(WallEnclosure).filter(WallEnclosure.enclosure_id == enclosure.id).all()
        for wall in walls:
            walls_with_layers.append(wall)

    return walls_with_layers
