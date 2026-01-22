import calendar
import concurrent.futures
import time

import numpy as np
import pandas as pd

# Metodo Dear and Brager
A = 18.9
B = 0.255
rango = 2.5

# tabla Reh x^4 %HR  # 0. Tabla de referencia
DT11 = 3.7649
DT12 = 0.2691
DT13 = 0.0105
DT14 = 0.00006
DT15 = 0.000005

gd_limit = 165  # gd limite estacional


def read_climate_data(file_path, use_warm_up=False):
    """Read climate data from Excel file using parallel processing."""
    try:
        start_time = time.time()

        # Detect file type and read accordingly
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, dtype=str, engine='openpyxl')
        else:
            raise ValueError(
                "Unsupported file format. Please provide a .xlsx file.")
        # Vectorized conversion of numeric columns
        numeric_columns = [
            'Velocidad de Viento[label: Vel_5.5m] [m/s]',
            'Velocidad de Viento[label: Vel_10m] [m/s]',
            'Velocidad de Viento[label: Vel_40m] [m/s]',
            'Temperatura en 2 metros (Corejida)[label: Temp] [C]',
            'Humedad Relativa[label: HR%] [%]',
            'Radiacion Global Horizontal[label: GHI] [W/m2]',
            'Radiacion Directa Normal[label: DNI] [W/m2]',
            'Radiacion Global[label: GLB] [W/m2]',
            'Radiacion Directa[label: DIR] [W/m2]',
            'Radiacion Difusa[label: DIF] [W/m2]',
            'Radiacion Difusa Reflejada[label: RFL] [W/m2]',
            'Presencia de nubes[label: Nube] [1=Si, 0=No]'
        ]

        # Parallel conversion of numeric columns
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {col: executor.submit(
                pd.to_numeric, df[col].str.replace(',', '.'), errors='coerce'
            ) for col in numeric_columns if col in df.columns}

            for col, future in futures.items():
                df[col] = future.result()

        # Vectorized column validation
        required_columns = [
            'Tiempo',
            'Velocidad de Viento[label: Vel_10m] [m/s]',
            'Velocidad de Viento[label: Vel_40m] [m/s]',
            'Temperatura en 2 metros (Corejida)[label: Temp] [C]',
            'Humedad Relativa[label: HR%] [%]',
            'Radiacion Global Horizontal[label: GHI] [W/m2]',
            'Radiacion Directa Normal[label: DNI] [W/m2]',
            'Radiacion Global[label: GLB] [W/m2]',
            'Radiacion Directa[label: DIR] [W/m2]',
            'Radiacion Difusa[label: DIF] [W/m2]',
            'Radiacion Difusa Reflejada[label: RFL] [W/m2]',
            'Presencia de nubes[label: Nube] [1=Si, 0=No]'
        ]

        print('Columns', df.columns)
        missing_columns = [
            col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(f"Missing columns in CSV file: {missing_columns}")

        result = df[required_columns]
        
        if use_warm_up:
            # --- WARMUP LOGIC ---
            # Convertir la columna 'Tiempo' a datetime si no lo está
            if not np.issubdtype(result['Tiempo'].dtype, np.datetime64):
                result['Tiempo'] = pd.to_datetime(result['Tiempo'])
            # Filtrar el primer día de diciembre
            dec_first = result[(result['Tiempo'].dt.month == 12) & (result['Tiempo'].dt.day == 1)]
            # Filtrar todos los datos después del primero de diciembre (inclusive)
            dec_after_first = result[(result['Tiempo'] >= dec_first.iloc[0]['Tiempo'])]
            # Concatenar estos datos al inicio del DataFrame original
            result_with_warmup = pd.concat([dec_after_first, result], ignore_index=True)
            # Validar que el resultado tenga 9504 filas
            assert len(result_with_warmup) == 9504, f"El resultado final no tiene 9504 filas, tiene {len(result_with_warmup)}"
            result = result_with_warmup
            # --- END WARMUP LOGIC ---

        end_time = time.time()
        print("\n=== Performance Metrics ===")
        print(f"Data Reading Time: {end_time - start_time:.4f} seconds")
        return result
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")


def calculate_average_temperature(df):
    """Calculate monthly average temperatures (Tm) using parallel processing."""
    try:
        start_time = time.time()

        if 'Tiempo' not in df.columns:
            raise KeyError("'Tiempo' column is missing from the data frame")

        # Convert 'Tiempo' column to datetime
        df['Tiempo'] = pd.to_datetime(df['Tiempo'])

        # Extract month from datetime
        df['Month'] = df['Tiempo'].dt.month

        # Split data into chunks for parallel processing
        num_chunks = 4
        chunk_size = len(df) // num_chunks
        chunks = [df.iloc[i:i + chunk_size]
                  for i in range(0, len(df), chunk_size)]

        # Function to process each chunk
        def process_chunk(chunk):
            return chunk.groupby('Month')['Temperatura en 2 metros (Corejida)[label: Temp] [C]'].mean()

        # Process chunks in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_chunk, chunks))

        # Combine results
        monthly_temps = pd.concat(results).groupby(level=0).mean()

        # Create a list of 12 monthly averages
        monthly_averages = [monthly_temps.get(month) for month in range(1, 13)]

        end_time = time.time()
        print(
            f"Time taken to calculate average temperature: {end_time - start_time:.4f} seconds")
        return monthly_averages
    except Exception as e:
        raise Exception(f"Error calculating average temperature: {str(e)}")


def calculate_tn_min(tm_values):
    """Calculate monthly Tn min values using the formula A + B * Tm - range."""
    try:
        start_time = time.time()

        # Vectorized calculation using numpy
        tm_array = np.array(tm_values)
        mask = ~np.isnan(tm_array)
        result = np.full_like(tm_array, np.nan)
        result[mask] = A + (B * tm_array[mask]) - rango

        end_time = time.time()
        print(
            f"Time taken to calculate Tn min: {end_time - start_time:.4f} seconds")
        return result.tolist()
    except Exception as e:
        raise Exception(f"Error calculating Tn min values: {str(e)}")


def calculate_tn_max(tm_values):
    """Calculate monthly Tn max values using the formula A + B * Tm + range."""
    try:
        start_time = time.time()

        # Vectorized calculation using numpy
        tm_array = np.array(tm_values)
        mask = ~np.isnan(tm_array)
        result = np.full_like(tm_array, np.nan)
        result[mask] = A + (B * tm_array[mask]) + rango

        end_time = time.time()
        print(
            f"Time taken to calculate Tn max: {end_time - start_time:.4f} seconds")
        return result.tolist()
    except Exception as e:
        raise Exception(f"Error calculating Tn max values: {str(e)}")


def export_to_parquet(df, file_path):
    """Export the processed DataFrame to a Parquet file."""
    try:
        if file_path.endswith('.csv'):
            output_parquet_path = file_path.replace(
                '.csv', '.processed.parquet')
        elif file_path.endswith('.xlsx'):
            output_parquet_path = file_path.replace(
                '.xlsx', '.processed.parquet')
        else:
            raise ValueError(
                "Unsupported file format for exporting to Parquet.")

        df.to_parquet(output_parquet_path, index=False)
        print(f"Data successfully exported to {output_parquet_path}")
        return output_parquet_path
    except Exception as e:
        raise Exception(f"Error exporting data to Parquet: {str(e)}")


def process_climate_data(file_path):
    """Main function to process climate data and apply calculations."""
    try:
        total_start_time = time.time()

        df = read_climate_data(file_path)

        # Calculate average temperature (Tm)
        tm = calculate_average_temperature(df)
        # Calculate Tn min values
        tn_min = calculate_tn_min(tm)
        # Calculate Tn max values
        tn_max = calculate_tn_max(tm)
        # Calculate gh calefaccion
        start_time = time.time()
        df['Month'] = df['Tiempo'].dt.month
        temp_col = 'Temperatura en 2 metros (Corejida)[label: Temp] [C]'

        # Vectorized calculation of gh calefaccion
        def get_tn_min_value(month, temp):
            month_idx = month - 1
            tn_min_month = tn_min[month_idx]
            return max(tn_min_month - temp, 0) if pd.notna(tn_min_month) and temp < tn_min_month else 0

        df['gh calefaccion'] = df.apply(
            lambda row: get_tn_min_value(row['Month'], row[temp_col]), axis=1)

        # Calculate absolute humidity
        F2 = df[temp_col]
        G2 = df['Humedad Relativa[label: HR%] [%]']
        df['Humedad Abs kg agua / kg Aire'] = (G2 * (
            DT11 + DT12 * F2 + DT13 * F2 ** 2 + DT14 * F2 ** 3 + DT15 * F2 ** 4)) / 100000

        end_time = time.time()
        print(
            f"Time taken to calculate gh calefaccion and humidity: {end_time - start_time:.4f} seconds")

        # Save the processed data
        # if file_path.endswith('.csv'):
        #     output_csv_path = file_path.replace('.csv', '.processed.csv')
        # elif file_path.endswith('.xlsx'):
        #     output_csv_path = file_path.replace('.xlsx', '.processed.xlsx')
        # else:
        #     raise ValueError("Formato de archivo no soportado para guardar los datos procesados.")
        # df.to_csv(output_csv_path, sep=';', index=False)


        print(" Df weather ",df)
        exported_file = export_to_parquet(df, file_path)

        total_end_time = time.time()
        print(f"\n=== Performance Metrics ===")
        print(
            f"Total Processing Time: {total_end_time - total_start_time:.4f} seconds")

        return df, tm, tn_min, tn_max, exported_file
    except Exception as e:
        raise Exception(f"Error processing climate data: {str(e)}")


def validate(file_path):
    """Valida que el archivo CSV cumpla con el formato indicado."""
    try:
        df = pd.read_csv(file_path, encoding='utf-8',
                         sep=';', dtype=str, engine='python')

        columnas_requeridas = [
            'Tiempo',
            'Velocidad de Viento[label: Vel_10m] [m/s]',
            'Velocidad de Viento[label: Vel_40m] [m/s]',
            'Temperatura en 2 metros (Corejida)[label: Temp] [C]',
            'Humedad Relativa[label: HR%] [%]',
            'Radiacion Global Horizontal[label: GHI] [W/m2]',
            'Radiacion Directa Normal[label: DNI] [W/m2]',
            'Radiacion Global[label: GLB] [W/m2]',
            'Radiacion Directa[label: DIR] [W/m2]',
            'Radiacion Difusa[label: DIF] [W/m2]',
            'Radiacion Difusa Reflejada[label: RFL] [W/m2]',
            'Presencia de nubes[label: Nube] [1=Si, 0=No]'
        ]

        # Verificar que todas las columnas requeridas estén presentes
        columnas_faltantes = [
            col for col in columnas_requeridas if col not in df.columns]
        if columnas_faltantes:
            raise ValueError(
                f"Columnas faltantes en el archivo CSV: {columnas_faltantes}")

        # Verificar que los datos en las columnas numéricas sean válidos
        columnas_numericas = columnas_requeridas[1:]  # Excluyendo 'Tiempo'
        for col in columnas_numericas:
            df[col] = pd.to_numeric(
                df[col].str.replace(',', '.'), errors='coerce')
            if df[col].isnull().any():
                raise ValueError(
                    f"Datos inválidos encontrados en la columna: {col}")

        print("El archivo CSV cumple con el formato indicado.")
        return True
    except Exception as e:
        print(f"Error al validar el archivo CSV: {str(e)}")
        return False


def main_climate_processing(file_path):
    """Main function to process climate data and return results."""
    validate(file_path)
    df, tm, tn_min, tn_max, exported_file = process_climate_data(file_path)

    # Asegurarse de que el índice del grupo sea un número entero válido
    # monthly_gh = df.groupby('Month')['gh calefaccion'].agg(
    #     lambda x: x.sum() / calendar.monthrange(df['Tiempo'].dt.year.iloc[0], int(x.name))[1] if 1 <= int(x.name) <= 12 else 0
    # )

    # print("\nPromedio mensual de gh calefaccion (suma/días del mes):")
    # for month in range(1, 13):
    #     if month in monthly_gh.index:
    #         days = calendar.monthrange(df['Tiempo'].dt.year.iloc[0], month)[1]
    #         print(f"Mes {month} ({days} días): {monthly_gh[month]:.2f}°C")
    #     else:
    #         print(f"Mes {month}: N/A")

    # # Calculate and print seasonal classification
    # print("\nClasificación estacional por mes:")
    # for month in range(1, 13):
    #     if month in monthly_gh.index:
    #         season = "Verano" if monthly_gh[month] < gd_limit else "Invierno"
    #         print(f"Mes {month}: {season} (gh calefaccion promedio: {monthly_gh[month]:.2f}°C")
    #     else:
    #         print(f"Mes {month}: N/A")

    return exported_file
