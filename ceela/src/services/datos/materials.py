import logging
import math
from collections import defaultdict
from typing import Any, Dict, List

import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.entity.calculations import Calculation
from src.models.entity.constant import \
    Constant  # Modelo para la tabla constants
from src.models.entity.detail_part import DetailPart
from src.models.entity.details import Detail
from src.models.entity.door import DoorEnclosure
from src.models.entity.elements import Element
# Importar los modelos según la estructura de tu proyecto
from src.models.entity.enclosure_general import EnclosureGenerals
from src.models.entity.floor import FloorEnclosure
from src.models.entity.formulas import Formulas
from src.models.entity.roof import RoofEnclosure
from src.models.entity.tabla_py import TablaPy
from src.models.entity.wall import WallEnclosure
from src.models.entity.window import WindowEnclosure

logger = logging.getLogger(__name__)

# Definir el mapeo de orientaciones
ORIENTATION_MAPPING: Dict[str, str] = {
    "N": "Wall1",
    "NE": "Wall2",
    "E": "Wall3",
    "SE": "Wall4",
    "S": "Wall5",
    "SO": "Wall6",
    "O": "Wall7",
    "NO": "Wall8",
    "AD": "Interior climatizado",
    "IN": "Interior no climatizado",
    "HR": "roof",
    "CT": "floor",
    "FL": "floor2"
}

TEMPERATURA_INTERIOR_MAPPING: Dict[str, str] = {
    "N": "NORMAL",
    "NE": "NORMAL",
    "E": "NORMAL",
    "SE": "NORMAL",
    "S": "NORMAL",
    "SO": "NORMAL",
    "O": "NORMAL",
    "NO": "NORMAL",
    "AD": "ADIABATICO",
    "IN": "INTERIOR",
    "HR": "TECHO",
    "CT": "C_TERRENO",
    "FL": "VENTILADO"
}

TEMPERATURA_EXTERIOR_MAPPING: Dict[str, str] = {
    "N": "TE",
    "NE": "TE",
    "E": "TE",
    "SE": "TE",
    "S": "TE",
    "SO": "TE",
    "O": "TE",
    "NO": "TE",
    "AD": "ZTC",
    "IN": "ZTU",
    "HR": "TE",
    "CT": "TT",
    "FL": "TE"
}



from collections import defaultdict
from typing import Any, Dict, List, Tuple
import math
from sqlalchemy.orm import Session
from sqlalchemy import cast
from sqlalchemy.types import Float

import math
from collections import defaultdict
from typing import List, Dict, Any, Tuple

