import pandas as pd
from sqlmodel import Session
from src.models.entity.regiones_comunas import Region, Comuna  # Ajusta el import según tu estructura

def regiones_from_excel(file_path: str, db: Session):
    """
    Lee el Excel y realiza inserciones masivas de Regiones y Comunas, 
    asegurando que los datos se inserten una sola vez.

    Se espera que el Excel tenga la hoja "0. Tablas referencia" con datos en el rango
    L11:U256 y que los encabezados sean (entre otros):
      - "Región"
      - "Comuna"
      - "Latitud"
      - "Longitud"
      - "Zonas térmicas", "Unnamed: 14", "Unnamed: 15" 
         (estas tres columnas conforman la información de zonas térmicas)

    Se agrega la comuna "La Cisterna" en cada región con zonas_termicas = ["D"].
    """
    # Verifica si ya existen datos en la tabla de Region para evitar inserciones duplicadas
    if db.query(Region).first() is not None:
        print("Los datos ya han sido insertados previamente. Saltando seed.")
        return

    # Se leen las columnas desde L hasta U para capturar todas las columnas de zonas térmicas
    df = pd.read_excel(
        file_path,
        sheet_name="0. Tablas referencia",
        engine="openpyxl",
        skiprows=9,          # Fila 10 será fdla cabecera
        usecols="L:U",        # Columnas L a U
        nrows=246             # Desde la fila 10 hasta la 256 (inclusive)
    )
    
    # Combina las columnas de zonas térmicas en una sola columna, omitiendo valores "0"
    def combine_zones(row):
        zonas = []
        # Para cada columna, se verifica que no sea nula y que el valor (como string) no sea "0"
        if pd.notnull(row.get("Zonas térmicas")):
            valor = str(row["Zonas térmicas"]).strip()
            if valor != "0":
                zonas.append(valor)
        if "Unnamed: 14" in row and pd.notnull(row.get("Unnamed: 14")):
            valor = str(row["Unnamed: 14"]).strip()
            if valor != "0":
                zonas.append(valor)
        if "Unnamed: 15" in row and pd.notnull(row.get("Unnamed: 15")):
            valor = str(row["Unnamed: 15"]).strip()
            if valor != "0":
                zonas.append(valor)
        return zonas

    # Crear nueva columna combinada
    df["Zonas Térmicas Combinadas"] = df.apply(combine_zones, axis=1)
    
    # 1. Extraemos las regiones únicas y generamos un mapeo para asignar IDs manualmente.
    regiones_unicas = df["Región"].dropna().unique().tolist()
    regiones_unicas.sort()  # Opcional: para ordenar alfabéticamente
    region_mapping = {region: idx + 1 for idx, region in enumerate(regiones_unicas)}
    
    # Preparamos los datos para la tabla de Regiones
    regiones_data = [
        {"id": region_mapping[region], "nombre_region": region}
        for region in regiones_unicas
    ]
    
    # Inserción masiva de Regiones
    db.bulk_insert_mappings(Region, regiones_data)
    db.commit()
    
    # 2. Preparamos los datos para la tabla de Comunas leyendo cada fila del Excel
    comunas_data = []
    for _, row in df.iterrows():
        region = row["Región"]
        comuna = row["Comuna"]
        lat = row["Latitud"] if not pd.isna(row["Latitud"]) else None
        lon = row["Longitud"] if not pd.isna(row["Longitud"]) else None
        
        comunas_data.append({
            "nombre_comuna": comuna,
            "latitud": lat,
            "longitud": lon,
            "zonas_termicas": row["Zonas Térmicas Combinadas"],
            "region_id": region_mapping.get(region)
        })
    
    # Inserción masiva de Comunas
    db.bulk_insert_mappings(Comuna, comunas_data)
    db.commit()
    
    print("Seed realizado con éxito desde el Excel.")
