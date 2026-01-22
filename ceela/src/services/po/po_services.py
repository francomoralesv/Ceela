from sqlalchemy.orm import Session
from sqlmodel import select, func
from src.models.entity.wall import WallEnclosure
from src.models.entity.window import WindowEnclosure
from src.models.entity.floor import FloorEnclosure
from src.models.entity.thermal_bridge_general import ThermalBridge
from src.models.entity.thermal_bridges import ThermalBridgeWall
from src.models.entity.po.po import WallPO, WindowPO, FloorPO
from src.models.entity.detail_part import DetailPart
from src.models.entity.elements import Element
from src.models.entity.pt_table import PTTable
from src.services.pt_table.pt_table import aggregate_pt_by_enclosure
from src.services.tablas_py.tablas_py import calculate_tablas_py
from src.models.entity.enclosure_general import EnclosureGenerals
from sqlalchemy import cast, Integer

def format_esp(esp: float) -> str:
    """
    Devuelve una representación sin decimales si esp es entero o cero.
    """
    if esp == 0 or esp.is_integer():
        return str(int(esp))
    return str(esp)

def thermal_bridges_wall(wall: WallEnclosure, db: Session):
    print(f"Iniciando thermal_bridges_wall para wall.id: {wall.id}")

    original_wall = db.query(DetailPart).filter(DetailPart.id == wall.wall_id).first()
    if not original_wall:
        raise Exception("Muro original no encontrado")
    name_wall = original_wall.name_detail or "0"
    orientation = wall.orientation or "0"
    categoria_muro_1 = str(original_wall.calculations.get("cat_ceeup", "0"))

    try:
        esp_val = float(original_wall.calculations.get("espesor_aislacion", 0))
    except:
        esp_val = 0.0
    esp1 = esp_val / 100
    esp2 = round(esp1, 2) if esp1 and esp1 < 0.2 else (0.2 if esp1 else 0.0)
    esp2_str = format_esp(esp2)

    posicion1 = "sa" if esp1 < 0.01 else str(original_wall.calculations.get("position_insulation", "0"))

    po_fields = {
        "P01": ("po1_length", "po1_id_element"),
        "P02": ("po2_length", "po2_id_element"),
        "P03": ("po3_length", "po3_id_element"),
        "P04": ("po4_length", "po4_id_element"),
    }

    thermal_bridges = db.query(ThermalBridgeWall).filter(ThermalBridgeWall.wall_id == wall.id).all()

    espacio_cont = wall.characteristics or "0"
    factor = 1 if espacio_cont == 'Exterior' else 0 if espacio_cont == "Inter Recintos Clim" else 0.6 if espacio_cont == "Inter Recintos No Clim" else 0

    existing = db.query(WallPO).filter(WallPO.enclosure_id == wall.enclosure_id, WallPO.wall_id == wall.id).all()
    existing_by_tipo = {}
    for rec in existing:
        existing_by_tipo.setdefault(rec.tipo_muro, []).append(rec)

    wall_po_list = []
    cache = {}

    for tb in thermal_bridges:
        for tipo_po, (len_field, id_field) in po_fields.items():
            try:
                longitud_pt = getattr(tb, len_field) or 0
                id_elem2 = getattr(tb, id_field) or 0

                pos_use = posicion1
                pos2 = None
                if tipo_po == "P04":
                    if posicion1.lower() == "ce":
                        pos2 = "ce"
                    elif posicion1.lower() in ["ci", "cm"]:
                        pos2 = "ce"
                    elif posicion1.lower() == "sa":
                        pos2 = "sa"
                    else:
                        pos2 = posicion1
                    pos_use = pos2

                if id_elem2 == 0:
                    cat2 = "0"
                    codigo_pt = f"{tipo_po}.{categoria_muro_1.upper()}.{cat2}.{pos_use.upper()}.{esp2_str}"
                    pt = 0
                    pt_lineal = 0
                else:
                    if id_elem2 not in cache:
                        cache[id_elem2] = db.query(DetailPart).filter(DetailPart.id == id_elem2).first()
                    elem2 = cache[id_elem2]
                    cat2 = str(elem2.calculations.get("cat_ceeup", "0")) if elem2 else "0"
                    codigo_pt = f"{tipo_po}.{categoria_muro_1.upper()}.{cat2.upper()}.{pos_use.upper()}.{esp2_str}"
                    pt = db.query(ThermalBridge.value_pt).filter(ThermalBridge.code_pt == codigo_pt).scalar() or 0
                    pt_lineal = longitud_pt * pt * factor

                data = {
                    "enclosure_id": wall.enclosure_id,
                    "tipo_muro": tipo_po,
                    "nombre": name_wall,
                    "orientacion": orientation,
                    "longitud_pt": longitud_pt,
                    "categoria_1": categoria_muro_1,
                    "categoria_2": cat2,
                    "posicion_aislamiento_1": posicion1,
                    "e_aislamient0_1": esp1,
                    "e_aislamiento_2": esp2,
                    "codigo_pt": codigo_pt,
                    "pt": pt,
                    "pt_lineal": pt_lineal,
                    "espacio_contiguo": espacio_cont,
                    "wall_id": wall.id
                }
                if tipo_po == "P04":
                    data["posicion_aislamiento_2"] = pos2

                if tipo_po in existing_by_tipo:
                    for rec in existing_by_tipo[tipo_po]:
                        for k, v in data.items():
                            setattr(rec, k, v)
                        if tipo_po == "P04":
                            rec.posicion_aislamiento_2 = pos2
                        wall_po_list.append(rec)
                else:
                    new = WallPO(**{k:v for k,v in data.items() if k not in ("posicion_aislamiento_2",)})
                    if tipo_po == "P04":
                        setattr(new, "posicion_aislamiento_2", pos2)
                    db.add(new)
                    wall_po_list.append(new)
            except Exception:
                continue

    db.commit()
    aggregate_pt_by_enclosure(wall.enclosure_id, db)
    calculate_tablas_py("muro", wall.id, wall.enclosure_id, db)
    return wall_po_list