def get_material_details(
    enclosure_id: int,
    current_user: dict = None,
    db: "Session" = None
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    # 1) project_id del enclosure
    enclosure = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.id == enclosure_id
    ).first()
    project_id = getattr(enclosure, "project_id", 0)

    # 2) TablaPy (muro/techo/piso/door)
    tabla_records = db.query(TablaPy).filter(
        TablaPy.enclosure_id == enclosure_id,
        TablaPy.type.in_(["muro", "techo", "piso", "door"])
    ).all()

    processed_orientations = defaultdict(set)

    # Constantes de Fourier (con fallback seguro)
    constants = db.query(Constant).filter(
        Constant.name == "generals",
        Constant.type == "details"
    ).first()
    fourier = ((constants.atributs or {}).get("Fourier") if constants else {}) or {}
    f_ref = fourier.get("F_ref", 0)
    dt_fourier = fourier.get("dt_Fourier", 0)

    # Acumuladores por orientación
    orient_acc: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)

    # 3) Recorrer TablaPy y acumular datos por orientación (incluye puertas)
    for record in tabla_records:
        original_orientation = getattr(record, "orientation", "ND") or "ND"
        mapped_orientation = ORIENTATION_MAPPING.get(original_orientation, original_orientation)

        area = 0.0
        dp_type_from_record = None
        door_element_id = None
        is_door = (record.type == "door")

        if record.type == "muro":
            ent = db.query(WallEnclosure).filter(
                WallEnclosure.id == record.item_id,
                WallEnclosure.enclosure_id == enclosure_id
            ).first()
            detail_part_id = getattr(ent, "wall_id", None) if ent else None
            area = float(getattr(ent, "area", 0) or 0)
            dp_type_from_record = "Muro"

        elif record.type == "techo":
            ent = db.query(RoofEnclosure).filter(
                RoofEnclosure.id == record.item_id,
                RoofEnclosure.enclosure_id == enclosure_id
            ).first()
            detail_part_id = getattr(ent, "roof_id", None) if ent else None
            area = float(getattr(ent, "area", 0) or 0)
            dp_type_from_record = "Techo"

        elif record.type == "piso":
            ent = db.query(FloorEnclosure).filter(
                FloorEnclosure.id == record.item_id,
                FloorEnclosure.enclosure_id == enclosure_id
            ).first()
            detail_part_id = getattr(ent, "floor_id", None) if ent else None
            area = float(getattr(ent, "area", 0) or 0)
            dp_type_from_record = "Piso"

        elif record.type == "door":
            ent = db.query(DoorEnclosure).filter(
                DoorEnclosure.id == record.item_id,
                DoorEnclosure.enclosure_id == enclosure_id
            ).first()
            detail_part_id = None
            if ent:
                door_element_id = getattr(ent, "door_id", None)   # Elements.id
                # si existe detail_part_id úsalo, pero no es requisito para competir
                detail_part_id = getattr(ent, "detail_part_id", None)

                # área o (ancho*alto)
                area = float(getattr(ent, "area", 0) or 0)
                if area <= 0:
                    w = float(getattr(ent, "broad", 0) or getattr(ent, "width", 0) or 0)
                    h = float(getattr(ent, "high", 0) or getattr(ent, "height", 0) or 0)
                    area = w * h

                dp_type_from_record = "Muro"  # compite con muros

        if area <= 0:
            continue

        # Para muros/techos/pisos: usar DetailPart para km_op (peso)
        dp_id = None
        km_op_for_competition = 0.0

        if not is_door:
            if not detail_part_id:
                continue
            dp = db.query(DetailPart).filter(
                DetailPart.id == detail_part_id,
                DetailPart.project_id == project_id
            ).first()
            if not dp:
                continue
            dp_id = dp.id
            try:
                km_op_for_competition = float((dp.calculations or {}).get("km_op", 0) or 0)
            except Exception:
                km_op_for_competition = 0.0

        else:
            # PUERTA: cálculos internos sin depender de DetailPart
            layer_thickness_raw = 10            # mm (constante)
            d_value = layer_thickness_raw / 100 # m
            specific_heat = 1759
            density = 410

            # r_puro desde Elements
            r_puro_door = 0.0
            if door_element_id:
                elem = db.query(Element).filter(
                    Element.id == door_element_id,
                    Element.type == "door"
                ).first()
                if elem:
                    try:
                        r_puro_door = float((elem.calculations or {}).get("r_puro", 0) or 0)
                    except Exception:
                        r_puro_door = 0.0

            # conductivity interna (no se retorna): d / r_puro
            conductivity_door = (d_value / r_puro_door) if r_puro_door else 0.0

            # km_op para competir: c * density * d
            km_op_door = specific_heat * density * d_value

            # id sintético negativo para puertas (en base al elements.id) para diferenciar
            dp_id = -int(door_element_id or 0) if door_element_id else None
            if dp_id is None:
                continue

            km_op_for_competition = km_op_door

        peso = km_op_for_competition * area

        orient_acc[(original_orientation, mapped_orientation)].append({
            "dp_id": dp_id,
            "detail_part_id": None if is_door else detail_part_id,
            "dp_name_detail": "Puerta" if is_door else (dp.name_detail if not is_door else "Puerta"),
            "dp_type": dp_type_from_record,
            "km_op": km_op_for_competition,
            "area": area,
            "peso": peso,
            "is_door": is_door,
            "door_element_id": door_element_id
        })

    # 4) Procesar cada orientación (puertas compiten con muros/techos/pisos)
    for (original_orientation, mapped_orientation), items in orient_acc.items():
        if not items:
            continue

        # Sumas por orientación (todos compiten con la misma regla)
        suma_areas = sum(x["area"] for x in items) or 0.0
        for it in items:
            it["km_op_2"] = (it["km_op"] * it["area"] / suma_areas) if suma_areas > 0 else 0.0
        suma_km_op_2 = sum(it["km_op_2"] for it in items)

        # r_puro por ítem (puerta: Elements.r_puro; otros: suma Details.r)
        r_puro_por_item: Dict[int, float] = {}
        for it in items:
            dp_key = it["dp_id"]
            r_puro = 0.0

            if it.get("is_door") and it.get("door_element_id"):
                elem = db.query(Element).filter(
                    Element.id == it["door_element_id"],
                    Element.type == "door"
                ).first()
                if elem:
                    try:
                        r_puro = float((elem.calculations or {}).get("r_puro", 0) or 0)
                    except Exception:
                        r_puro = 0.0
            else:
                dp_details = db.query(Detail).filter(
                    Detail.detail_part_id == it["detail_part_id"],
                    Detail.project_id == project_id,
                    Detail.is_deleted == False
                ).all()
                for d in dp_details:
                    d_id = getattr(d, "id", None)
                    if not d_id:
                        continue
                    calc = db.query(Calculation).filter(
                        Calculation.reference_id == d_id,
                        Calculation.project_id == project_id
                    ).first()
                    if not calc:
                        continue
                    try:
                        r_val = float((calc.values or {}).get("r", 0) or 0)
                    except Exception:
                        r_val = 0.0
                    r_puro += r_val

            r_puro_por_item[dp_key] = r_puro

        # Elegir GANADOR (misma métrica peso/suma_pesos)
        suma_pesos = sum(x["peso"] for x in items) or 0.0
        if suma_pesos <= 0:
            ganador = next((x for x in items if x["km_op"] > 0), items[0])
        else:
            ganador = max(items, key=lambda x: (x["peso"] / suma_pesos))

        # === Si la puerta gana esta orientación ===
        if ganador.get("is_door", False):
            # Constantes puerta (internas)
            layer_thickness_raw = 10
            d_value = layer_thickness_raw / 100.0
            specific_heat = 1759
            density = 410

            # Agrupar SOLO puertas de la orientación
            door_items = [it for it in items if it.get("is_door")]
            suma_areas_puertas = sum(it["area"] for it in door_items) or 0.0

            # Cálculo agregado para puertas (km_op_2 y r_a_atot_sum de puertas)
            suma_km_op_2_puertas = 0.0
            r_a_atot_items_puertas = []
            for it in door_items:
                dp_key = it["dp_id"]
                r_puro_i = r_puro_por_item.get(dp_key, 0.0)

                km_op_door_i = specific_heat * density * d_value
                km_op_2_i = (km_op_door_i / suma_areas_puertas) if suma_areas_puertas > 0 else 0.0
                suma_km_op_2_puertas += km_op_2_i

                factor_area_puerta = (it["area"] / suma_areas_puertas) if suma_areas_puertas else 0.0
                r_a_atot_items_puertas.append(r_puro_i * factor_area_puerta)

            r_a_atot_sum_puertas = sum(r_a_atot_items_puertas) if r_a_atot_items_puertas else 0.0

            # Parámetros del ganador puerta
            r_puro_ganador = r_puro_por_item.get(ganador["dp_id"], 0.0)
            conductivity_ganador = (d_value / r_puro_ganador) if r_puro_ganador else 0.0
            r_porcentaje_ganador = ((d_value / conductivity_ganador) / r_puro_ganador) if (conductivity_ganador and r_puro_ganador) else 0.0

            # conductivity_final = d / (r_porcentaje * r_a_atot_sum_puertas)  -> lambda
            conductivity_final = (d_value / (r_porcentaje_ganador * r_a_atot_sum_puertas)) if (r_porcentaje_ganador and r_a_atot_sum_puertas) else 0.0

            # Construir material_info de la PUERTA ganadora:
            material_info = {
                "name": "Puerta",
                "p": density,                                # density como 'p'
                "lambda": conductivity_final,                # lambda final
                "c": specific_heat,                          # AHORA: c = 1759 (como pediste)
                "d": d_value,                                # 0.1 m
                "R": (d_value / conductivity_final) if conductivity_final else 0,
                "Nd": 0  # se calcula abajo con la misma fórmula que el resto
            }

            # Nd de PUERTA (misma fórmula que muro/techo/piso)
            try:
                denom_nd = (material_info["lambda"] / (material_info["p"] * material_info["c"])) \
                           * (dt_fourier / (material_info["d"] ** 2)) if material_info["d"] else 0
                if denom_nd:
                    val_nd = math.sqrt(f_ref / denom_nd) + 0.999999
                    material_info["Nd"] = max(1, int(val_nd))
                else:
                    material_info["Nd"] = 0
            except Exception:
                material_info["Nd"] = 0

            puerta_key = f"Puerta_{original_orientation}_{mapped_orientation}"
            if puerta_key not in processed_orientations[(original_orientation, mapped_orientation)]:
                results.append({
                    "orientation": original_orientation,
                    "capa": mapped_orientation,
                    "material_info": material_info,
                    "detail_id": None,
                    "km_op_detail": 0.0
                })
                processed_orientations[(original_orientation, mapped_orientation)].add(puerta_key)

            continue  # puertas no se descomponen en Details

        # === Si NO gana puerta: flujo tradicional (muro/techo/piso) ===
        dp_id_win = ganador["detail_part_id"]

        # km_op_detail_part del DP ganador
        km_op_detail_part = 0.0
        if dp_id_win:
            dp_rec = db.query(DetailPart).filter(
                DetailPart.id == dp_id_win,
                DetailPart.project_id == project_id
            ).first()
            if dp_rec:
                try:
                    km_op_detail_part = float((dp_rec.calculations or {}).get("km_op", 0) or 0)
                except Exception:
                    km_op_detail_part = 0.0

        # r_a_atot_sum (global) para esta orientación (todos los ítems)
        r_a_atot_sum_global = 0.0
        for it in items:
            r_puro_i = r_puro_por_item.get(it["dp_id"], 0.0)
            factor_area_global = (it["area"] / suma_areas) if suma_areas else 0.0
            r_a_atot_sum_global += r_puro_i * factor_area_global

        # Descomponer por Details del DP ganador
        details_records = db.query(Detail).filter(
            Detail.detail_part_id == dp_id_win,
            Detail.project_id == project_id,
            Detail.is_deleted == False
        ).all()
        if not details_records:
            details_records = [{"material_id": 0, "layer_thickness": 0, "id": None}]

        for d in details_records:
            detail_id_i = d.get("id", None) if isinstance(d, dict) else getattr(d, "id", None)

            km_op_detail_i = 0.0
            r_detail_i = 0.0
            if detail_id_i:
                calc_i = db.query(Calculation).filter(
                    Calculation.reference_id == detail_id_i,
                    Calculation.project_id == project_id
                ).first()
                if calc_i:
                    try:
                        km_op_detail_i = float((calc_i.values or {}).get("km_op", 0) or 0)
                    except Exception:
                        km_op_detail_i = 0.0
                    try:
                        r_detail_i = float((calc_i.values or {}).get("r", 0) or 0)
                    except Exception:
                        r_detail_i = 0.0

            p_val_i = (km_op_detail_i / km_op_detail_part) * suma_km_op_2 if km_op_detail_part else 0.0

            material_id = d.get("material_id", 0) if isinstance(d, dict) else getattr(d, "material_id", 0)
            layer_thickness_raw = d.get("layer_thickness", 0) if isinstance(d, dict) else getattr(d, "layer_thickness", 0)
            d_value = (layer_thickness_raw or 0) / 100.0  # m

            specific_heat = 0.0
            conductivity_original = 0.0
            material_name = ""
            if material_id:
                const_rec = db.query(Constant).filter(
                    Constant.id == material_id,
                    Constant.type == "definition materials",
                    Constant.name == "materials"
                ).first()
                if const_rec:
                    at = const_rec.atributs or {}
                    material_name = at.get("name", "")
                    conductivity_original = at.get("conductivity", 0) or 0
                    specific_heat = at.get("specific_heat", 0) or 0

            denom_true = (specific_heat * d_value)
            p_val_true = (p_val_i / denom_true) if denom_true else 0.0

            r_puro_ganador = r_puro_por_item.get(ganador["dp_id"], 0.0)
            if conductivity_original and r_puro_ganador:
                r_porcentaje_i = (d_value / conductivity_original) / r_puro_ganador
            else:
                r_porcentaje_i = 0.0

            denom_lambda = (r_porcentaje_i * r_a_atot_sum_global) if r_a_atot_sum_global else 0.0
            lambda_new = (d_value / denom_lambda) if denom_lambda else 0.0

            material_info = {
                "name": material_name,
                "p": p_val_true,
                "lambda": lambda_new,
                "c": specific_heat,
                "d": d_value,
                "R": (d_value / lambda_new) if lambda_new else 0
            }

            # Nd (Fourier) — misma fórmula
            try:
                denom = (material_info["lambda"] / (material_info["p"] * material_info["c"])) \
                        * (dt_fourier / (material_info["d"] ** 2)) if material_info["d"] else 0
                if denom:
                    val = math.sqrt(f_ref / denom) + 0.999999
                    Nd_val = max(1, int(val))
                else:
                    Nd_val = 0
            except Exception:
                Nd_val = 0
            material_info["Nd"] = Nd_val

            key = f"{material_info['name']}_{material_info['d']}_{material_info['lambda']}"
            if key not in processed_orientations[(original_orientation, mapped_orientation)]:
                results.append({
                    "orientation": original_orientation,
                    "capa": mapped_orientation,
                    "material_info": material_info,
                    "detail_id": detail_id_i,
                    "km_op_detail": km_op_detail_i
                })
                processed_orientations[(original_orientation, mapped_orientation)].add(key)

        # 6) Caso especial: Piso con original_orientation == "CT" → Tierra (igual que antes)
        if (ganador["dp_type"] == "Piso") and (original_orientation == "CT"):
            tierra_key = "Tierra_1_2"
            if tierra_key not in processed_orientations[(original_orientation, mapped_orientation)]:
                tierra_info = {
                    "name": "Tierra",
                    "p": 1800,
                    "lambda": 2,
                    "c": 3157,
                    "d": 1,
                    "R": 0.5,
                    "Nd": 20
                }
                results.append({
                    "orientation": original_orientation,
                    "capa": mapped_orientation,
                    "material_info": tierra_info,
                    "detail_id": None,
                    "km_op_detail": 0.0
                })
                processed_orientations[(original_orientation, mapped_orientation)].add(tierra_key)

    return results



