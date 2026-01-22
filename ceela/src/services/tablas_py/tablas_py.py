from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.entity.wall import WallEnclosure
from src.models.entity.floor import FloorEnclosure
from src.models.entity.roof import RoofEnclosure
from src.models.entity.door import DoorEnclosure
from src.models.entity.detail_part import DetailPart
from src.models.entity.calculations import Calculation
from src.models.entity.details import Detail
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.elements import Element
from src.models.entity.tabla_py import TablaPy


def get_characteristic_orientation(characteristic: str) -> str:
    mapping = {
        "Interior climatizado": "AD",
        "Interior no climatizado": "IN"
    }
    return mapping.get(characteristic, "")  # Si no se encuentra, retorna cadena vacía


def get_orientation(tipo: str, item_id: int, enclosure_id: int, db: Session) -> str:
    orientation = None

    if tipo == "muro":
        wall = db.query(WallEnclosure).filter(
            WallEnclosure.enclosure_id == enclosure_id,
            WallEnclosure.id == item_id
        ).first()
        if wall:
            # LÓGICA INTELIGENTE: Determinar orientación según características
            # Si es interior, SIEMPRE usar orientación de characteristic (ignorar orientation geográfica)
            # Si es exterior, SIEMPRE usar orientación geográfica de BD

            if wall.characteristics in ["Interior climatizado", "Interior no climatizado"]:
                # Muros interiores: usar orientación especial (AD o IN)
                orientation = get_characteristic_orientation(wall.characteristics)
                print(f"Muro interior: characteristics='{wall.characteristics}' → orientation='{orientation}'")
            else:
                # Muros exteriores: usar orientación geográfica de BD
                orientation = wall.orientation
                print(f"Muro exterior: characteristics='{wall.characteristics}' → orientation='{orientation}'")

    elif tipo == "techo":
        techo = db.query(RoofEnclosure).filter(
            RoofEnclosure.enclosure_id == enclosure_id,
            RoofEnclosure.id == item_id
        ).first()
        if techo:
            # Lógica inteligente para techos
            if techo.characteristic == "Interior no climatizado":
                # Techo interior (ej: techo que da a ático no climatizado)
                orientation = "IN"
                print(f"Techo interior: characteristic='{techo.characteristic}' → orientation='IN'")
            else:
                # Techo exterior (caso común)
                orientation = "HR"
                print(f"Techo exterior: characteristic='{techo.characteristic}' → orientation='HR'")
        else:
            orientation = "HR"

    elif tipo == "piso":
        piso = db.query(FloorEnclosure).filter(
            FloorEnclosure.enclosure_id == enclosure_id,
            FloorEnclosure.id == item_id
        ).first()
        if piso:
            # Lógica inteligente para pisos
            if piso.characteristic == "Interior no climatizado":
                # Piso interior (ej: piso sobre espacio no climatizado)
                orientation = "IN"
                print(f"Piso interior: characteristic='{piso.characteristic}' → orientation='IN'")
            else:
                # Piso exterior: depende si está ventilado o no
                orientation = "CT" if piso.is_ventilated == "No Ventilado" else "FL"
                print(f"Piso exterior: characteristic='{piso.characteristic}', ventilado='{piso.is_ventilated}' → orientation='{orientation}'")

    elif tipo == "door":
        door = db.query(DoorEnclosure).filter(
            DoorEnclosure.enclosure_id == enclosure_id,
            DoorEnclosure.id == item_id
        ).first()
        if door:
            # Lógica inteligente para puertas (similar a muros)
            if door.characteristics in ["Interior climatizado", "Interior no climatizado"]:
                # Puertas interiores
                orientation = get_characteristic_orientation(door.characteristics)
                print(f"Puerta interior: characteristics='{door.characteristics}' → orientation='{orientation}'")
            else:
                # Puertas exteriores
                orientation = door.orientation
                print(f"Puerta exterior: characteristics='{door.characteristics}' → orientation='{orientation}'")

    # Si no se pudo determinar, se asigna un valor por defecto ("ND")
    return orientation if orientation is not None else "ND"


