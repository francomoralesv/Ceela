import pandas as pd
import numpy as np
import os

def read_parquet_and_export_radiations(file_path):
    try:
        # Leer archivo parquet
        df = pd.read_parquet(file_path)

        # Columnas necesarias
        tiempo_col = 'Tiempo'
        ghi_col    = "Radiacion Global Horizontal[label: GHI] [W/m2]"
        dni_col    = "Radiacion Directa Normal[label: DNI] [W/m2]"
        dif_col    = "Radiacion Difusa[label: DIF] [W/m2]"

        for col in [tiempo_col, ghi_col, dni_col, dif_col]:
            if col not in df.columns:
                raise ValueError(f"Falta la columna requerida: {col}")

        # Convertir tiempo a datetime con zona horaria UTC
        if np.issubdtype(df[tiempo_col].dtype, np.number):
            df[tiempo_col] = pd.to_datetime(df[tiempo_col], unit='ms', utc=True)
        else:
            df[tiempo_col] = pd.to_datetime(df[tiempo_col], utc=True)
        df[tiempo_col] = df[tiempo_col].dt.tz_convert('Etc/GMT-1')

        # Asegurar que columnas de radiación son numéricas
        df[ghi_col] = pd.to_numeric(df[ghi_col], errors='coerce')
        df[dni_col] = pd.to_numeric(df[dni_col], errors='coerce')
        df[dif_col] = pd.to_numeric(df[dif_col], errors='coerce')

        # Extraer mes y hora
        month_mapping = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        df['mes']  = df[tiempo_col].dt.month.map(month_mapping)
        df['mes']  = pd.Categorical(df['mes'],
                                    categories=list(month_mapping.values()),
                                    ordered=True)
        df['hora'] = df[tiempo_col].dt.hour + 1  # 1–24

        # Preparamos un df intermedio sin las últimas 3 filas
        df2 = df.iloc[:-2].copy()

        # Creamos los labels desplazados localmente, sin tocar df2
        mes_labels  = df2['mes'].shift(-2)
        hora_labels = df2['hora'].shift(-2)

        # Agrupar usando esos labels desplazados
        grouped = (
            df2
            .groupby([mes_labels, hora_labels])[[ghi_col, dni_col, dif_col]]
            .mean()
            .reset_index()
            .rename(columns={
                'level_0': 'mes',
                'level_1': 'hora',
                ghi_col:    'rad GH',
                dni_col:    'G_sol_b',
                dif_col:    'G_sol_d'
            })
        )

        # Crear carpeta y exportar parquet
        output_dir = os.path.join("public", "radiaciones")
        os.makedirs(output_dir, exist_ok=True)
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        output_path   = os.path.join(output_dir, f"{base_filename}_promedios.parquet")
        grouped.to_parquet(output_path, index=False)

        print(f"✅ Archivo exportado exitosamente a: {output_path}")
        return {"message": "✅ Archivo exportado exitosamente"}

    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")
        return {"error": "❌ Error al procesar el archivo"}




    
# read_parquet_and_export_radiations("public/uploads/chile_peru_arequipa_05_04_2025.processed.parquet")