def get_nodos_area_by_orientation(
        enclosure_id: int,
        db: Session,
        current_user: dict | None = None
) -> List[Dict[str, Any]]:
    """
    Para cada orientación, devuelve el mayor valor de nodos_area y su correspondiente nodos_emisividad.
    El resto de datos se conservan tal como estaban inicialmente.
    """
    print(f"[DEBUG] Inicio de depuración: enclosure_id={enclosure_id}")
    results: List[Dict[str, Any]] = []

    grouped: Dict[str, Dict[str, Any]] = {
        ori: {
            "Componente": comp,
            "Orientacion": ori,
            "Absorcion": 0,
            "Area": 0,
            "Temperatura_Exterior": TEMPERATURA_EXTERIOR_MAPPING.get(ori, "NORMAL"),
            "Temperatura": TEMPERATURA_INTERIOR_MAPPING.get(ori, "NORMAL"),
            "item_id": None,
            "type": None
        }
        for ori, comp in ORIENTATION_MAPPING.items()
    }
    print(f"[DEBUG] Buckets iniciales: {grouped}")

    try:
        tabla_records = (
            db.query(TablaPy)
            .filter(
                TablaPy.enclosure_id == enclosure_id,
                TablaPy.type.in_(["muro", "techo", "piso", "door", "window"])
            )
            .all()
        )
        print(f"[DEBUG] Registros obtenidos: {len(tabla_records)}")
    except Exception as exc:
        print(f"[ERROR] Error consultando TablaPy: {exc}")
        return list(grouped.values())

    for idx, record in enumerate(tabla_records, start=1):
        orientation = getattr(record, "orientation", None) or "ND"
        print(f"[DEBUG] Registro #{idx}: orientation={orientation}, type={record.type}, item_id={record.item_id}")
        if orientation not in ORIENTATION_MAPPING:
            print(f"[WARN] Orientación '{orientation}' no válida, se omite")
            continue

        record_type = getattr(record, "type", "")
        item_id = getattr(record, "item_id", None)
        nodos_area = getattr(record, "nodos_area", 0) or 0
        nodos_emisividad = getattr(record, "nodos_emisividad", 0) or 0
        print(f"[DEBUG] nodos_area={nodos_area}, nodos_emisividad={nodos_emisividad}")

        # Solo llenar item_id y type si siguen siendo None
        if grouped[orientation]["item_id"] is None:
            grouped[orientation]["item_id"] = item_id
            print(f"[DEBUG] Se asigna item_id inicial para '{orientation}': {item_id}")
        if grouped[orientation]["type"] is None:
            grouped[orientation]["type"] = record_type
            print(f"[DEBUG] Se asigna type inicial para '{orientation}': {record_type}")
        
        if record_type in ("muro", "door"):
            if record_type == "muro":
                ent = (
                    db.query(WallEnclosure)
                    .filter(
                        WallEnclosure.id == item_id,
                        WallEnclosure.enclosure_id == enclosure_id
                    )
                    .first()
                )
                area = ent.area if ent and ent.area else 0
                print(f"[DEBUG] Muro área={area}")
            else:  # door
                ent = (
                    db.query(DoorEnclosure)
                    .filter(DoorEnclosure.id == item_id)
                    .first()
                )
                area = (ent.broad or 0) * (ent.high or 0) if ent else 0
                print(f"[DEBUG] Door área={area}")

            grouped[orientation]["Area"] += area
            prev = grouped[orientation]["Absorcion"]
            if nodos_emisividad > prev:
                grouped[orientation]["Absorcion"] = nodos_emisividad
                print(f"[DEBUG] Nueva Absorcion para '{orientation}': {prev} -> {nodos_emisividad}")
            else:
                print(f"[DEBUG] Absorcion no cambia para '{orientation}': permanece {prev}")

        elif record_type == "techo":
            roof = db.query(RoofEnclosure).filter(
                RoofEnclosure.id == item_id,
                RoofEnclosure.enclosure_id == enclosure_id
            ).first()
            if roof:
                prev_area = grouped[orientation]["Area"]
                if nodos_area > prev_area:
                    grouped[orientation]["Area"] = nodos_area
                    grouped[orientation]["Absorcion"] = nodos_emisividad
                    print(f"[DEBUG] Techo nuevo Area para '{orientation}': {prev_area} -> {nodos_area}, Absorcion={nodos_emisividad}")
                else:
                    print(f"[DEBUG] Techo mantiene Area para '{orientation}': {prev_area}, Absorcion={grouped[orientation]['Absorcion']}")

        elif record_type == "piso":
            floor = db.query(FloorEnclosure).filter(
                FloorEnclosure.id == item_id,
                FloorEnclosure.enclosure_id == enclosure_id
            ).first()
            if floor:
                prev_area = grouped[orientation]["Area"]
                if nodos_area > prev_area:
                    grouped[orientation]["Area"] = nodos_area
                    grouped[orientation]["Absorcion"] = nodos_emisividad
                    print(f"[DEBUG] Piso nuevo Area para '{orientation}': {prev_area} -> {nodos_area}, Absorcion={nodos_emisividad}")
                else:
                    print(f"[DEBUG] Piso mantiene Area para '{orientation}': {prev_area}, Absorcion={grouped[orientation]['Absorcion']}")

        print(f"[DEBUG] Estado bucket['{orientation}']: Area={grouped[orientation]['Area']}, Absorcion={grouped[orientation]['Absorcion']}")

    result = [grouped[ori] for ori in ORIENTATION_MAPPING.keys()]
    print(f"[DEBUG] Resultado final: {result}")
    return result