def update_or_create_tabla_py(enclosure_id: int, item_id: int, tipo: str, orientation: str, db: Session):
    """
    Si existe un registro en TablaPy para el mismo enclosure_id, item_id, tipo y orientation,
    se actualiza (o se utiliza para actualizar); de lo contrario, se crea uno nuevo.
    """
    tabla_reg = db.query(TablaPy).filter(
        TablaPy.enclosure_id == enclosure_id,
        TablaPy.item_id == item_id,
        TablaPy.type == tipo,
    ).first()

    if not tabla_reg:
        # Se crea el registro con valores por defecto (0 o cadena vacía) para los campos numéricos/texto.
        tabla_reg = TablaPy(
            enclosure_id=enclosure_id,
            item_id=item_id,
            type=tipo,
            orientation=orientation,
            name="",
            nodos_emisividad=0,
            nodos_area=0,
            r_puro=0,
            emisividad_x_sup=0,
            emisividad=0,
            r_a_atot=0,
        )
        db.add(tabla_reg)
        db.commit()  # Guarda el registro inicial
    else:
        # En modo actualización se puede asignar la orientación y otros campos si fuera necesario.
        tabla_reg.orientation = orientation
    return tabla_reg


def get_similar_tabla_py_records(enclosure_id: int, orientation: str, tipo: str, db: Session):
    """
    Obtiene registros de TablaPy filtrados por enclosure_id, orientation y tipo.
    Si no se encuentran, se retorna la lista con el registro actual para seguir operaciones.
    """
    registros = db.query(TablaPy).filter(
        TablaPy.enclosure_id == enclosure_id,
        TablaPy.orientation == orientation,
        TablaPy.type == tipo
    ).order_by(TablaPy.id.asc()).all()
    if not registros:
        print("Advertencia: No se encontraron registros similares en TablaPy, se usará el registro actual.")
        return []
    return registros


def process_door_type(registros_similares, db: Session):
    """
    Procesa la lógica específica para tipo 'door'. Si no se encuentran datos,
    se retornan valores 0 para continuar las operaciones.
    """
    try:
        door_item_id = registros_similares[-1].item_id if registros_similares else None

        if door_item_id is not None:
            door = db.query(DoorEnclosure).filter(DoorEnclosure.id == door_item_id).first()
        else:
            door = None

        if not door:
            print("Advertencia: Door no encontrado, se asignarán 0 en cálculos.")
            return 0, 0

        element = db.query(Element).filter(
            Element.type == "door",
            Element.id == door.door_id
        ).first()
        if not element:
            print("Advertencia: Elemento door no encontrado en Element, se asignarán 0 en cálculos.")
            return 0, 0

        try:
            r_puro = element.calculations.get("r_puro", 0)
        except Exception as e:
            print(f"Error al procesar cálculos en Element: {e}")
            r_puro = 0

        km_op_total = 0  # Para door, km_op se asigna en 0
        return r_puro, km_op_total
    except Exception as e:
        print(f"Error en process_door_type: {e}")
        return 0, 0


