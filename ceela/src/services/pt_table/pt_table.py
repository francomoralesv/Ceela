from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.entity.po.po import WallPO, WindowPO, FloorPO
from src.models.entity.pt_table import PTTable

def aggregate_pt_by_enclosure(enclosure_id: int, db: Session) -> PTTable:
    """
    Para un enclosure_id dado:
      - En WallPO se agrupa por 'tipo_muro' y se suma 'pt_lineal' para obtener P01, P02, P03 y P04.
      - En WindowPO se suma 'pt_lineal' (corresponde a P05).
      - En FloorPO se suma 'pt_lineal' (corresponde a P06).
      
    Luego, se calcula:
        total_pt = (P01 + P02 + P03 + P04 + P05 + P06) + pt_piso_prop,
    donde pt_piso_prop se toma directamente de PTTable (o se asume 0 si no existe).
    
    Si ya existe un registro en PTTable para este enclosure_id se actualiza; de lo contrario, se crea uno nuevo.
    """
    # Inicializar variables
    p01 = p02 = p03 = p04 = 0
    p05 = 0
    p06 = 0

    # --- Sumar valores en WallPO (P01 a P04) ---
    wall_results = (
        db.query(WallPO.tipo_muro, func.sum(WallPO.pt_lineal).label("sum_pt"))
          .filter(
              WallPO.enclosure_id == enclosure_id,
              WallPO.tipo_muro.in_(["P01", "P02", "P03", "P04"])
          )
          .group_by(WallPO.tipo_muro)
          .all()
    )
    for tipo_muro, sum_pt in wall_results:
        valor = sum_pt or 0
        if tipo_muro == "P01":
            p01 = valor
        elif tipo_muro == "P02":
            p02 = valor
        elif tipo_muro == "P03":
            p03 = valor
        elif tipo_muro == "P04":
            p04 = valor

    # --- Sumar valores en WindowPO (P05) ---
    window_result = (
        db.query(func.sum(WindowPO.pt_lineal).label("sum_P05"))
          .filter(WindowPO.enclosure_id == enclosure_id)
          .one()
    )
    p05 = window_result.sum_P05 or 0

    # --- Sumar valores en FloorPO (P06) ---
    floor_result = (
        db.query(func.sum(FloorPO.pt_lineal).label("sum_P06"))
          .filter(FloorPO.enclosure_id == enclosure_id)
          .one()
    )
    p06 = floor_result.sum_P06 or 0

    # --- Obtener pt_piso_prop desde PTTable (si existe) ---
    existing_record = (
        db.query(PTTable)
          .filter(PTTable.enclosure_id == enclosure_id)
          .first()
    )
    pt_piso_prop = existing_record.pt_piso_prop if existing_record and existing_record.pt_piso_prop is not None else 0

    # --- Calcular total_pt ---
    total_pt = (p01 + p02 + p03 + p04 + p05 + p06) + pt_piso_prop

    # --- Actualizar o crear registro en PTTable ---
    if existing_record:
        existing_record.P01 = p01
        existing_record.P02 = p02
        existing_record.P03 = p03
        existing_record.P04 = p04
        existing_record.P05 = p05
        existing_record.P06 = p06
        existing_record.total_pt = total_pt
        record = existing_record
    else:
        record = PTTable(
            enclosure_id=enclosure_id,
            P01=p01,
            P02=p02,
            P03=p03,
            P04=p04,
            P05=p05,
            P06=p06,
            pt_piso_prop=pt_piso_prop,
            total_pt=total_pt,
            pt_piso_base=0,
            case="Propuesto"
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return record