def get_translucent_window_area(enclosure_id: int, current_user: dict, db: Session) -> Dict[str, Any]:
    """
    Consulta todas las ventanas (WindowEnclosure) creadas en un recinto y calcula, para cada una,
    el área traslúcida.

    Donde fm se extrae del elemento correspondiente en la tabla Elements (filtrado por window_id y type=="window").
    Se suma el área traslúcida de cada ventana y se retorna:
        - total_translucent_area: Suma total del área traslúcida de todas las ventanas.
        - windows: Lista de objetos con los datos de cada ventana (id, área total, área traslúcida y fm obtenido).

    :param enclosure_id: Identificador del recinto.
    :param db: Sesión de base de datos (SQLAlchemy Session).
    :return: Diccionario con la suma total del área traslúcida y la lista de ventanas.
    """
    windows: List[WindowEnclosure] = db.query(WindowEnclosure).filter(
        WindowEnclosure.enclosure_id == enclosure_id
    ).all()

    total_translucent_area: float = 0.0
    windows_data: List[Dict[str, Any]] = []

    for window in windows:
        try:
            # Calcular el área total de la ventana (se asume que high y broad son numéricos)
            high_value = float(getattr(window, "high", 0))
            broad_value = float(getattr(window, "broad", 0))
            area_total = high_value * broad_value
        except Exception as e:
            high_value = 0.0
            broad_value = 0.0
            area_total = 0.0

        # Consultar la tabla Elements usando window_id y type=="window"
        element = db.query(Element).filter(
            Element.id == getattr(window, "window_id", None),
            Element.type == "window"
        ).first()

        # Si se encuentra el elemento, extraer fm; si no, asumir fm=0
        fm = getattr(element, "fm", 0) if element else 0

        # Calcular el área traslúcida de la ventana:
        # A_translucida = area_total * (1 - 2 * fm)
        area_marco = area_total * (1 - fm)
        translucent_area = area_total - area_marco

        # Acumular el área traslúcida
        total_translucent_area += translucent_area

        windows_data.append({
            "window_enclosure_id": getattr(window, "id", None),
            "area_total": area_total,
            "translucent_area": translucent_area,
            "fm": fm
        })

    return {
        "Componente": "Window",
        "orientacion": "VE",
        "area": total_translucent_area,
        "Class Distribution": "D",
        "T_EXT": "TE"
    }


