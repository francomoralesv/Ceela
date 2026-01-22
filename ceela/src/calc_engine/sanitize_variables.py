import traceback
import numpy as np
import pandas as pd

from .utils import create_matrix


class SanitizeVariablesDTO:
    def __init__(self, T, L, areas, conductividad, densidad, cp, espesor, pared, area_ventana, orientacion, parametros, humedad):
        self.T = T
        self.L = L
        self.areas = areas
        self.conductividad = conductividad
        self.densidad = densidad
        self.cp = cp
        self.espesor = espesor
        self.pared = pared
        self.area_ventana = area_ventana
        self.orientacion = orientacion
        self.parametros = parametros
        self.humedad = humedad

async def sanitize_variables(path):
    print("[Calculator engine] Loading variables")
    # Importación de parametros fiscos necesarios para armar las ecuaciones de balance energetico
    # Orden de los muros de mayor a menor numero de nodos desde la importacion de excel
    T = pd.read_excel(path, sheet_name='temperatura')
    parametros = pd.read_excel(path, sheet_name='areas')
    humedad = pd.read_excel(path, sheet_name='humedad')

    # Generacion de las propiedades fisicas para la generacion de kpl y hpl, ordenados de mayor a menor numero de nodos
    df = pd.read_excel(path, sheet_name='muros')
    areas = pd.read_excel(path, sheet_name='areas')
    try:
        areas = areas.iloc[:, :5]
        areas = areas[areas["Area"] != 0]
        conductividad, orientacion, orden = create_matrix(df, areas, "λ [W/mK]")
        densidad, orientacion, orden = create_matrix(df, areas, "ρ [kg/m³]")
        cp, orientacion, orden = create_matrix(df, areas, "c [J/kg K]")
        espesor, orientacion, orden = create_matrix(df, areas, "d [m]")
        L = len(T)
        # Quita los espacios vacios de las listas de valores importados.
        pared = parametros.iloc[:, 0].dropna()
        area_ventana = np.float64(parametros.iloc[0, 8])
    except Exception as e:
        traceback.print_exc()
        print(f"Error al procesar los datos: {e}")
        raise
    return SanitizeVariablesDTO(T,L,areas, conductividad, densidad, cp, espesor, pared, area_ventana,orientacion,parametros,humedad)
