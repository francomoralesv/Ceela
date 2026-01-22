import pandas as pd
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.entity.constant import Constant  # Ajusta la ruta a tu modelo

def create_azimut_constants(file_path: str, db: Session):
    """
    Lee el Excel y almacena la tabla de Azimut/Orientaciones en la tabla 'constants'
    dentro del campo 'atributs', en formato JSON.
    """
    try:
        # Definir el identificador único del conjunto de datos
        name_value = "Azimut Table"
        type_value = "orientation"

        # Verificar si ya existe el registro en la base de datos
        existing_constant = db.query(Constant).filter(
            Constant.name == name_value,
            Constant.type == type_value
        ).first()

        # Si el registro ya existe, detener la ejecución
        if existing_constant:
            return {
                "message": "El conjunto de datos ya existe. No se realizaron cambios.",
                "status": "skipped"
            }

        # Si no existe, leer el archivo Excel y almacenar los datos
        df = pd.read_excel(
            file_path,
            sheet_name="0. Tablas referencia",  # Ajusta el nombre de la hoja si es diferente
            engine="openpyxl",
            skiprows=9,      # Se saltan las primeras 9 filas; fila 10 se toma como cabecera
            usecols="AD:AF", # Lee las columnas AD, AE y AF
            nrows=19         # Lee la cabecera + 18 filas (de la fila 10 a la 28)
        )
        
        # Renombrar columnas
        df.columns = ["range_az", "orientation", "azimut_360"]
        
        # Omitir la primera fila de datos, que se asume vacía
        df = df.iloc[1:]
        
        # Eliminar filas con valores NaN en "range_az"
        df = df[df["range_az"].notna()]
        
        # Convertir el DataFrame a una lista de diccionarios
        data_rows = df.to_dict(orient="records")

        # Crear un nuevo registro en 'constants'
        new_constant = Constant(
            name=name_value,
            type=type_value,
            atributs={"orientations": data_rows}
        )
        db.add(new_constant)

        # Confirmar la transacción
        db.commit()

        return {
            "message": "Azimut/Orientaciones creados correctamente.",
            "total_rows": len(data_rows),
            "status": "created"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el archivo Excel: {str(e)}"
        )
