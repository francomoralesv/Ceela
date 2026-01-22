import math
from sqlalchemy import func, cast, Float
from sqlalchemy.orm import Session
from src.models.entity.calculations import Calculation
from src.models.entity.constant import Constant
from src.models.entity.details import Detail
from src.models.entity.elements import Element


def calculation_nodes_fourier(conductivity: float, density: float, specific_heat: float, layer_thickness: float, f_ref: float, dt_fourier: float):
    """ Calcula la cantidad de nodos de Fourier necesarios para la simulación. """
    if not conductivity or not density or not specific_heat or not layer_thickness:
        return 0 
    
    try:
        value = math.sqrt(f_ref / ((conductivity / (density * specific_heat)) * (dt_fourier / (layer_thickness / 100) ** 2)))
        return max(1, math.floor(value + 0.999999))
    except ZeroDivisionError:
        return 0  


def calculation_km_op(specific_heat: float, density: float, layer_thickness: float):
    return specific_heat * (density * layer_thickness / 100)



def is_wood(thickness, conductivity, density, specific_heat, is_wood_data):
    if thickness < is_wood_data["e_min_mad"]:
        return 0

    if (is_wood_data["lambda_min_mad"] <= conductivity <= is_wood_data["lambda_max_mad"] and
        is_wood_data["p_min_mad"] <= density <= is_wood_data["p_max_mad"] and
        specific_heat >= is_wood_data["Cp_min_mod"]):
        return 1
    else:
        return 0



def is_insulating(conductivity, density, is_insulation_data):
    return 1 if (conductivity <= is_insulation_data["lambda_max_ais"] and
                 density <= is_insulation_data["p_max_ais"]) else 0




def calculation_default_details(db: Session):
    """ Realiza los cálculos de resistencia térmica y nodos de Fourier para los detalles predeterminados. """

    details = db.query(Detail.id, Detail.material_id, Detail.layer_thickness, Detail.scantilon_location, Detail.name_detail).filter(
        Detail.created_status == "default"
    ).all()

    if not details:
        print("⚠️ No hay detalles para procesar.")
        return

    existing_calculations_set = {
        calc[0] for calc in db.query(Calculation.reference_id).filter(
            Calculation.reference_id.in_([d.id for d in details]),
            Calculation.type == "details",
            Calculation.name == "generals"
        ).all()
    }

    new_details = [d for d in details if d.id not in existing_calculations_set]

    if not new_details:
        print("⚠️ Todos los cálculos ya existen, no hay nuevos para agregar.")
        return

    constants = db.query(Constant.atributs).filter(
        Constant.name == "generals",
        Constant.type == "details"
    ).first()

    if not constants:
        print("⚠️ No se encontraron las constantes generales en la base de datos.")
        return

    f_ref = constants.atributs["Fourier"]["F_ref"]
    dt_fourier = constants.atributs["Fourier"]["dt_Fourier"]
    is_wood_data = {item["name"]: item["value"] for item in constants.atributs["is_wood"]}
    is_insulating_data = {item["name"]: item["value"] for item in constants.atributs["is_insulation"]}
    
    material_ids = {d.material_id for d in new_details}
    materials = db.query(Constant.id, Constant.atributs).filter(Constant.id.in_(material_ids)).all()

    material_properties = {
        m.id: {
            "conductivity": m.atributs.get("conductivity"),
            "density": m.atributs.get("density"),
            "specific_heat": m.atributs.get("specific_heat")
        }
        for m in materials
    }


    new_calculations = []

    for detail in new_details:
        material = material_properties.get(detail.material_id)
        if not material or material["conductivity"] is None:
            print(f"⚠️ El material {detail.material_id} no tiene conductividad definida.")
            continue

        conductivity = material["conductivity"]
        density = material["density"]
        specific_heat = material["specific_heat"]

        r = (detail.layer_thickness / 100) / conductivity
        fourier_nodes = calculation_nodes_fourier(conductivity, density, specific_heat, detail.layer_thickness, f_ref, dt_fourier)
        km_op = calculation_km_op(specific_heat, density, detail.layer_thickness)

        is_wood_ = is_wood(detail.layer_thickness, conductivity, density, specific_heat, is_wood_data)
        is_insulating_ = is_insulating(conductivity, density, is_insulating_data)
        
        new_calculations.append({
            "reference_id": detail.id,
            "type": "details",
            "name": "generals",
            "values": {
                "r": r,
                "fourier_nodes": fourier_nodes,
                "km_op": km_op,
                "is_wood": is_wood_,
                "is_insulation": is_insulating_
            }
        })

    if new_calculations:
        db.bulk_insert_mappings(Calculation, new_calculations)
        db.commit()
        print(f"✅ {len(new_calculations)} cálculos por defecto agregados.")
    else:
        print("⚠️ No se agregaron cálculos debido a datos faltantes.")
        



def calculate_all_doors(db: Session):
    """ Calcula las propiedades térmicas de todas las puertas en una sola operación,
        pero solo si el campo calculations está vacío. """

    doors = db.query(Element).filter(
        Element.type == "door",
        Element.calculations == {}  
    ).all()

    if not doors:
        print("⚠️ Todas las puertas ya tienen cálculos. No se ejecutará de nuevo.")
        return

    constant = db.query(Constant).filter(
        Constant.name == "generals",
        Constant.type == "elements"
    ).first()
    
    thermal_resistances = constant.atributs["thermal_resistances"]
    rsi_m = thermal_resistances["rsi_wall"]
    rse_m = thermal_resistances["rse_wall"]

    # Obtener IDs de las ventanas asociadas
    window_ids = {door.atributs.get("ventana_id") for door in doors if door.atributs.get("ventana_id")}
    window_ids.discard(None)

    # Consultar todas las ventanas en una sola operación
    windows = db.query(Element.id, Element.atributs).filter(Element.id.in_(window_ids), Element.type == "window").all()
    window_map = {window.id: window.atributs for window in windows}

    updates = []

    for door in doors:
        ventana_id = door.atributs.get("ventana_id")
        window_attrs = window_map.get(ventana_id, {})  

        u_puerta_opaca = door.atributs.get("u_puerta_opaca", 0)
        porcentaje_vidrio = door.atributs.get("porcentaje_vidrio", 0)
        u_marco = door.u_marco
        fm = door.fm

        # Evitar división por cero
        u_ponderado_opaco = 0 if (1 - porcentaje_vidrio) == 0 else (
            (u_puerta_opaca * (1 - porcentaje_vidrio - fm) + u_marco * fm) / (1 - porcentaje_vidrio)
        )

        u_vidrio = window_attrs.get("u_vidrio", 0)
        u_ponderado = u_puerta_opaca * (1 - porcentaje_vidrio - fm) + (u_vidrio * porcentaje_vidrio) + (u_marco * fm)
        r_puro = 0 if u_ponderado_opaco == 0 else 1 / u_ponderado_opaco - (rsi_m + rse_m)

        updates.append({
            "id": door.id,
            "calculations": {
                "u_ponderado_opaco": u_ponderado_opaco,
                "u_vidrio": u_vidrio,
                "u_ponderado": u_ponderado,
                "r_puro": r_puro
            }
        })

    if updates:
        db.bulk_update_mappings(Element, updates)
        db.commit()
        print(f"✅ Se calcularon y actualizaron {len(updates)} puertas correctamente.")

    else:
        print("⚠️ No se realizaron cálculos debido a datos faltantes.")


