import math

import numpy as np
import pandas as pd

from .parameters import Parameters


def process_shape(rt):
    dim = np.shape(rt)
    hp=np.zeros([dim[0],dim[1]])
    for i in range(0, dim[1], 1):  # Columnas
        for j in range(0, dim[0], 1):  # Filas
            if rt[j, i] != 0:
                hp[j, i] = 1.0 / rt[j, i]
            else:
                hp[j, i] = 0

    return hp
def make_sorter(l):
    """
    Create a dict from the list to map to 0..len(l)
    Returns a mapper to map a series to this custom sort order
    """
    print("Sorting order: ", l)
    sort_order = {k:v for k,v in zip(l, range(len(l)))}
    return lambda s: s.map(lambda x: sort_order[x])


def create_matrix(df1,df2,column):
    order = df1.groupby(["Capa"]).sum().sort_values(by="Nd",ascending=False).index.tolist()
    final_sort = []
    matrix = []
    for types in order: 
        multiply = df2.Componente.value_counts().loc[types]
        print(f"multiply: {multiply}")
        for i in range(0,multiply):
            final_sort.append(types)
    for value in final_sort:
        aux = df1[df1["Capa"]==value]
        lambda_coef = aux[column] 
        matrix.append(lambda_coef.tolist())
    df_final = pd.DataFrame(matrix)
    return df_final.fillna(0).T.to_numpy() , df2.sort_values('Componente', key=make_sorter(final_sort)) , final_sort



def len_pared(areas):
    lenpared = 0
    for i in range(0, len(areas)):
        lenpared += 1

    return lenpared


async def locate_params(T,cp,lenpared:int):
    print("[Calculator engine] Loading params")
    # #Otros parametros
    c_int = T.iloc[0, 45] * T.iloc[0, 46]
    dt = T.iloc[5, 34]
    ren = T.iloc[7, 34]
    F_ref = T.iloc[0, 47]
    Htr = T.iloc[0, 36]
    L=len(T)
    Hve = T.iloc[:, 23]
    Hve_i = T.iloc[:, 24]
    flu_int = T.iloc[:, 21]
    flu_sol = T.iloc[:, 20]
    flu_HC = np.zeros(L)
    factor = T.iloc[0, 49:58]
    f_int = factor.iloc[0]
    f_sol = factor.iloc[1]
    f_HC = factor.iloc[2]
    a_sol = factor.iloc[3]
    F_sh = factor.iloc[5]
    ID1 = factor.iloc[6]
    ID2 = factor.iloc[7]
    Informes = factor.iloc[8]

    # Coeficientes convectivos y radiativos
    hre = np.zeros([lenpared])

    hci = T.iloc[:, 38].dropna()
    hce = T.iloc[:, 39].dropna()
    hri = T.iloc[:, 40].dropna()
    hre_e = T.iloc[0, 41]

    # Resistencias superficiales Rsi y Rse
    Rs_ext = T.iloc[:, 42:44].dropna().to_numpy()

    # Parametros ventana
    U_v = T.iloc[0, 44]
    Rc = 1.0 / U_v - Rs_ext[0, 0] - Rs_ext[0, 1]
    hci_v = hci[1]

    if Rs_ext[0, 1] != 0:
        hce_v = hce[1]
    else:
        hce_v = hce[1]

    hpl_v = 1.0 / Rc
    kpl_v = np.array([0, 0])
    kpl_v = np.append(kpl_v, c_int)

    # Variables de temperatura
    t_e = T.iloc[:, 5]
    NORTE = T.iloc[:, 6]
    NORESTE = T.iloc[:, 7]
    ESTE = T.iloc[:, 8]
    SURESTE = T.iloc[:, 9]
    SUR = T.iloc[:, 10]
    SUROESTE = T.iloc[:, 11]
    OESTE = T.iloc[:, 12]
    NOROESTE = T.iloc[:, 13]
    HORIZONTAL = T.iloc[:, 14]
    PHISOL_DIF = T.iloc[:, 15]
    PHISOL_VENTANA = T.iloc[:, 16]
    T_T = T.iloc[:, 17]
    T_ZTU = T.iloc[:, 18]
    T_ZTC = T.iloc[:, 19]
    CLIMA = T.iloc[:, 22]

    nodeT = 0
    Fo_L = np.zeros(len(cp))
    Nd = np.zeros([len(cp), lenpared])  # hay que cambiar el largo al máximo entre los materiales del muro.
    # o a la cantidad de materiales distintos
    dx = np.zeros([len(cp), lenpared])

    start = 0
    stop = len(cp)
    nodos = np.zeros(lenpared)

    return Parameters(hre_e, c_int, dt, ren, F_ref, Htr, Hve, Hve_i, flu_int, flu_sol, flu_HC, factor, f_int, f_sol, f_HC,
                    a_sol, F_sh, ID1, ID2, Informes, hci, hce, hri, hre, Rs_ext, U_v, Rc, hci_v, hce_v, hpl_v, kpl_v, t_e,
                    NORTE, NORESTE, ESTE, SURESTE, SUR, SUROESTE, OESTE, NOROESTE, HORIZONTAL, PHISOL_DIF, PHISOL_VENTANA,
                    T_T, T_ZTU, T_ZTC, CLIMA, nodeT, Fo_L, Nd, dx, start, stop, nodos,lenpared)


def convert_to_csv(file_name):
    with open(file_name, 'r', encoding='latin-1') as f:
        lines = f.readlines()

    header = lines[0].strip().split()
    data = []
    for line in lines[1:]:
        if not line.strip():
            continue
        values = line.strip().split()
        if len(values) == len(header):
            data.append(values)

    df = pd.DataFrame(data, columns=header)

    # Intentar convertir columnas a numérico donde se pueda
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass

    df.to_csv(file_name + '.csv', index=False)


def to_dataframe(texto):
    """
    Convierte un texto con encabezados y datos en un DataFrame de pandas.

    :param texto: Cadena de texto con encabezados y datos separados por espacios.
    :return: DataFrame de pandas con los datos procesados.
    """
    # Dividir el texto en líneas
    print(type(texto))
    if isinstance(texto, np.ndarray):
        texto = "\n".join(" ".join(map(str, row)) for row in texto)
    lineas = texto.strip().split("\n")

    # La primera línea contiene los encabezados
    encabezados = lineas[0].split()

    # Las líneas restantes contienen los datos
    datos = [list(map(float, linea.split())) for linea in lineas[1:]]

    # Crear el DataFrame
    df = pd.DataFrame(datos, columns=encabezados)
    print(df)
    return df


def calcular_vol_surf(area_base, altura):
    lado = math.sqrt(area_base)
    perimetro = 4 * lado
    superficie = 2 * area_base + perimetro * altura
    volumen = area_base * altura
    return superficie, volumen