from sqlalchemy.orm import Session
from src.models.entity.constant import Constant

def calculate_r_pers(ida: str, ocupacion: str, db: Session):
    values = db.query(Constant).filter(
        Constant.type == "enclosures",
        Constant.name == "enclosures"
    ).first()
    
    if not values or not hasattr(values, "atributs"):
        raise ValueError("No se encontraron valores de referencia en la base de datos.")
    
    try:
        value_ida = float(values.atributs["idas"].get(ida.lower(), 0))
        value_ocupacion = float(values.atributs["co2_pers"].get(ocupacion, 0))
        
        if value_ocupacion == 0:
            raise ValueError(f"El valor de ocupación '{ocupacion}' no es válido o es cero.")
        
        return (value_ocupacion * 1_000_000) / (value_ida* 3600)
    
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Error en el cálculo de R-Pers: {str(e)}")
    
    
    
def calculate_potencia_propuesta(potencia_base: float, estrategia: str, db: Session):
    values = db.query(Constant).filter(
        Constant.type == "enclosures",
        Constant.name == "enclosures"
    ).first()

    if not values:
        raise ValueError("No se encontraron valores de referencia en la base de datos.")

    try:
        if estrategia not in values.atributs["estrategia_iluminacion"]:
            raise KeyError(f"Estrategia '{estrategia}' no encontrada en la base de datos.")

        value_estrategia = float(values.atributs["estrategia_iluminacion"][estrategia])

        return potencia_base * (1 - value_estrategia)

    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Error en el cálculo de Potencia Propuesta: {str(e)}")
    
    
    