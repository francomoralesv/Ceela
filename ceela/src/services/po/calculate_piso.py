import math
from sqlalchemy.orm import Session
from src.models.entity.calculate_piso import CalculatePiso
from src.models.entity.constant import Constant
from src.models.entity.floor import FloorEnclosure
from src.models.entity.detail_part import DetailPart
from src.models.entity.pt_table import PTTable

# ------------------------------
# Constantes Globales
# ------------------------------
LAMBDA_G = 2
RSI = 0.17
RSE = 0.4
DW = 0.20
PI = math.pi

# ------------------------------
# Funciones Auxiliares de Cálculo
# ------------------------------
def calculate_b(area: float, perimetro: float) -> float:
    try:
        return area / (perimetro / 2)
    except (ZeroDivisionError, TypeError):
        return 0

def calculate_rf(value_u: float) -> float:
    try:
        return 1 / value_u
    except (ZeroDivisionError, TypeError):
        return 0

def calculate_df(rf: float) -> float:
    return DW + LAMBDA_G * (RSI + RSE + rf)

def calculate_udf_sog(df: float, b: float) -> float:
    if df < b:
        return (2 * LAMBDA_G) / (PI * b + df) * math.log(((PI * b) / df) + 1)
    return LAMBDA_G / (0.457 * b + df)

def calculate_psi(e_aisl: float) -> float:
    return 0.2 if e_aisl != 0 else 0

def calculate_u_vert(ufg_sog: float, psi_vertical: float, b: float) -> float:
    try:
        return ufg_sog + 2 * (psi_vertical / b)
    except ZeroDivisionError:
        return 0

def calculate_rn_vert(e_aislacion_vert: float, lambda_aislacion_vert: float) -> float:
    try:
        return e_aislacion_vert / lambda_aislacion_vert
    except ZeroDivisionError:
        return 0

def calculate_dn_vert(e_aislacion_vert: float) -> float:
    try:
        return e_aislacion_vert / LAMBDA_G
    except ZeroDivisionError:
        return 0

def calculate_r_vertical(rn_vertical: float, dn_vertical: float) -> float:
    return rn_vertical - dn_vertical

def calculate_d_vertical(r_vertical: float) -> float:
    return r_vertical * LAMBDA_G

def calculate_psi_vertical(D_vertical: float, df: float, d_vertical: float) -> float:
    return -1 * (LAMBDA_G / PI) * (math.log((2 * D_vertical / df) + 1) - math.log((2 * D_vertical / (df + d_vertical)) + 1))

def calculate_u_horiz(ufg_sog: float, psi_horiz: float, b: float) -> float:
    try:
        return ufg_sog + 2 * (psi_horiz / b)
    except ZeroDivisionError:
        return 0

def calculate_rn_horiz(e_aislacion_horiz: float, lambda_aislacion_horiz: float) -> float:
    try:
        return e_aislacion_horiz / lambda_aislacion_horiz
    except ZeroDivisionError:
        return 0

def calculate_dn_horiz(e_aislacion_horiz: float) -> float:
    try:
        return e_aislacion_horiz / LAMBDA_G
    except ZeroDivisionError:
        return 0

def calculate_r_horiz(rn_horiz: float, dn_horiz: float) -> float:
    return rn_horiz - dn_horiz

def calculate_d_horiz(r_horiz: float) -> float:
    return r_horiz * LAMBDA_G

def calculate_psi_horiz(D_horiz: float, df: float, d_horiz: float) -> float:
    return -1 * (LAMBDA_G / PI) * (math.log((2 * D_horiz / df) + 1) - math.log((2 * D_horiz / (df + d_horiz)) + 1))

def calculate_psi_min(psi_vertical: float, psi_horiz: float) -> float:
    # Esta función no se utiliza en el flujo principal; se puede modificar según se requiera.
    return psi_horiz * psi_vertical

def calculate_ls(area: float, u_vert: float, u_horiz: float, perimetro: float, psi_vertical: float, psi_horiz: float) -> float:
    # Se utiliza la función built-in min() para obtener el mínimo de u_vert y u_horiz.
    return area * min(u_vert, u_horiz) + perimetro * (psi_vertical + psi_horiz)