def _group_by_enclosure(raw: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    """
    Convierte una lista de objetos que incluyen 'enclosure_id' en un
    diccionario {enclosure_id: [objetos…]} manteniendo los objetos tal cual.
    """
    grouped: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for item in raw:
        encl_id = item.get("enclosure_id")
        if encl_id is not None:
            grouped[encl_id].append(item)
    return dict(grouped)


def get_material_details_by_enclosure(enclosure_id: int, current_user: dict, db: Session) -> List[Dict[str, Any]]:
    """
    Para un solo recinto (enclosure_id), retorna los detalles de materiales igual que la función original pero solo para ese recinto.
    """
    results: List[Dict[str, Any]] = []

    enclosure = db.query(EnclosureGenerals).filter(EnclosureGenerals.id == enclosure_id).first()
    if not enclosure:
        print(f"Advertencia: No se encontró el recinto con id {enclosure_id}.")
        return results

    project_id = getattr(enclosure, "project_id", 0)

    default_material_info = {
        "name": "",
        "p": 0,  # densidad
        "lambda": 0,  # conductividad
        "c": 0  # calor específico
    }

    tabla_records = db.query(TablaPy).filter(
        TablaPy.enclosure_id == enclosure_id,
        TablaPy.type.in_(["muro", "techo", "piso"])
    ).all()

    for record in tabla_records:
        computed_detail_id = None
        if record.type == "muro":
            wall = db.query(WallEnclosure).filter(
                WallEnclosure.id == record.item_id,
                WallEnclosure.enclosure_id == enclosure_id
            ).first()
            if wall:
                computed_detail_id = getattr(wall, "wall_id", None)
            else:
                print(f"Advertencia: No se encontró WallEnclosure para item_id {record.item_id} en recinto {enclosure_id}.")
                continue
        elif record.type == "techo":
            techo = db.query(RoofEnclosure).filter(
                RoofEnclosure.id == record.item_id,
                RoofEnclosure.enclosure_id == enclosure_id
            ).first()
            if techo:
                computed_detail_id = getattr(techo, "roof_id", None)
            else:
                print(f"Advertencia: No se encontró RoofEnclosure para item_id {record.item_id} en recinto {enclosure_id}.")
                continue
        elif record.type == "piso":
            piso = db.query(FloorEnclosure).filter(
                FloorEnclosure.id == record.item_id,
                FloorEnclosure.enclosure_id == enclosure_id
            ).first()
            if piso:
                computed_detail_id = getattr(piso, "floor_id", None)
            else:
                print(f"Advertencia: No se encontró FloorEnclosure para item_id {record.item_id} en recinto {enclosure_id}.")
                continue

        detail_part_name = ""
        if computed_detail_id is not None:
            dp = db.query(DetailPart).filter(
                DetailPart.id == computed_detail_id,
                DetailPart.project_id == project_id
            ).first()
            if dp:
                detail_part_name = getattr(dp, "name_detail", "")
            else:
                detail_part_name = ""
                continue
        else:
            print("Advertencia: No se pudo determinar un id para DetailPart; se asignará cadena vacía.")
            detail_part_name = ""
            continue

        details_records = db.query(Detail).filter(
            Detail.name_detail == detail_part_name,
            Detail.project_id == project_id,
            Detail.is_deleted == False
        ).all()
        print(f"details_records: {details_records}")
        if not details_records:
            default_scantilon = {"muro": "Muro", "techo": "Techo", "piso": "Piso"}.get(record.type, "")
            details_records = [{
                "id": 0,
                "material_id": 0,
                "is_deleted": False,
                "scantilon_location": default_scantilon,
                "name_detail": "",
                "layer_thickness": 0,
                "project_id": 0,
                "created_status": "created"
            }]
            continue

        constants = db.query(Constant).filter(
            Constant.name == "generals",
            Constant.type == "details"
        ).first()

        f_ref = constants.atributs["Fourier"]["F_ref"]
        dt_fourier = constants.atributs["Fourier"]["dt_Fourier"]

        for d in details_records:
            if isinstance(d, dict):
                material_id = d.get("material_id", 0)
                layer_thickness = d.get("layer_thickness", 0)
            else:
                material_id = getattr(d, "material_id", 0)
                layer_thickness = getattr(d, "layer_thickness", 0)

            d_value = layer_thickness / 100

            if material_id and material_id != 0:
                const_record = db.query(Constant).filter(
                    Constant.id == material_id,
                    Constant.type == "definition materials",
                    Constant.name == "materials"
                ).first()
                if const_record:
                    const_atributs = const_record.atributs
                    material_info = {
                        "name": const_atributs.get("name", ""),
                        "p": const_atributs.get("density", 0),  # densidad -> p
                        "lambda": const_atributs.get("conductivity", 0),  # conductividad -> lambda
                        "c": const_atributs.get("specific_heat", 0)  # calor específico -> c
                    }
                else:
                    material_info = default_material_info.copy()
            else:
                material_info = default_material_info.copy()

            material_info["d"] = d_value
            conductivity = material_info.get("lambda", 0)
            R_value = d_value / conductivity if conductivity != 0 else 0
            material_info["R"] = R_value
            original_orientation = getattr(record, "orientation", "ND") or "ND"
            mapped_orientation = ORIENTATION_MAPPING.get(original_orientation, original_orientation)

            try:
                denominador = (material_info["lambda"] / (material_info["p"] * material_info["c"])) * (
                            dt_fourier / (material_info["d"] ** 2))
                if denominador == 0:
                    Nd_val = 0
                else:
                    valor = math.sqrt(f_ref / denominador) + 0.999999
                    Nd_val = int(valor)
                    Nd_val = max(1, Nd_val)
            except Exception as e:
                Nd_val = 0
            material_info["Nd"] = Nd_val

            output_obj = {
                "enclosure_id": enclosure_id,
                "orientation": original_orientation,
                "capa": mapped_orientation,
                "material_info": material_info,
                "R": R_value
            }
            results.append(output_obj)

    return results


def get_material_details_by_project(project_id: int, current_user: dict, db: Session) -> List[Dict[str, Any]]:
    """
    Para cada recinto (EnclosureGenerals) del proyecto (project_id) y, por cada registro en TablaPy (tipo 'muro', 'techo' o 'piso'):
      1. Se valida que el recinto pertenezca al proyecto indicado.
      2. Se consulta la tabla correspondiente (WallEnclosure, RoofEnclosure o FloorEnclosure) para obtener
         el identificador (wall_id, roof_id o floor_id) que se usará para consultar DetailPart.
      3. Con ese identificador se consulta DetailPart para obtener el name_detail.
      4. Se consulta la tabla Detail usando el name_detail y el project_id.
         Si no se encuentran registros, se usa un objeto por defecto con layer_thickness en 0.
      5. Por cada registro de Detail se utiliza su material_id para obtener la información
         del material desde la tabla Constant filtrando por:
             - id = material_id
             - type = "definition materials"
             - name = "materials"
         La información del material se renombra de la siguiente forma:
             - density  -> p
             - conductivity -> lambda
             - specific_heat -> c
      6. Se calcula:
             d = layer_thickness / 100
         y se guarda en material_info bajo la clave "d".
      7. Se calcula R = d / material_info["lambda"] (controlando división por cero)
         y se retorna en la clave "R".
      8. Finalmente, se retorna una lista de objetos que contienen:
             - "enclosure_id": identificador del recinto procesado.
             - "orientation": la orientación original (del registro de TablaPy)
             - "capa": la conversión de la orientación según ORIENTATION_MAPPING
             - "material_info": la información del material con sus claves renombradas y agregada "d"
             - "R": el valor calculado.
    """
    results: List[Dict[str, Any]] = []

    # 1. Obtener todos los recintos (enclosures) del proyecto
    enclosures = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.project_id == project_id).all()
    if not enclosures:
        print(
            f"Advertencia: No se encontraron recintos para project_id {project_id}.")
        return results

    # Objeto por defecto para material_info con claves renombradas
    default_material_info = {
        "name": "",
        "p": 0,  # densidad
        "lambda": 0,  # conductividad
        "c": 0  # calor específico
    }

    # Iterar sobre cada recinto del proyecto
    for enclosure in enclosures:
        enclosure_id = getattr(enclosure, "id", None)
        # Consultar TablaPy para los tipos deseados
        tabla_records = db.query(TablaPy).filter(
            TablaPy.enclosure_id == enclosure_id,
            TablaPy.type.in_(["muro", "techo", "piso"])
        ).all()

        for record in tabla_records:
            computed_detail_id = None
            if record.type == "muro":
                wall = db.query(WallEnclosure).filter(
                    WallEnclosure.id == record.item_id,
                    WallEnclosure.enclosure_id == enclosure_id
                ).first()
                if wall:
                    computed_detail_id = getattr(wall, "wall_id", None)
                else:
                    print(
                        f"Advertencia: No se encontró WallEnclosure para item_id {record.item_id} en recinto {enclosure_id}.")
            elif record.type == "techo":
                techo = db.query(RoofEnclosure).filter(
                    RoofEnclosure.id == record.item_id,
                    RoofEnclosure.enclosure_id == enclosure_id
                ).first()
                if techo:
                    computed_detail_id = getattr(techo, "roof_id", None)
                else:
                    print(
                        f"Advertencia: No se encontró RoofEnclosure para item_id {record.item_id} en recinto {enclosure_id}.")
            elif record.type == "piso":
                piso = db.query(FloorEnclosure).filter(
                    FloorEnclosure.id == record.item_id,
                    FloorEnclosure.enclosure_id == enclosure_id
                ).first()
                if piso:
                    computed_detail_id = getattr(piso, "floor_id", None)
                else:
                    print(
                        f"Advertencia: No se encontró FloorEnclosure para item_id {record.item_id} en recinto {enclosure_id}.")

            detail_part_name = ""
            if computed_detail_id is not None:
                dp = db.query(DetailPart).filter(
                    DetailPart.id == computed_detail_id,
                    DetailPart.project_id == project_id
                ).first()
                if dp:
                    detail_part_name = getattr(dp, "name_detail", "")
                else:
                    detail_part_name = ""
                    continue
            else:
                print(
                    "Advertencia: No se pudo determinar un id para DetailPart; se asignará cadena vacía.")
                detail_part_name = ""
            details_records = db.query(Detail).filter(
                Detail.name_detail == detail_part_name,
                Detail.project_id == project_id,
                Detail.is_deleted == False
            ).all()
            if not details_records:
                default_scantilon = {
                    "muro": "Muro", "techo": "Techo", "piso": "Piso"}.get(record.type, "")
                details_records = [{
                    "id": 0,
                    "material_id": 0,
                    "is_deleted": False,
                    "scantilon_location": default_scantilon,
                    "name_detail": "",
                    "layer_thickness": 0,
                    "project_id": 0,
                    "created_status": "created"
                }]
            constants = db.query(Constant).filter(
                Constant.name == "generals",
                Constant.type == "details"
            ).first()

            f_ref = constants.atributs["Fourier"]["F_ref"]
            dt_fourier = constants.atributs["Fourier"]["dt_Fourier"]

            for d in details_records:
                if isinstance(d, dict):
                    material_id = d.get("material_id", 0)
                    layer_thickness = d.get("layer_thickness", 0)
                else:
                    material_id = getattr(d, "material_id", 0)
                    layer_thickness = getattr(d, "layer_thickness", 0)

                d_value = layer_thickness / 100

                if material_id and material_id != 0:
                    const_record = db.query(Constant).filter(
                        Constant.id == material_id,
                        Constant.type == "definition materials",
                        Constant.name == "materials"
                    ).first()
                    if const_record:
                        const_atributs = const_record.atributs
                        material_info = {
                            "name": const_atributs.get("name", ""),
                            # densidad -> p
                            "p": const_atributs.get("density", 0),
                            # conductividad -> lambda
                            "lambda": const_atributs.get("conductivity", 0),
                            # calor específico -> c
                            "c": const_atributs.get("specific_heat", 0)
                        }
                    else:
                        material_info = default_material_info.copy()
                else:
                    material_info = default_material_info.copy()

                material_info["d"] = d_value
                conductivity = material_info.get("lambda", 0)
                R_value = d_value / conductivity if conductivity != 0 else 0
                material_info["R"] = R_value
                original_orientation = getattr(
                    record, "orientation", "ND") or "ND"
                mapped_orientation = ORIENTATION_MAPPING.get(
                    original_orientation, original_orientation)

                try:
                    denominador = (material_info["lambda"] / (material_info["p"] * material_info["c"])) * (
                        dt_fourier / (material_info["d"] ** 2))
                    if denominador == 0:
                        Nd_val = 0
                    else:
                        valor = math.sqrt(f_ref / denominador) + 0.999999
                        Nd_val = int(valor)
                        Nd_val = max(1, Nd_val)
                except Exception as e:
                    Nd_val = 0
                material_info["Nd"] = Nd_val

                output_obj = {
                    "enclosure_id": enclosure_id,
                    "orientation": original_orientation,
                    "capa": mapped_orientation,
                    "material_info": material_info,
                    "R": R_value
                }
                results.append(output_obj)

    return _group_by_enclosure(results)