def fetch_detail_info(reg: TablaPy, tipo: str, db: Session):
    """
    Obtiene el registro correspondiente (muro, techo o piso) y retorna el identificador,
    el tipo y el nombre para DetailPart. Si no se encuentra, se retornan valores por defecto.
    """
    try:
        if tipo == "muro":
            rec = db.query(WallEnclosure).filter(WallEnclosure.id == reg.item_id).first()
            if rec:
                name_detail = db.query(DetailPart.name_detail).filter(DetailPart.id == rec.wall_id).scalar() or ""
                return rec.wall_id, "Muro", name_detail
            else:
                print("Advertencia: Muro no encontrado, se asigna 0 y cadena vacía.")
                return 0, "Muro", ""
        elif tipo == "techo":
            rec = db.query(RoofEnclosure).filter(RoofEnclosure.id == reg.item_id).first()
            if rec:
                name_detail = db.query(DetailPart.name_detail).filter(DetailPart.id == rec.roof_id).scalar() or ""
                return rec.roof_id, "Techo", name_detail
            else:
                print("Advertencia: Techo no encontrado, se asigna 0 y cadena vacía.")
                return 0, "Techo", ""
        elif tipo == "piso":
            rec = db.query(FloorEnclosure).filter(FloorEnclosure.id == reg.item_id).first()
            if rec:
                name_detail = db.query(DetailPart.name_detail).filter(DetailPart.id == rec.floor_id).scalar() or ""
                return rec.floor_id, "Piso", name_detail
            else:
                print("Advertencia: Piso no encontrado, se asigna 0 y cadena vacía.")
                return 0, "Piso", ""
        elif tipo == "door":
            return 0, tipo.capitalize(), ""
    except Exception as e:
        print(f"Error en fetch_detail_info: {e}")
        return 0, tipo.capitalize(), ""


def get_detail_part(detail_identifier, detail_type, name_detail, db: Session):
    """
    Consulta DetailPart usando el identificador, el tipo y el nombre.
    Si no se encuentra, se retorna un objeto dummy que contiene los atributos mínimos.
    """
    try:
        detail_part = db.query(DetailPart).filter(
            DetailPart.id == detail_identifier,
            DetailPart.type == detail_type,
            DetailPart.name_detail == name_detail
        ).first()
        if not detail_part:
            print("Advertencia: DetailPart no encontrado, se asigna objeto dummy.")
            return type("DummyDetailPart", (), {"calculations": {}, "info": {}, "name_detail": name_detail})
        return detail_part
    except Exception as e:
        print(f"Error en get_detail_part: {e}")
        return type("DummyDetailPart", (), {"calculations": {}, "info": {}, "name_detail": name_detail})


def sum_detail_calculations(project_id: int, name_detail: str, db: Session) -> float:
    """
    Suma los valores 'r' de todas las Calculation asociadas a los Detail que coincidan.
    Si no se encuentran detalles o cálculos, se retorna 0.
    """
    try:
        details = db.query(Detail).filter(
            Detail.project_id == project_id,
            Detail.name_detail == name_detail
        ).all()
        if not details:
            return 0

        detail_r_puro_sum = 0
        for det in details:
            calculations = db.query(Calculation).filter(
                Calculation.reference_id == det.id,
                Calculation.type == "details"
            ).all()
            for calc in calculations:
                try:
                    detail_r_puro_sum += calc.values.get("r", 0)
                except Exception as e:
                    print(f"Error al procesar cálculo (r): {e}")
        return detail_r_puro_sum
    except Exception as e:
        print(f"Error en sum_detail_calculations: {e}")
        return 0


def process_other_types(registros_similares, enclosure_id: int, tipo: str, db: Session):
    """
    Procesa la lógica para 'muro', 'techo' y 'piso' acumulando r_puro y km_op.
    Si algún dato no se encuentra, se asigna 0 y se continúa la operación.
    """
    total_r_puro = 0
    total_km_op = 0

    # Obtener project_id desde EnclosureGenerals; si no se encuentra, se asigna 0.
    enclosure_record = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.id == enclosure_id
    ).first()
    project_id = enclosure_record.project_id if (enclosure_record and hasattr(enclosure_record, "project_id")) else 0

    for reg in registros_similares:
        detail_identifier, detail_type, name_detail = fetch_detail_info(reg, tipo, db)
        if detail_identifier == 0:
            continue
        detail_part = get_detail_part(detail_identifier, detail_type, name_detail, db)
        try:
            km_op_item = detail_part.calculations.get("km_op", 0)
        except Exception as e:
            print(f"Error al procesar cálculos en DetailPart: {e}")
            km_op_item = 0

        detail_r_puro_sum = sum_detail_calculations(project_id, detail_part.name_detail, db)
        total_r_puro += detail_r_puro_sum
        total_km_op += km_op_item

    return total_r_puro, total_km_op


