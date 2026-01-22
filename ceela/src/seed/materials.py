import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.models.entity.constant import Constant

def create_materials_from_excel(file_path: str, db: Session):
    # 1) Carga el Excel
    df = pd.read_excel(
        file_path,
        sheet_name="1. Materiales",
        engine="openpyxl",
        skiprows=10,
        usecols="B:E",
        nrows=33
    )

    # 2) Prepara listas de datos (saltando la cabecera)
    materials       = [str(v).strip() for v in df["Nombre "][1:]]
    conductivities  = [float(v)      for v in df["Conductividad"][1:]]
    specific_heats  = [float(v)      for v in df["Calor especifico"][1:]]
    densities       = [float(v)      for v in df["densidad"][1:]]

    # 3) Detecta materiales ya existentes (por nombre)
    existing_names = {
        mat.atributs["name"]
        for mat in db.query(Constant).filter(Constant.type == "definition materials").all()
    }

    # 4) Calcula el siguiente número para code_ifc
    #    Busca todos los code_ifc que empiecen por 'mat_'
    existing_codes = db.query(Constant.code_ifc).filter(
        Constant.type == "definition materials",
        Constant.code_ifc.like(r"MATERIAL\_%")
    ).all()
    existing_nums = [
        int(code.split("_")[1])
        for (code,) in existing_codes
        if code and "_" in code and code.split("_")[1].isdigit()
    ]
    next_code_num = max(existing_nums) + 1 if existing_nums else 1

    # 5) Arma la lista de mappings a insertar
    new_materials = []
    for i, name in enumerate(materials):
        if name in existing_names:
            print(f"El material '{name}' ya existe en la base de datos.")
            continue

        code_ifc = f"MATERIAL_{next_code_num:03d}"
        next_code_num += 1

        new_materials.append({
            "type": "definition materials",
            "create_status": "default",
            "name": "materials",
            "code_ifc": code_ifc,
            "atributs": {
                "name":          name,
                "conductivity":  conductivities[i],
                "specific_heat": specific_heats[i],
                "density":       densities[i]
            }
        })

    # 6) Inserta en bloque
    if new_materials:
        try:
            db.bulk_insert_mappings(Constant, new_materials)
            db.commit()
            print(f"{len(new_materials)} materiales creados exitosamente.")
        except Exception as e:
            db.rollback()
            print(f"Error al insertar materiales: {e}")
    else:
        print("No hay materiales nuevos para insertar.")