def get_nodos_area_by_orientation_by_enclosure(enclosure_id: int, db: Session, current_user: dict = None):
    """
    Para un solo recinto (enclosure_id), devuelve un DataFrame con todas las orientaciones del ORIENTATION_MAPPING ordenadas,
    incluyendo aquellas sin datos, usando el valor máximo de nodos_area si existe.
    """
    import pandas as pd
    enclosure = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.id == enclosure_id).first()
    if not enclosure:
        print(f"Advertencia: No se encontró el recinto con id {enclosure_id}.")
        return pd.DataFrame()

    grouped: Dict[str, Dict[str, Any]] = {
        ori: {
            "Componente": comp,
            "Orientacion": ori,
            "Area": 0,
            # Absorcion intentionally omitted
            "Temperatura_Exterior": TEMPERATURA_EXTERIOR_MAPPING.get(ori, "NORMAL"),
            "Temperatura": TEMPERATURA_INTERIOR_MAPPING.get(ori, "NORMAL")        }
        for ori, comp in ORIENTATION_MAPPING.items()
    }

    tabla_records = db.query(TablaPy).filter(
        TablaPy.enclosure_id == enclosure_id,
        TablaPy.type.in_(["muro", "techo", "piso"])
    ).all()

    for record in tabla_records:
        orientation = getattr(record, "orientation", "ND") or "ND"
        if orientation not in ORIENTATION_MAPPING:
            continue
        
        record_type = getattr(record, "type", "")
        item_id = getattr(record, "item_id", None)
        nodos_area = getattr(record, "nodos_area", 0) or 0
        
        # Solo sumar el área si se encuentra el registro correspondiente en su tabla específica
        area_to_add = 0
        if record_type == "muro":
            wall = db.query(WallEnclosure).filter(
                WallEnclosure.id == item_id,
                WallEnclosure.enclosure_id == enclosure_id
            ).first()
            if wall:
                area_to_add = nodos_area
        elif record_type == "techo":
            roof = db.query(RoofEnclosure).filter(
                RoofEnclosure.id == item_id,
                RoofEnclosure.enclosure_id == enclosure_id
            ).first()
            if roof:
                area_to_add = nodos_area
        elif record_type == "piso":
            floor = db.query(FloorEnclosure).filter(
                FloorEnclosure.id == item_id,
                FloorEnclosure.enclosure_id == enclosure_id
            ).first()
            if floor:
                area_to_add = nodos_area
        
        # Sumar el área (será 0 si no se encontró el registro correspondiente)
        grouped[orientation]["Area"] += area_to_add

    df = pd.DataFrame([grouped[ori] for ori in ORIENTATION_MAPPING.keys()])
    return df