def calculate_ls_ponderado(floor: FloorEnclosure, db: Session):
    """
    Calcula el promedio ponderado de ls para todos los pisos asociados a un enclosure.
    
    La fórmula es:
        ls_ponderado = (ls1 * area1 + ls2 * area2 + ... + lsN * areaN) / (area1 + area2 + ... + areaN)
        
    Se asume que cada piso ya tiene un registro de cálculo (CalculatePiso) con su ls calculado.
    
    Además, se actualiza la columna total_pt en PTTable para que sea la suma de los pt (P01 a P06)
    más el pt_piso_prop, que se toma del mismo PTTable.
    
    Si ya existe un registro en PTTable para ese enclosure_id se actualiza; de lo contrario, se crea uno nuevo.
    
    Args:
        floor (FloorEnclosure): Objeto piso, cuyo enclosure_id se usará para agrupar los pisos.
        db (Session): La sesión de base de datos.
    
    Returns:
        PTTable: El registro de PTTable actualizado o creado.
    """
    # Obtener todos los pisos del enclosure
    pisos = db.query(FloorEnclosure).filter(FloorEnclosure.enclosure_id == floor.enclosure_id).all()
    if not pisos:
        return None

    total_area = 0.0
    suma_ponderada = 0.0

    for piso in pisos:
        # Se asume que ya se ha calculado la terminancia del piso y
        # existe un registro en CalculatePiso para cada piso.
        calculo_piso = (
            db.query(CalculatePiso)
            .filter(CalculatePiso.floor_id == piso.id)
            .first()
        )
        # Si no se encontró el registro, se ignora ese piso.
        if not calculo_piso:
            continue
        # Se acumulan ls * área y el total de área
        suma_ponderada += calculo_piso.ls * piso.area
        total_area += piso.area

    # Evitar división por cero
    ls_ponderado = suma_ponderada / total_area if total_area > 0 else 0

    # Buscar si ya existe un registro en PTTable para este enclosure_id
    enclosure_record = (
        db.query(PTTable)
        .filter(PTTable.enclosure_id == floor.enclosure_id)
        .first()
    )
    
    if enclosure_record:
        # Actualizar pt_piso_prop con ls_ponderado
        enclosure_record.pt_piso_prop = ls_ponderado
        # Total_pt = (P01 + P02 + P03 + P04 + P05 + P06) + pt_piso_prop
        enclosure_record.total_pt = (
            (enclosure_record.P01 or 0) +
            (enclosure_record.P02 or 0) +
            (enclosure_record.P03 or 0) +
            (enclosure_record.P04 or 0) +
            (enclosure_record.P05 or 0) +
            (enclosure_record.P06 or 0) +
            ls_ponderado
        )
    else:
        # Si no existe, se crea el registro; en este caso se asumen P01-P06 en 0
        enclosure_record = PTTable(
            enclosure_id=floor.enclosure_id,
            P01=0,
            P02=0,
            P03=0,
            P04=0,
            P05=0,
            P06=0,
            pt_piso_prop=ls_ponderado,
            total_pt=ls_ponderado,
            pt_piso_base=0,
            case="Propuesto"
        )
        db.add(enclosure_record)

    db.commit()
    db.refresh(enclosure_record)
    return enclosure_record


# ------------------------------
# Función Principal: Calcular/Actualizar Terminancia de Piso
# ------------------------------
def safe_get_float(data: dict, key1: str, key2: str, default: float = 0) -> float:
    """
    Intenta obtener data[key1][key2] y llamar a .as_float(). 
    Si falla por no existir la clave o por error de atributo, devuelve default.
    """
    try:
        value = data.get(key1, {}).get(key2, None)
        if value is None:
            return default
        return value.as_float()
    except (AttributeError, TypeError):
        return default