def thermal_bridges_window(window: WindowEnclosure, db: Session):
    print(f"Iniciando thermal_bridges_window para window.id: {window.id}")

    original_win = db.query(Element).filter(Element.id == window.window_id, Element.type == "window").first()
    if not original_win:
        raise Exception("Ventana original no encontrada")

    tipo = original_win.name_element or "0"
    orientation = window.orientation or "0"
    altura = window.high or 0
    ancho = window.broad or 0

    housed_in = window.housed_in or 0
    muro_asoc = db.query(DetailPart).filter(DetailPart.id == housed_in).first()
    if not muro_asoc:
        raise Exception("Muro asociado no encontrado")

    alojado_en = muro_asoc.name_detail or "0"
    cat_muro = str(muro_asoc.calculations.get("cat_ceeup", "0"))
    cat_vent = "VI"

    try:
        esp_val = float(muro_asoc.calculations.get("espesor_aislacion", 0))
    except:
        esp_val = 0.0
    esp1 = esp_val / 100 if esp_val else 0.0
    esp2 = round(esp1, 2) if esp1 and esp1 < 0.2 else (0.2 if esp1 else 0.0)
    esp2_str = format_esp(esp2)

    pos1 = "sa" if esp1 < 0.01 else str(muro_asoc.calculations.get("position_insulation", "0"))
    retorno = window.with_no_return or "0"
    pos_vid = window.position or "0"

    codigo_pt = f"P05.{cat_muro.upper()}.{cat_vent}.{pos1.upper()}.{esp2_str}.{retorno.capitalize()}.{pos_vid.capitalize()}"
    pt = db.query(ThermalBridge.value_pt).filter(ThermalBridge.code_pt == codigo_pt).scalar() or 0

    espacio_cont = window.characteristics or "0"
    factor = 1 if espacio_cont == 'Exterior' else 0 if espacio_cont == "Inter Recintos Clim" else 0.6 if espacio_cont == "Inter Recintos No Clim" else 0
    pt_lineal = pt * (2 * ancho + 2 * altura) * factor

    existing = db.query(WindowPO).filter(WindowPO.enclosure_id == window.enclosure_id, WindowPO.window_id == window.id).first()
    attrs = {
        "enclosure_id": window.enclosure_id,
        "tipo": tipo,
        "hosted_in": alojado_en,
        "orientacion": orientation,
        "altura": altura,
        "ancho": ancho,
        "categoria_muro": cat_muro,
        "categoria_ventana": cat_vent,
        "posicion_aislamiento": pos1,
        "e_aislamient0_1": esp1,
        "e_aislamiento_2": esp2,
        "retorno": retorno,
        "posicion_vidrio": pos_vid,
        "codigo_pt": codigo_pt,
        "pt": pt,
        "pt_lineal": pt_lineal,
        "espacio_contiguo": espacio_cont
    }
    if existing:
        for k,v in attrs.items():
            setattr(existing, k, v)
        window_po_obj = existing
    else:
        new = WindowPO(**attrs)
        db.add(new)
        window_po_obj = new

    db.commit()
    aggregate_pt_by_enclosure(window.enclosure_id, db)
    return window_po_obj


