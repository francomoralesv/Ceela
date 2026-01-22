from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.pt_table import PTTable


def get_htr_wk_by_project(project_id: int,  db: Session):
    
    enclosures = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.project_id == project_id
    ).all()

    if not enclosures:
        return 0

    total_htr_wk = 0
    for enclosure in enclosures:
        pt_record = db.query(PTTable).filter(
            PTTable.enclosure_id == enclosure.id
        ).first()

        if pt_record and pt_record.total_pt is not None:
            total_htr_wk += pt_record.total_pt

    print(f"Calculo de htr_wk para el proyecto con ID: {project_id} con  valor {total_htr_wk}")
    return total_htr_wk


def get_htr_wk_by_enclosure(project_id: int, db: Session):
    enclosures = db.query(EnclosureGenerals)\
                   .filter(EnclosureGenerals.project_id == project_id)\
                   .all()

    # Si no hay enclosure para ese proyecto, devolvemos dict vacío
    if not enclosures:
        return {}

    resultado = {}
    for enclosure in enclosures:
        pt_record = db.query(PTTable)\
                      .filter(PTTable.enclosure_id == enclosure.id)\
                      .first()
        # Asignamos total_pt o 0 si no existe o es None
        resultado[enclosure.id] = pt_record.total_pt if (pt_record and pt_record.total_pt is not None) else 0.0

    print(f"Detalle de htr_wk para proyecto {project_id}: {resultado}")
    return resultado