def calculate_r_a_atot(r_puro: float, registro, km_op_total: float, db: Session):
    """
    Calcula r_a_atot usando la fórmula:
       r_a_atot = r_puro * (área individual) / (suma total de áreas)
    Si km_op_total es 0 o no se encuentra área, se retorna 0.
    """
    if km_op_total == 0:
        return 0

    registros_similares = db.query(TablaPy).filter(
        TablaPy.enclosure_id == registro.enclosure_id,
        TablaPy.orientation == registro.orientation
    ).all()

    total_area = 0
    for reg in registros_similares:
        rec = None
        if reg.type == "muro":
            rec = db.query(WallEnclosure).filter(
                WallEnclosure.id == reg.item_id,
                WallEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "techo":
            rec = db.query(RoofEnclosure).filter(
                RoofEnclosure.id == reg.item_id,
                RoofEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "piso":
            rec = db.query(FloorEnclosure).filter(
                FloorEnclosure.id == reg.item_id,
                FloorEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "door":
            rec = db.query(DoorEnclosure).filter(
                DoorEnclosure.id == reg.item_id,
                DoorEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        if rec and hasattr(rec, "area") and rec.area is not None:
            total_area += rec.area

    if total_area == 0:
        return 0

    rec_ind = None
    if registro.type == "muro":
        rec_ind = db.query(WallEnclosure).filter(
            WallEnclosure.id == registro.item_id,
            WallEnclosure.enclosure_id == registro.enclosure_id
        ).first()
    elif registro.type == "techo":
        rec_ind = db.query(RoofEnclosure).filter(
            RoofEnclosure.id == registro.item_id,
            RoofEnclosure.enclosure_id == registro.enclosure_id
        ).first()
    elif registro.type == "piso":
        rec_ind = db.query(FloorEnclosure).filter(
            FloorEnclosure.id == registro.item_id,
            FloorEnclosure.enclosure_id == registro.enclosure_id
        ).first()
    elif registro.type == "door":
        rec_ind = db.query(DoorEnclosure).filter(
            DoorEnclosure.id == registro.item_id,
            DoorEnclosure.enclosure_id == registro.enclosure_id
        ).first()

    individual_area = rec_ind.area if (rec_ind and hasattr(rec_ind, "area") and rec_ind.area is not None) else 0
    return (r_puro * individual_area / total_area) if total_area else 0


def calculate_total_area_by_orientation(registro, db: Session) -> float:
    """
    Calcula la suma total de áreas para todos los registros en TablaPy con el mismo
    enclosure_id y orientation, considerando solo 'muro', 'techo' y 'piso'.
    """
    registros_similares = db.query(TablaPy).filter(
        TablaPy.enclosure_id == registro.enclosure_id,
        TablaPy.orientation == registro.orientation
    ).all()

    total_area = 0

    def get_individual_area(reg, db):
        rec = None
        if reg.type == "muro":
            rec = db.query(WallEnclosure).filter(
                WallEnclosure.id == reg.item_id,
                WallEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "techo":
            rec = db.query(RoofEnclosure).filter(
                RoofEnclosure.id == reg.item_id,
                RoofEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "piso":
            rec = db.query(FloorEnclosure).filter(
                FloorEnclosure.id == reg.item_id,
                FloorEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "door":
            rec = db.query(DoorEnclosure).filter(
                DoorEnclosure.id == reg.item_id,
                DoorEnclosure.enclosure_id == reg.enclosure_id
            ).first()
            area = rec.broad * rec.high
            return area
        
        return rec.area if (rec and hasattr(rec, "area") and rec.area is not None) else 0

    for reg in registros_similares:
        if reg.type in ("muro", "techo", "piso", "door"):
            total_area += get_individual_area(reg, db)

    return total_area


def calculate_average_emisividad_by_orientation(registro, db: Session) -> float:
    """
    Calcula el promedio de emisividad para todos los registros en TablaPy con el mismo 
    enclosure_id y orientation usando:
         promedio_emisividad = suma_emisividades / suma_total_de_áreas
    Si no hay áreas acumuladas o para registros de tipo 'door', retorna 0.
    """
    registros_similares = db.query(TablaPy).filter(
        TablaPy.enclosure_id == registro.enclosure_id,
        TablaPy.orientation == registro.orientation
    ).all()


    db.flush() 
    def get_individual_area(reg, db):
        rec = None
        if reg.type == "muro":
            rec = db.query(WallEnclosure).filter(
                WallEnclosure.id == reg.item_id,
                WallEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "techo":
            rec = db.query(RoofEnclosure).filter(
                RoofEnclosure.id == reg.item_id,
                RoofEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "piso":
            rec = db.query(FloorEnclosure).filter(
                FloorEnclosure.id == reg.item_id,
                FloorEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "door":
            rec = db.query(DoorEnclosure).filter(
                DoorEnclosure.id == reg.item_id,
                DoorEnclosure.enclosure_id == reg.enclosure_id
            ).first()
            area = rec.broad * rec.high
        
        print("Tipo", type)
        if reg.type == 'door':
            print("Area puerta: ", area)
            return area
        return rec.area if (rec and hasattr(rec, "area") and rec.area is not None) else 0

    def get_surface_value(reg, db):
        try:
            detail_identifier, detail_type, detail_name = fetch_detail_info(reg, reg.type, db)
            if detail_type == 'Door':
                print("Nuevo mensaje nuevo de puerta")
                return 0.9
            detail_part = get_detail_part(detail_identifier, detail_type, detail_name, db)
            return detail_part.info.get("surface_color", {}).get("exterior", {}).get("value", 0)
        except Exception as e:
            print(f"Error al obtener surface_value: {e}")
            return 0

    suma_emisividades = 0
    suma_total_area = 0

    for reg in registros_similares:
        # Fuerza recarga desde la base de datos para reflejar cualquier cambio en orientation
        db.refresh(reg)

        if reg.type in ("muro", "techo", "piso", "door"):
            area_ind = get_individual_area(reg, db)
            if reg.orientation == 'CT':
                surface_value = 0.9
            else:
                surface_value = get_surface_value(reg, db)
            suma_emisividades += surface_value * area_ind
            suma_total_area += area_ind

    return (suma_emisividades / suma_total_area) if suma_total_area else 0


def calculate_emisividades_by_orientation(registro, db: Session) -> list:
    """
    Calcula para el registro de TablaPy la emisividad individual y la suma total de emisividades
    de todos los registros con el mismo enclosure_id y orientation.
    Para 'door' se asigna 0.
    """

    db.flush() 
    
    registros_similares = db.query(TablaPy).filter(
        TablaPy.enclosure_id == registro.enclosure_id,
        TablaPy.orientation == registro.orientation
    ).all()

    def get_individual_area(reg, db):
        rec = None
        if reg.type == "muro":
            rec = db.query(WallEnclosure).filter(
                WallEnclosure.id == reg.item_id,
                WallEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "techo":
            rec = db.query(RoofEnclosure).filter(
                RoofEnclosure.id == reg.item_id,
                RoofEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "piso":
            rec = db.query(FloorEnclosure).filter(
                FloorEnclosure.id == reg.item_id,
                FloorEnclosure.enclosure_id == reg.enclosure_id
            ).first()
        elif reg.type == "door":
            rec = db.query(DoorEnclosure).filter(
                DoorEnclosure.id == reg.item_id,
                DoorEnclosure.enclosure_id == reg.enclosure_id
            ).first()
            area = rec.broad * rec.high
        
        if reg.type == 'door':
            return area
        return rec.area if (rec and hasattr(rec, "area") and rec.area is not None) else 0

    def get_surface_value(reg, db):
        try:
            detail_identifier, detail_type, detail_name = fetch_detail_info(reg, reg.type, db)
            if detail_type == 'Door':
                print("Nuevo mensaje nuevo de puerta")
                return 0.9
            detail_part = get_detail_part(detail_identifier, detail_type, detail_name, db)
            return detail_part.info.get("surface_color", {}).get("exterior", {}).get("value", 0)
        except Exception as e:
            print(f"Error al obtener surface_value en emisividades: {e}")
            return 0

    suma_emisividades = 0
    for reg in registros_similares:
        if reg.type in ("muro", "techo", "piso", "door"):
            area_ind = get_individual_area(reg, db)
            if reg.orientation == 'CT':
                surface_value = 0.9
                print("Entro Surface: 0.9")
            else:
                surface_value = get_surface_value(reg, db)
                print(f"No entro Surface: {surface_value}")
            suma_emisividades += surface_value * area_ind

    current_area = get_individual_area(registro, db)
    current_surface_value = get_surface_value(registro, db)
    emisividad_x_sup = current_surface_value * current_area

    return [
        {"emisividad_x_sup": emisividad_x_sup},
        {"suma_emisividades": suma_emisividades}
    ]


def calculate_tablas_py(tipo: str, item_id: int, enclosure_id: int, db: Session):
    """
    Flujo:
      1. Determinar la orientación del elemento.
      2. Actualizar o crear en TablaPy un registro, según exista o se requiera actualizar.
      3. Filtrar en TablaPy los registros con el mismo enclosure_id, orientation y tipo.
         - Para 'muro', 'techo' y 'piso': se consulta DetailPart y se suman valores de 'r' de Calculation.
         - Para 'door': se procesa de forma especial.
      4. Actualizar el registro en TablaPy con los valores totales de r_puro, km_op, r_a_atot,
         emisividad_x_sup, promedio de emisividad (nodos_emisividad) y el área total (nodos_area).
    """
    if tipo not in ("muro", "techo", "piso", "door"):
        print("Advertencia: Tipo no soportado, se retorna sin procesar.")
        return None

    # 1. Determinar la orientación.
    orientation = get_orientation(tipo, item_id, enclosure_id, db)
    if not orientation:
        orientation = "ND"
        print("Advertencia: No se pudo determinar la orientación, se asigna 'ND'.")

    # 2. Actualizar o crear registro en TablaPy.
    tabla_reg = update_or_create_tabla_py(enclosure_id, item_id, tipo, orientation, db)
    
    # 3. Obtener registros similares. Si no hay, se utiliza el registro actual.
    registros_similares = get_similar_tabla_py_records(enclosure_id, orientation, tipo, db)
    if not registros_similares:
        registros_similares = [tabla_reg]

    # 4. Procesar según el tipo.
    if tipo == "door":
        r_puro, km_op_total = process_door_type(registros_similares, db)
    else:
        r_puro, km_op_total = process_other_types(registros_similares, enclosure_id, tipo, db)

    # Se asigna r_puro calculado
    tabla_reg.r_puro = r_puro

    # Calcular r_a_atot y asignarlo
    tabla_reg.r_a_atot = calculate_r_a_atot(r_puro, tabla_reg, km_op_total, db)

    # Calcular emisividad_x_sup y suma total de emisividades
    emisividades = calculate_emisividades_by_orientation(tabla_reg, db)
    tabla_reg.emisividad_x_sup = emisividades[0].get("emisividad_x_sup", 0)
    print("Emisividades: ", emisividades)
    # Calcular promedio de emisividad y asignarlo
    promedio_emisividad = calculate_average_emisividad_by_orientation(tabla_reg, db)
    tabla_reg.nodos_emisividad = promedio_emisividad
    print("Promedio Emisividad: ", promedio_emisividad)
    # Calcular el área total y asignarla a nodos_area
    total_area = calculate_total_area_by_orientation(tabla_reg, db)
    print("Total Area: ", total_area)
    tabla_reg.nodos_area = total_area

    try:
        db.commit()
    except Exception as e:
        print(f"Error al hacer commit en la base de datos: {e}")
        db.rollback()

    return [emisividades, {"promedio_emisividad": promedio_emisividad, "total_area": total_area}]
