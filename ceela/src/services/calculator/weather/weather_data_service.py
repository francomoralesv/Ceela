import calendar
import concurrent.futures
import time

import numpy as np
import pandas as pd

from src.utils.processor import export_to_parquet


class WeatherProcessor:

    def __init__(self, file_path):
        self.A = 18.9
        self.B = 0.255
        self.rango = 2.5

        # tabla Reh x^4 %HR  # 0. Tabla de referencia
        self.DT11 = 3.7649
        self.DT12 = 0.2691
        self.DT13 = 0.0105
        self.DT14 = 0.00006
        self.DT15 = 0.000005

        self.gd_limit = 165  # gd limite estacional
        self.monthly_output_path = None
        self.output_processed_path = None
        self.file_path = file_path

    def process_climate_data(self):
        """Main function to process climate data and apply calculations."""
        try:
            total_start_time = time.time()
            df_warmup,df = self.read_climate_data()

            # Calculate average temperature (Tm)
            tm =  self.calculate_average_temperature(df_warmup)

            # Calculate Tn min values
            tn_min =  self.calculate_tn_min(tm)

            # Calculate Tn max values
            tn_max =  self.calculate_tn_max(tm)

            # Calculate gh calefaccion
            start_time = time.time()
            df['Month'] = df['Tiempo'].dt.month
            df_warmup['Month'] = df_warmup['Tiempo'].dt.month
            temp_col = 'Temperatura en 2 metros (Corejida)[label: Temp] [C]'

            # Vectorized calculation of gh calefaccion
            def get_tn_min_value(month, temp):
                month_idx = month - 1
                tn_min_month = tn_min[month_idx]
                return max(tn_min_month - temp, 0) if pd.notna(tn_min_month) and temp < tn_min_month else 0

            df['gh calefaccion'] = df.apply(
                lambda row: get_tn_min_value(row['Month'], row[temp_col]), axis=1)            
            
            df_warmup['gh calefaccion'] = df_warmup.apply(
                lambda row: get_tn_min_value(row['Month'], row[temp_col]), axis=1)

            # Calculate absolute humidity
            F2 = df[temp_col]
            G2 = df['Humedad Relativa[label: HR%] [%]']
            df['Humedad Abs kg agua / kg Aire'] = (G2 * (
                    self.DT11 + self.DT12 * F2 + self.DT13 * F2 ** 2 + self.DT14 * F2 ** 3 + self.DT15 * F2 ** 4)) / 100000
            df_warmup['Humedad Abs kg agua / kg Aire'] = (G2 * (
                    self.DT11 + self.DT12 * F2 + self.DT13 * F2 ** 2 + self.DT14 * F2 ** 3 + self.DT15 * F2 ** 4)) / 100000

            end_time = time.time()
            print(
                f"Time taken to calculate gh calefaccion and humidity: {end_time - start_time:.4f} seconds")

            exported_file = export_to_parquet(df, self.file_path)

            total_end_time = time.time()
            print(f"\n=== Performance Metrics ===")
            print(
                f"Total Processing Time: {total_end_time - total_start_time:.4f} seconds")

            return df,df_warmup, tm, tn_min, tn_max, exported_file
        except Exception as e:
            raise Exception(f"Error processing climate data: {str(e)}")

    def load_constants(self, list_constants):
        """Load constants from a configuration file or define them here."""
        try:
            # Load constants from the provided dictionary
            self.A = list_constants.get('A', self.A)
            self.B = list_constants.get('B', self.B)
            self.rango = list_constants.get('rango', self.rango)
    
            # Tabla Reh x^4 %HR - Tabla de referencia
            self.DT11 = list_constants.get('DT11', self.DT11)
            self.DT12 = list_constants.get('DT12', self.DT12)
            self.DT13 = list_constants.get('DT13', self.DT13)
            self.DT14 = list_constants.get('DT14', self.DT14)
            self.DT15 = list_constants.get('DT15', self.DT15)
    
            self.gd_limit = list_constants.get('gd_limit', self.gd_limit)
        except KeyError as e:
            raise ValueError(f"Missing required constant: {e}")

    def read_climate_data(self):
        """Read climate data from Excel file using parallel processing."""
        try:
            start_time = time.time()

            df = pd.read_excel(self.file_path, engine='openpyxl')
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
                futures = {}
                for col in numeric_columns:
                    if col in df.columns:
                        # Check if the column is of string type before applying .str
                        if df[col].dtype == 'object':
                            futures[col] = executor.submit(
                                pd.to_numeric, df[col].str.replace(',', '.'), errors='coerce'
                            )
                        else:
                            futures[col] = executor.submit(
                                pd.to_numeric, df[col], errors='coerce'
                            )

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

            # --- WARMUP LOGIC ---
            # Convertir la columna 'Tiempo' a datetime si no lo está
            if not np.issubdtype(result['Tiempo'].dtype, np.datetime64):
               result['Tiempo'] = pd.to_datetime(result['Tiempo'])
            # Obtener solo las filas de diciembre (744 filas)
            diciembre = result[result['Tiempo'].dt.month == 12].copy()
            result_with_warmup = pd.concat([diciembre, result], ignore_index=True)
            # Validar que el resultado tenga 9504 filas
            print("Mes cuenta filas", result['Tiempo'].dt.month.value_counts())
            assert len(diciembre) == 744, f"Diciembre no tiene 744 filas, tiene {len(diciembre)}"
            assert len(result_with_warmup) == len(result) + 744, f"El resultado final no tiene {len(result) + 744} filas, tiene {len(result_with_warmup)}"
            # --- END WARMUP LOGIC ---

            end_time = time.time()
            print("\n=== Performance Metrics ===")
            print(f"Data Reading Time: {end_time - start_time:.4f} seconds")
            return result_with_warmup, result

        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    def calculate_average_temperature(self,df):
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
    def calculate_tn_min(self,tm_values):
        """Calculate monthly Tn min values using the formula A + B * Tm - range."""
        try:
            start_time = time.time()

            # Vectorized calculation using numpy
            tm_array = np.array(tm_values)
            mask = ~np.isnan(tm_array)
            result = np.full_like(tm_array, np.nan)
            result[mask] = self.A + (self.B * tm_array[mask]) - self.rango

            end_time = time.time()
            print(
                f"Time taken to calculate Tn min: {end_time - start_time:.4f} seconds")
            return result.tolist()
        except Exception as e:
            raise Exception(f"Error calculating Tn min values: {str(e)}")
    def calculate_tn_max(self,tm_values):
        """Calculate monthly Tn max values using the formula A + B * Tm + range."""
        try:
            # Vectorized calculation using numpy
            tm_array = np.array(tm_values)
            mask = ~np.isnan(tm_array)
            result = np.full_like(tm_array, np.nan)
            result[mask] = self.A + (self.B * tm_array[mask]) + self.rango
            return result.tolist()
        except Exception as e:
            raise Exception(f"Error calculating Tn max values: {str(e)}")


    def validate(self):
        """Valida que el archivo CSV cumpla con el formato indicado."""
        try:
            df = pd.read_excel(self.file_path, encoding='utf-8',
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
                    f"Columnas faltantes en el archivo EXCEL: {columnas_faltantes}")

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
            print(f"Error al validar el archivo EXCEL: {str(e)}")
            return False

    def read_parquet_file(self,parquet_file) -> pd.DataFrame:
        """Read a Parquet file and convert it to a pandas DataFrame.

        Args:
            file_path: Path to the parquet file

        Returns:
            pd.DataFrame: The loaded DataFrame from the parquet file

        Raises:
            Exception: If there is an error reading the file
        """
        try:
            df = pd.read_parquet(parquet_file)
            return df
        except Exception as e:
            raise Exception(f"Error reading Parquet file: {str(e)}")

    # gd_limit viene de tabla de referencias de limites estacional
    def montlhy_weather(self,df, tm, tn_min, tn_max,gd_limit=165):
        # Ensure 'Month' column is of integer type
        df['Month'] = df['Month'].astype(int)

        monthly_gh_calefaccion = [
            df[df['Month'] == month]['gh calefaccion'].sum() / calendar.monthrange(df['Tiempo'].dt.year.iloc[0], month)[1]
            if month in df['Month'].unique() else 0
            for month in range(1, 13)
        ]
        # Save results to parquet with monthly data
        monthly_data = pd.DataFrame({
            'month': range(1, 13),  # Adding month column from 1 to 12
            'tm': tm,
            'tn_min': tn_min,
            'tn_max': tn_max,
            'monthly_gh': monthly_gh_calefaccion
        }, index=range(1, 13))
        monthly_data['estacion'] = monthly_data['monthly_gh'].apply(lambda gh: 'V' if gh < gd_limit else 'I')
        return monthly_data


    def save_parquet(self,df,output_path):
        """Write the DataFrame to a Parquet file."""
        try:
            df.to_parquet(output_path, index=False)
            print(f"Data successfully written to {output_path}")
            return output_path
        except Exception as e:
            raise Exception(f"Error writing DataFrame to Parquet: {str(e)}")
        
    def run(self):
        """Main function to process climate data and return results."""
        # validate(file_path)
        df, df_warmup,tm, tn_min, tn_max, exported_file = self.process_climate_data()
        df_warmup['Month'] = df_warmup['Month'].astype(int)
        monthly_data = self.montlhy_weather(df, tm, tn_min, tn_max)
        self.monthly_output_path = self.file_path.replace('.xlsx', '_monthly.processed.parquet')
        self.save_parquet(monthly_data, self.monthly_output_path)
        total_data = self.read_parquet_file(exported_file)
        self.output_processed_path=exported_file
        return total_data, monthly_data