def calculate_termitancia_piso(floor: FloorEnclosure, db: Session) -> CalculatePiso:
    # Se busca el registro existente según floor_id
    calculate_piso = db.query(CalculatePiso).filter(CalculatePiso.enclosure_id == floor.enclosure_id, CalculatePiso.floor_id == floor.id).first()
    
    original_floor = db.query(DetailPart).filter(
        DetailPart.id == floor.floor_id
    ).first()
    
    area = floor.area
    perimetro = floor.parameter

    # Datos de aislación vertical
    lambda_aislacion_vert = safe_get_float(original_floor.info, "ref_aisl_vertical", "lambda", 0)
    e_aislacion_vert = safe_get_float(original_floor.info, "ref_aisl_vertical", "e_aisl", 0)
    value_u = getattr(original_floor, "value_u", 0)
    d_val_vert = safe_get_float(original_floor.calculations, "ref_aisl_vertical", "d", 0) / 100
    D_vertical = d_val_vert if d_val_vert > 0.4 else 0.4

    # Datos de aislación horizontal
    lambda_aislacion_horiz = safe_get_float(original_floor.info, "ref_aisl_horizontal", "lambda", 0)
    e_aislacion_horiz = safe_get_float(original_floor.info, "ref_aisl_horizontal", "e_aisl", 0)
    d_val_horiz = safe_get_float(original_floor.calculations, "ref_aisl_horizontal", "d", 0) / 100
    D_horiz = d_val_horiz if d_val_horiz > 0.4 else 0.4

    e_aisl = safe_get_float(original_floor.info, "aislacion_bajo_piso", "e_aisl", 0)
    
    # Cálculos intermedios
    b = calculate_b(area, perimetro)
    rf = calculate_rf(value_u)
    df = calculate_df(rf)
    ufg_sog = calculate_udf_sog(df, b)
    psi = calculate_psi(e_aisl)
    
    # Cálculos para aislación vertical
    rn_vert = calculate_rn_vert(e_aislacion_vert, lambda_aislacion_vert)
    dn_vert = calculate_dn_vert(e_aislacion_vert)
    r_vert = calculate_r_vertical(rn_vert, dn_vert)
    d_vert = calculate_d_vertical(r_vert)
    psi_vertical = calculate_psi_vertical(D_vertical, df, d_vert)
    u_vert = calculate_u_vert(ufg_sog, psi_vertical, b)

    # Cálculos para aislación horizontal
    rn_horiz = calculate_rn_horiz(e_aislacion_horiz, lambda_aislacion_horiz)
    dn_horiz = calculate_dn_horiz(e_aislacion_horiz)
    r_horiz = calculate_r_horiz(rn_horiz, dn_horiz)
    d_horiz = calculate_d_horiz(r_horiz)
    psi_horiz = calculate_psi_horiz(D_horiz, df, d_horiz)
    u_horiz = calculate_u_horiz(ufg_sog, psi_horiz, b)

    # Cálculo de psi_min y ls
    psi_min = min(psi_vertical, psi_horiz)
    ls = calculate_ls(area, u_vert, u_horiz, perimetro, psi_vertical, psi_horiz)

    # Si existe el registro, se actualizan sus campos; de lo contrario, se crea uno nuevo.
    if calculate_piso:
        calculate_piso.enclosure_id = floor.enclosure_id
        calculate_piso.floor_id = floor.floor_id
        calculate_piso.b = b
        calculate_piso.rf = rf
        calculate_piso.df = df
        calculate_piso.ufg_sog = ufg_sog
        calculate_piso.psi = psi
        calculate_piso.u_vert = u_vert
        calculate_piso.rn_vert = rn_vert
        calculate_piso.dn_vert = dn_vert
        calculate_piso.r_vertical = r_vert
        calculate_piso.d_vertical = d_vert
        calculate_piso.psi_vertical = psi_vertical
        calculate_piso.u_horiz = u_horiz
        calculate_piso.rn_horiz = rn_horiz
        calculate_piso.dn_horiz = dn_horiz
        calculate_piso.r_horiz = r_horiz
        calculate_piso.d_horiz = d_horiz
        calculate_piso.psi_horiz = psi_horiz
        calculate_piso.psi_min = psi_min
        calculate_piso.ls = ls
    else:
        calculate_piso = CalculatePiso(
            enclosure_id=floor.enclosure_id,
            floor_id=floor.id,
            b=b,
            rf=rf,
            df=df,
            ufg_sog=ufg_sog,
            psi=psi,
            u_vert=u_vert,
            rn_vert=rn_vert,
            dn_vert=dn_vert,
            r_vertical=r_vert,
            d_vertical=d_vert,
            psi_vertical=psi_vertical,
            u_horiz=u_horiz,
            rn_horiz=rn_horiz,
            dn_horiz=dn_horiz,
            r_horiz=r_horiz,
            d_horiz=d_horiz,
            psi_horiz=psi_horiz,
            psi_min=psi_min,
            ls=ls
        )
        db.add(calculate_piso)

    db.commit()
    db.refresh(calculate_piso)

    
    calculate_ls_ponderado(calculate_piso, db)