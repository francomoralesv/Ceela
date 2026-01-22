import pandas as pd
from sqlalchemy.orm import Session
from src.models.entity.thermal_bridge_general import ThermalBridge

def thermal_bridges_from_excel(file_path: str, db: Session):
    """
    Lee el Excel y realiza inserciones masivas en la tabla ThermalBridge.
    
    Se espera que el Excel tenga la hoja "0.Puentes Térmicos" con los datos organizados
    en columnas que incluyen (por ejemplo, luego de la cabecera a dos niveles):
      - "Code PT"
      - "Type PT"
      - "Element 1"
      - "Element 2"
      - "Position Insulation"
      - "Insulation Thickness"
      - "Return Insulation"
      - "Position Window"
      - "Value PT"
    
    Se leen los datos desde la fila 4 (donde inicia la cabecera de dos filas) hasta la fila 1770.
    """

    # Evitar inserciones duplicadas si ya existen registros en ThermalBridge
    if db.query(ThermalBridge).first() is not None:
        print("Los datos ya han sido insertados previamente. Saltando seed.")
        return

    # Calcula la cantidad de filas a leer (desde la fila 4 hasta la 1770, se omiten las 3 primeras)

    # Leer el Excel sin usar 'usecols', y luego seleccionar las columnas deseadas
    df = pd.read_excel(
        file_path,
        sheet_name="0.Puentes Térmicos",
        engine="openpyxl",
        skiprows=range(0, 3),  # Omite las primeras 3 filas, haciendo que la fila 4 sea la primera leída
        header=[0, 1],         # Se leen dos filas de encabezado (fila 4 y 5)
        nrows=1767
    )

    # Selecciona las columnas desde la C hasta la K (índices 2 a 10)
    df = df.iloc[:, 2:11]

    # Aplanar el MultiIndex de columnas
    df.columns = [
        " ".join([str(item).strip() for item in col if str(item) != "nan"]).strip()
        for col in df.columns.values
    ]
    # Opcional: Verificar que el encabezado se haya aplanado correctamente
    # print(df.columns.tolist())

    # Preparar la data para ThermalBridge. Asegúrate de que los nombres de las columnas
    # coincidan con los encabezados aplanados del Excel.
    count = 0
    thermal_bridges_data = []
    for _, row in df.iterrows():
        thermal_bridges_data.append({
            "code_pt": row["Código PT"],
            "type_pt": row["Tipo PT"],
            "element_1": row["Elemento 1"],
            "element_2": row["Elemento 2"],
            "position_insulation": row["Posición Aislación"],
            "insulation_thickness": (row["Espesor Aislación"]) if not pd.isna(row["Espesor Aislación"]) else None,
            "return_insulation": (row["Retorno Aislación"]) if not pd.isna(row["Retorno Aislación"]) else None,
            "position_window": (row["Posición Ventana"]) if not pd.isna(row["Posición Ventana"]) else None,
            "value_pt": (row["Valor PT"]) if not pd.isna(row["Valor PT"]) else None,
        })
        count += 1

    print("Longituda", len(thermal_bridges_data))
    print("Cuentasss: ", count)
    # Inserción masiva de ThermalBridge
    db.bulk_insert_mappings(ThermalBridge, thermal_bridges_data)
    db.commit()

    print("Seed realizado con éxito desde el Excel.")