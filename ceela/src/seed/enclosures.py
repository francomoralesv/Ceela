import pandas as pd
from sqlalchemy.orm import Session
from src.models.entity.enclosure import Enclosure
from sqlalchemy.exc import SQLAlchemyError

def create_enclosures_default(file_path: str, db: Session):
    """
    Inserta en la tabla `enclosures` los perfiles de ocupación del Excel
    (sheet "2. Perfiles de ocupacion"), evitando duplicados sobre `code`
    y generando un `code_ifc` secuencial con prefijo 'pl_'.
    """
    try:
        # 1) Leer el Excel
        df = pd.read_excel(
            file_path,
            sheet_name="2. Perfiles de ocupacion",
            engine="openpyxl",
            skiprows=12,
            usecols="V:W",
            nrows=30
        )
        df.columns = ["code", "name"]

        # 2) Códigos ya existentes en la tabla
        existing_codes = {c for (c,) in db.query(Enclosure.code).all()}

        # 3) Preparar lista filtrada de nuevos recintos
        to_insert = [
            {"code": row["code"], "name": row["name"]}
            for row in df.to_dict(orient="records")
            if row["code"] not in existing_codes
        ]
        if not to_insert:
            return {"message": "No hay recintos nuevos para insertar."}

        # 4) Calcular el siguiente número para code_ifc (prefijo 'pl_')
        existing_ifcs = db.query(Enclosure.code_ifc).filter(
            Enclosure.code_ifc.like(r"OCP\_%")
        ).all()
        nums = [
            int(ifc.split("_")[1])
            for (ifc,) in existing_ifcs
            if ifc and "_" in ifc and ifc.split("_")[1].isdigit()
        ]
        next_num = max(nums) + 1 if nums else 1

        # 5) Construir mappings con code_ifc y created_status
        new_enclosures = []
        for rec in to_insert:
            code_ifc = f"OCP_{next_num:03d}"
            next_num += 1
            new_enclosures.append({
                "code": rec["code"],
                "name": rec["name"],
                "code_ifc": code_ifc,
                "created_status": "default",
                "user_id": None
            })

        # 6) Bulk insert
        db.bulk_insert_mappings(Enclosure, new_enclosures)
        db.commit()
        return {"message": f"{len(new_enclosures)} recintos nuevos creados correctamente."}

    except SQLAlchemyError as e:
        db.rollback()
        return {"error": f"Error al insertar recintos: {e}"}
    except Exception as e:
        db.rollback()
        return {"error": f"Error al procesar el archivo: {e}"} 

    
    


    