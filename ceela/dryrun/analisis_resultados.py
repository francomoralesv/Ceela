import numpy as np
import pandas as pd

def calcular_demanda_refrigeracion_calefaccion(path_output_simple):
    """
    Calcula la demanda de refrigeración y calefacción a partir del archivo .output_simple.txt generado por ejecutable_iso.
    Retorna un diccionario con la demanda total de calefacción y refrigeración.
    """
    df = pd.read_csv(path_output_simple, sep='\s+', skip_blank_lines=True)
    if 'Demanda' in df.columns:
        demanda_neta = pd.to_numeric(df['Demanda'], errors='coerce')
    else:
        demanda_neta = pd.to_numeric(df.iloc[:, 7], errors='coerce')  # Ajusta si la columna cambia
    demanda_neta = demanda_neta.dropna()
    demanda_calefaccion = demanda_neta[demanda_neta > 0].sum()
    demanda_refrigeracion = -demanda_neta[demanda_neta < 0].sum()
    print(f"Demanda calefacción: {demanda_calefaccion:.2f} kWh")
    print(f"Demanda refrigeración: {demanda_refrigeracion:.2f} kWh")
    return {
        'calefaccion': demanda_calefaccion,
        'refrigeracion': demanda_refrigeracion
    }

def calcular_horas_disconfort(path_output_simple, t_min=20, t_max=26):
    """
    Calcula las horas de disconfort térmico a partir del archivo .output_simple.txt.
    t_min y t_max definen el rango de confort (°C).
    Retorna el número de horas fuera del rango de confort.
    """
    df = pd.read_csv(path_output_simple, sep='\s+', skip_blank_lines=True)
    df.head(8760)
    if 'Temperatura_operativa_con_clima' in df.columns:
        temp_operativa = pd.to_numeric(df['Temperatura_operativa_con_clima'], errors='coerce')
    else:
        temp_operativa = pd.to_numeric(df.iloc[:, 6], errors='coerce')  # Ajusta si la columna cambia
    temp_operativa = temp_operativa.dropna()
    horas_disconfort = ((temp_operativa < t_min) | (temp_operativa > t_max)).sum()
    print(f"Horas de disconfort: {horas_disconfort}")
    return int(horas_disconfort)