def thermal_bridge_floor(floor: FloorEnclosure, db: Session):
    print(f"Iniciando thermal_bridge_floor para floor.id: {floor.id}")

    original_floor = db.query(DetailPart).filter(DetailPart.id == floor.floor_id).first()
    if not original_floor:
        raise Exception("Piso original no encontrado")

    name_floor = original_floor.name_detail or "0"
    longitud_pt = floor.po6_l or 0
    cat = original_floor.calculations.get("cat_ceeup", "0")

    if isinstance(cat, str):
        cat1 = "EP" if cat.lower() in ["ep", "ei"] else "EM" if cat.lower() == "em" else "0"
    else:
        cat1 = "0"
    cat2 = "VI"

    try:
        esp1 = float(original_floor.calculations.get("espesor_aislacion", 0))
    except:
        esp1 = 0.0
    if esp1 != 0:
        esp2 = 0.01 if esp1 < 0.03 else 0.03
    else:
        esp2 = 0.0
    esp2_str = format_esp(esp2)

    pos1 = "sa" if esp1 < 0.01 else "ce"
    codigo_pt = "0" if longitud_pt == 0 else f"P06.{cat1}.{cat2}.{pos1.upper()}.{esp2_str}"
    pt = db.query(ThermalBridge.value_pt).filter(ThermalBridge.code_pt == codigo_pt).scalar() or 0

    espacio_cont = floor.characteristic or "0"
    factor = 1 if espacio_cont == 'Exterior' else 0 if espacio_cont == "Inter Recintos Clim" else 0.6 if espacio_cont == "Inter Recintos No Clim" else 0
    pt_lineal = pt * longitud_pt * factor

    existing = db.query(FloorPO).filter(FloorPO.enclosure_id == floor.enclosure_id, FloorPO.floor_id == floor.id).first()
    attrs = {
        "enclosure_id": floor.enclosure_id,
        "floor_id": floor.id,
        "nombre": name_floor,
        "longitud_pt": longitud_pt,
        "categoria": cat,
        "categoria_1": cat1,
        "categoria_2": cat2,
        "posicion_aislamiento": pos1,
        "e_aislamiento_1": esp1,
        "e_aislamiento_2": esp2,
        "codigo_pt": codigo_pt,
        "pt": pt,
        "pt_lineal": pt_lineal,
        "espacio_contiguo": espacio_cont
    }
    if existing:
        for k,v in attrs.items():
            setattr(existing, k, v)
        floor_po_obj = existing
    else:
        new = FloorPO(**attrs)
        db.add(new)
        floor_po_obj = new

    db.commit()
    aggregate_pt_by_enclosure(floor.enclosure_id, db)
    calculate_tablas_py("piso", floor.id, floor.enclosure_id, db)
    return floor_po_obj



def get_thermal_bridges_by_enclosure(enclosure_id: int, db: Session):
    """
    Obtiene todos los thermal bridges asociados a un enclosure dado su ID.

    :param enclosure_id: ID del enclosure.
    :param db: Sesión de base de datos.
    :return: Diccionario con listas de thermal bridges por tipo (wall, window, floor).
    """
    print(f"Obteniendo thermal bridges para enclosure_id: {enclosure_id}")

    try:
        # Obtener thermal bridges asociados a muros
        wall_bridges = db.query(ThermalBridgeWall).filter(
            ThermalBridgeWall.enclosure_id == enclosure_id
        ).all()
        print(f"Se encontraron {len(wall_bridges)} thermal bridges para muros en el enclosure_id: {enclosure_id}")

        # Obtener thermal bridges asociados a ventanas
        window_bridges = db.query(WindowEnclosure).filter(
            WindowEnclosure.enclosure_id == enclosure_id
        ).all()
        print(f"Se encontraron {len(window_bridges)} thermal bridges para ventanas en el enclosure_id: {enclosure_id}")

        # Obtener thermal bridges asociados a pisos
        floor_bridges = db.query(FloorEnclosure).filter(
            FloorEnclosure.enclosure_id == enclosure_id
        ).all()
        print(f"Se encontraron {len(floor_bridges)} thermal bridges para pisos en el enclosure_id: {enclosure_id}")

        return {
            "walls": wall_bridges,
            "windows": window_bridges,
            "floors": floor_bridges
        }
    except Exception as e:
        print(f"Error al obtener thermal bridges para enclosure_id {enclosure_id}: {e}")
        raise


def get_thermal_bridges_value_sum_by_project(project_id: int, db: Session):
    """
    Obtiene la sumatoria de los valores `value_pt` de todos los thermal bridges asociados a un proyecto dado su ID.

    :param project_id: ID del proyecto.
    :param db: Sesión de base de datos.
    :return: Diccionario con la sumatoria de `value_pt` por tipo (wall, window, floor) y el total.
    """
    print(f"Calculando sumatoria de value_pt para project_id: {project_id}")

    try:
        
        # Get enclosures for the project from the EnclosureGenerals table
        enclosures = db.query(EnclosureGenerals).filter(
            EnclosureGenerals.project_id == project_id
        ).all()
        print(f"Se encontraron {len(enclosures)} enclosures para project_id: {project_id}")


        # Gather all thermal bridge wall values for the enclosures
        wall_sum = 0
        for enclosure in enclosures:
            wall_bridges = db.query(ThermalBridgeWall).filter(
            ThermalBridgeWall.enclosure_id == enclosure.id
            ).all()
            
            # For each wall bridge, get associated ThermalBridge values
            for wall_bridge in wall_bridges:
                for element_id in [wall_bridge.po1_id_element, 
                        wall_bridge.po2_id_element,
                        wall_bridge.po3_id_element,
                        wall_bridge.po4_id_element]:
                    if element_id:
                        bridge_value = db.query(ThermalBridge.value_pt).filter(
                            ThermalBridge.id == element_id
                        ).scalar() or 0
                        wall_sum += bridge_value

        print(f"Suma de thermal bridges de muros: {wall_sum}")
       
        return wall_sum
    except Exception as e:
        print(f"Error al calcular sumatoria de value_pt para project_id {project_id}: {e}")
        raise