def get_enclosures_by_project(project_id: int, db: Session, current_user: dict = None) -> List[EnclosureGenerals]:
    """
    Obtiene todos los recintos (enclosures) de un proyecto específico.
    :param project_id: ID del proyecto.
    :param db: Sesión de base de datos (SQLAlchemy Session).
    :return: Lista de recintos.
    """
    enclosures = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.project_id == project_id).all()
    if not enclosures:
        print(
            f"Advertencia: No se encontraron recintos para project_id {project_id}.")
        raise Exception(
            f"No se encontraron recintos para project_id {project_id}.")

    return enclosures


def get_nodos_area_by_orientation_by_project(project_id: int, db: Session, current_user: dict = None) -> List[
        Dict[str, Any]]:
    """
    Para cada recinto (EnclosureGenerals) del proyecto y sus registros en TablaPy (tipos 'muro', 'techo' o 'piso'):
      1. Se agrupan los registros por el campo "orientation" (por recinto) tomando el primer registro de cada grupo.
      2. Se extrae el valor "nodos_area" y otros atributos (como nodos_emisividad).
      3. Se asigna la conversión de orientación a través de ORIENTATION_MAPPING,
         y las temperaturas exterior e interior usando TEMPERATURA_EXTERIOR_MAPPING y TEMPERATURA_INTERIOR_MAPPING respectivamente.
      4. Se retorna una lista de objetos que contienen:
           - "enclosure_id": identificador del recinto.
           - "Orientacion": la orientación original.
           - "Componente": la conversión de la orientación.
           - "Absorcion": valor extraído (nodos_emisividad).
           - "Area": nodos_area.
           - "Temperatura_Exterior": temperatura asignada según el mapeo exterior.
           - "Temperatura": temperatura interior asignada.
    """
    results: List[Dict[str, Any]] = []

    # Obtener todos los recintos del proyecto
    enclosures = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.project_id == project_id).all()
    if not enclosures:
        print(
            f"Advertencia: No se encontraron recintos para project_id {project_id}.")
        return results    # Por cada recinto, agrupar por orientación y sumar las áreas
    for enclosure in enclosures:
        enclosure_id = getattr(enclosure, "id", None)
        tabla_records = db.query(TablaPy).filter(
            TablaPy.enclosure_id == enclosure_id,
            TablaPy.type.in_(["muro", "techo", "piso"])
        ).all()

        # Agrupar por orientación y sumar las áreas
        orientation_data: Dict[str, Dict[str, Any]] = {}
        
        for record in tabla_records:
            orientation = getattr(record, "orientation", "ND") or "ND"
            record_type = getattr(record, "type", "")
            item_id = getattr(record, "item_id", None)
            nodos_area = getattr(record, "nodos_area", 0) or 0
            nodos_emisividad = getattr(record, "nodos_emisividad", 0) or 0
            
            # Verificar si el registro existe en la tabla correspondiente
            area_to_add = 0
            absorcion_to_add = 0
            
            if record_type == "muro":
                wall = db.query(WallEnclosure).filter(
                    WallEnclosure.id == item_id,
                    WallEnclosure.enclosure_id == enclosure_id
                ).first()
                if wall:
                    area_to_add = nodos_area
                    absorcion_to_add = nodos_emisividad
            elif record_type == "techo":
                roof = db.query(RoofEnclosure).filter(
                    RoofEnclosure.id == item_id,
                    RoofEnclosure.enclosure_id == enclosure_id
                ).first()
                if roof:
                    area_to_add = nodos_area
                    absorcion_to_add = nodos_emisividad
            elif record_type == "piso":
                floor = db.query(FloorEnclosure).filter(
                    FloorEnclosure.id == item_id,
                    FloorEnclosure.enclosure_id == enclosure_id
                ).first()
                if floor:
                    area_to_add = nodos_area
                    absorcion_to_add = nodos_emisividad
            
            # Inicializar o actualizar los datos de la orientación
            if orientation not in orientation_data:
                mapped_orientation = ORIENTATION_MAPPING.get(orientation, orientation)
                temperatura_exterior = TEMPERATURA_EXTERIOR_MAPPING.get(orientation, "NORMAL")
                temperatura = TEMPERATURA_INTERIOR_MAPPING.get(orientation, "NORMAL")
                
                orientation_data[orientation] = {
                    "enclosure_id": enclosure_id,
                    "Componente": mapped_orientation,
                    "Orientacion": orientation,
                    "Area": 0,
                    "Absorcion": 0,
                    "Temperatura_Exterior": temperatura_exterior,
                    "Temperatura": temperatura
                }
            
            # Sumar las áreas y absorción
            orientation_data[orientation]["Area"] += area_to_add
            orientation_data[orientation]["Absorcion"] += absorcion_to_add

        # Agregar los resultados de este recinto
        for orientation_result in orientation_data.values():
            results.append(orientation_result)

    return _group_by_enclosure(results)


