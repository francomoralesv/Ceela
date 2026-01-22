import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from src.models.entity.elements import Element
from src.services.calculator.calculation_parameters import calculate_element_door
from src.models.entity.constant import Constant

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

def create_elements_windows(file_path: str, db: Session):
    df = pd.read_excel(
        file_path,
        sheet_name="1. Materiales",
        engine="openpyxl",
        skiprows=10,
        nrows=10,
        usecols="BN:BT"
    )
    if df.empty:
        print("⚠️ No se encontraron datos en el archivo de materiales.")
        return

    # 1) Calcular el next_code para ventanas (prefijo 'vt')
    existing_codes = db.query(Element.code_ifc).filter(
        Element.type == "window",
        Element.code_ifc.like(r"VENTANA\_%")
    ).all()
    nums = [
        int(c.split("_")[1])
        for (c,) in existing_codes
        if c and "_" in c and c.split("_")[1].isdigit()
    ]
    next_code = max(nums) + 1 if nums else 1

    # 2) Preparar datos de columnas
    list_columns = df.columns[:7]
    list_detail = {
        header: df[header].iloc[1:].astype(str).str.strip().tolist()
        for header in list_columns
    }

    existing_names = {
        row.name_element
        for row in db.query(Element.name_element)
                     .filter(Element.type == "window")
                     .all()
    }

    # 3) Construir los nuevos mappings, asignando code_ifc
    new_elements = []
    for i, name_element in enumerate(list_detail["Nombre .5"]):
        if name_element in existing_names:
            print(f"⚠️ El elemento '{name_element}' ya existe y será omitido.")
            continue

        code_ifc = f"VENTANA_{next_code:03d}"
        next_code += 1

        new_elements.append({
            "name_element": name_element,
            "type": "window",
            "code_ifc": code_ifc,
            "atributs": {
                "u_vidrio": float(list_detail["U Vidrio"][i]),
                "fs_vidrio": float(list_detail["FS Vidrio"][i]),
                "clousure_type": list_detail["Tipo"][i],
                "frame_type": list_detail["Tipo.1"][i]
            },
            "u_marco": list_detail["U Marco"][i],
            "fm": list_detail["FM"][i],
            "created_status": "default",
            "calculations": {}
        })

    # 4) Insertar en bloque
    if new_elements:
        try:
            db.bulk_insert_mappings(Element, new_elements)
            db.commit()
            print(f"✅ {len(new_elements)} ventanas agregadas correctamente.")
        except SQLAlchemyError as e:
            db.rollback()
            print(f"❌ Error al guardar ventanas: {e}")
    else:
        print("⚠️ No se agregaron nuevas ventanas.")


def create_elements_door(file_path: str, db: Session):
    df = pd.read_excel(
        file_path,
        sheet_name="1. Materiales",
        engine="openpyxl",
        skiprows=10,
        nrows=8,
        usecols="BV:CA"
    )
    if df.empty:
        print("⚠️ No se encontraron datos en el archivo de materiales.")
        return

    # 1) Calcular el next_code para puertas (prefijo 'pt')
    existing_codes = db.query(Element.code_ifc).filter(
        Element.type == "door",
        Element.code_ifc.like(r"PUERTA\_%")
    ).all()
    nums = [
        int(c.split("_")[1])
        for (c,) in existing_codes
        if c and "_" in c and c.split("_")[1].isdigit()
    ]
    next_code = max(nums) + 1 if nums else 1

    # 2) Preparar datos de columnas
    list_columns = df.columns[:6]
    list_detail = {
        header: df[header].iloc[1:].astype(str).str.strip().tolist()
        for header in list_columns
    }

    existing_names = {
        row.name_element
        for row in db.query(Element.name_element)
                     .filter(Element.type == "door")
                     .all()
    }

    # Cargar ventanas para lookup de ventana_id
    windows = db.query(Element).filter(Element.type == "window").all()

    # 3) Construir los nuevos mappings, asignando code_ifc
    new_elements = []
    for i, name_element in enumerate(list_detail["Nombre .6"]):
        if name_element in existing_names:
            print(f"⚠️ El elemento '{name_element}' ya existe y será omitido.")
            continue

        code_ifc = f"PUERTA_{next_code:03d}"
        next_code += 1

        # buscar ventana por nombre
        vid = list_detail["Vidrio"][i]
        ventana_id = next(
            (w.id for w in windows if w.name_element == vid),
            None
        )

        new_elements.append({
            "name_element": name_element,
            "type": "door",
            "code_ifc": code_ifc,
            "atributs": {
                "u_puerta_opaca": float(list_detail["U puerta"][i]),
                "ventana_id": ventana_id,
                "name_ventana": vid,
                "porcentaje_vidrio": float(list_detail["% vidrio"][i])
            },
            "u_marco": list_detail["U Marco.1"][i],
            "fm": list_detail["FM.1"][i],
            "created_status": "default",
            "calculations": {}
        })

    # 4) Insertar en bloque
    if new_elements:
        try:
            db.bulk_insert_mappings(Element, new_elements)
            db.commit()
            print(f"✅ {len(new_elements)} puertas agregadas correctamente.")
        except SQLAlchemyError as e:
            db.rollback()
            print(f"❌ Error al guardar puertas: {e}")
    else:
        print("⚠️ No se agregaron nuevas puertas.")
