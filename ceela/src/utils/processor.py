import pandas as pd


def read_parquet_file(file_path: str) -> pd.DataFrame:
    """
    Lee un archivo Parquet y lo convierte en un DataFrame de pandas.

    Args:
        file_path (str): Ruta al archivo Parquet.

    Returns:
        pd.DataFrame: DataFrame cargado desde el archivo Parquet.

    Raises:
        Exception: Si ocurre un error al leer el archivo.
    """
    try:
        df = pd.read_parquet(file_path)
        return df
    except Exception as e:
        raise Exception(f"Error al leer el archivo Parquet: {str(e)}")


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


def txt_to_df( txt_path):
    """
    Lee un archivo txt de resultados y lo convierte en un DataFrame con columnas numéricas si es posible.
    Si hay filas con menos columnas que el header, las rellena con None.
    """
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    columns = lines[0].strip().split()
    n_cols = len(columns)
    data = []
    for line in lines[1:]:
        if line.strip():
            row = line.strip().split()
            # Rellenar con None si faltan columnas
            if len(row) < n_cols:
                row += [None] * (n_cols - len(row))
            data.append(row)

    df = pd.DataFrame(data, columns=columns)
    for col in df.columns:
        try:
            df[col] = df[col].astype(float)
        except Exception:
            pass

    # Convertir columnas específicas a enteros
    integer_columns = ['ID_Recinto', 'Mes', 'Hora']
    for col in integer_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(
                    df[col], errors='coerce').fillna(0).astype(int)
            except Exception:
                pass

    return df
