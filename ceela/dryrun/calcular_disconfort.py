import pandas as pd
import sys

# Parámetros de confort (puedes ajustar estos valores)
UMBRAL_MIN = 20.0  # Temperatura mínima de confort (°C) para calefacción
UMBRAL_MAX = 25.0  # Temperatura máxima de confort (°C) para refrigeración

# Uso: python calcular_disconfort.py archivo.txt

def main():
    if len(sys.argv) < 2:
        print("Uso: python calcular_disconfort.py archivo.txt")
        sys.exit(1)

    archivo = sys.argv[1]

    # Leer el archivo, asumiendo que el separador es espacio y no hay encabezado
    columnas = [
        "ID_Recinto", "Hora", "Dia", "Mes", "Temperatura_exterior",
        "Temperatura_operativa_free_float", "Temperatura_operativa_con_clima",
        "Demanda", "Sol", "G_HU", "G_DHU", "x_int_aire"
    ]
    df = pd.read_csv(archivo, sep='\s+', names=columnas)

    # Tomar solo las primeras 8760 filas (primer año)
    df = df.head(8760)

    for col in ["Temperatura_operativa_free_float"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calefacción: temperatura operativa menor al umbral mínimo
    df['disconfort_calef'] = (df['Temperatura_operativa_free_float'] < UMBRAL_MIN).astype(int)
    # Refrigeración: temperatura operativa mayor al umbral máximo
    df['disconfort_ref'] = (df['Temperatura_operativa_free_float'] > UMBRAL_MAX).astype(int)

    horas_disconfort_calef = df['disconfort_calef'].sum()
    horas_disconfort_ref = df['disconfort_ref'].sum()

    print(f"Horas de disconfort por calefacción: {horas_disconfort_calef}")
    print(f"Horas de disconfort por refrigeración: {horas_disconfort_ref}")

if __name__ == "__main__":
    main()