def get_translucent_window_area_by_enclosure(enclosure_id: int, current_user: dict=None, db: Session=None):
    """
    Para un solo recinto (enclosure_id), calcula el área traslúcida de todas las ventanas
    y retorna un DataFrame con el resultado.
    """
    translucent_sum = 0
    windows: List[WindowEnclosure] = db.query(WindowEnclosure).filter(
        WindowEnclosure.enclosure_id == enclosure_id
    ).all()
    for window in windows:
        try:
            high_value = float(getattr(window, "high", 0))
            broad_value = float(getattr(window, "broad", 0))
            area_total = high_value * broad_value
        except Exception:
            area_total = 0.0
        element = db.query(Element).filter(
            Element.id == getattr(window, "window_id", None),
            Element.type == "window"
        ).first()
        fm = getattr(element, "fm", 0) if element else 0
        area_marco = area_total * (1 - fm)
        translucent_area = area_total - area_marco
        translucent_sum += translucent_area

    logger.info(f"Area translúcida para el recinto {enclosure_id}: {translucent_sum}")
    data = [{
        "Componente": "Window",
        "orientacion": "VE",
        "area": translucent_sum,
        "Class Distribution": "D",
        "T_EXT": "TE",
    }]
    return pd.DataFrame(data)


def get_translucent_window_area_by_project(project_id: int, current_user: dict, db: Session) -> List[Dict[str, Any]]:
    """
    Para cada recinto, se agrupan las ventanas y se suma su área traslúcida.
    Devuelve un solo objeto por recinto con la suma total del área traslúcida.
    """
    total_translucent_area: float = 0.0
    # clave: enclosure_id, valor: suma area translúcida
    enclosure_window_map: Dict[int, float] = {}

    enclosures = db.query(EnclosureGenerals).filter(
        EnclosureGenerals.project_id == project_id).all()
    if not enclosures:
        print(
            f"Advertencia: No se encontraron recintos para project_id {project_id}.")
        return [{
            "Componente": "Window",
            "orientacion": "VE",
            "area": total_translucent_area,
            "Class Distribution": "D",
            "T_EXT": "TE",
            "windows": []
        }]

    for enclosure in enclosures:
        enclosure_id = getattr(enclosure, "id", None)
        total_enclosure_area = 0.0

        windows: List[WindowEnclosure] = db.query(WindowEnclosure).filter(
            WindowEnclosure.enclosure_id == enclosure_id
        ).all()

        for window in windows:
            try:
                high_value = float(getattr(window, "high", 0))
                broad_value = float(getattr(window, "broad", 0))
                area_total = high_value * broad_value
            except Exception:
                area_total = 0.0

            element = db.query(Element).filter(
                Element.id == getattr(window, "window_id", None),
                Element.type == "window"
            ).first()
            fm = getattr(element, "fm", 0) if element else 0

            area_marco = area_total * (1 - fm)
            translucent_area = area_total - area_marco

            total_enclosure_area += translucent_area

        enclosure_window_map[enclosure_id] = total_enclosure_area
        total_translucent_area += total_enclosure_area

    # Generar la lista de resultados
    windows_data: List[Dict[str, Any]] = []
    for enclosure_id, translucent_sum in enclosure_window_map.items():
        windows_data.append({
            "enclosure_id": enclosure_id,
            "Componente": "Window",
            "orientacion": "VE",
            "area": translucent_sum,
            "Class Distribution": "D",
            "T_EXT": "TE",
        })

    return _group_by_enclosure(windows_data)
