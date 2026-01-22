# -*- coding: utf-8 -*-
"""
21-11-2022

@author: PAN

Codigo creado cons^erando la norma ISO 52016-1 y validado segun ASHRAE 140 casos base 600 y 900.


"""

from math import sqrt as raiz
from math import exp
import numpy as np
import pandas as pd
from numpy.linalg import inv
from scipy.linalg import lu_factor, lu_solve
import time
from numpy import savetxt
import sys


def ejecutable_iso(project_id: int, path, output_dir):
    try:
        T = pd.read_excel(path, sheet_name='temperatura')
        parametros = pd.read_excel(path, sheet_name='areas')
        humedad = pd.read_excel(path, sheet_name='humedad')

        L = len(T)  # Cantidad de datos climáticos, 24*365+24*31
        if (L > 9000):
            RANGE = 9505
            START = 744
        else:
            RANGE = 8761
            START = 0
        print("[Calculator engine] Longitud de los datos: ", L)
        print(f"Rango de datos: f{START} to f{RANGE} ")

        # Importación de parametros fiscos necesarios para armar las ecuaciones de balance energetico
        # Orden de los muros de mayor a menor numero de nodos desde la importacion de excel

        def make_sorter(l):
            """
            Create a dict from the list to map to 0..len(l)
            Returns a mapper to map a series to this custom sort order
            """
            sort_order = {k: v for k, v in zip(l, range(len(l)))}
            return lambda s: s.map(lambda x: sort_order[x])

        def create_matrix(df1, df2, column):
            # Diagnostic: Check for NaN values in the 'Componente' column before sorting
            nan_rows = df2[df2['Componente'].isna()]
            if not nan_rows.empty:
                print("\nDETECTADOS VALORES NaN EN LA COLUMNA 'Componente':\n")
                print(nan_rows)
                print("\nIndices de las filas con NaN:", nan_rows.index.tolist())
                print("\nPor favor, corrige estos valores en el archivo Excel de entrada.\n")

            order = df1.groupby(["Capa"]).sum().sort_values(by="Nd", ascending=False).index.tolist()
            final_sort = []
            matrix = []
            for types in order:
                multiply = df2.Componente.value_counts().loc[types]
                for i in range(0, multiply):
                    final_sort.append(types)
            for value in final_sort:
                aux = df1[df1["Capa"] == value]
                lambda_coef = aux[column]
                matrix.append(lambda_coef.tolist())
            df_final = pd.DataFrame(matrix)
            return df_final.fillna(0).T.to_numpy(), df2.sort_values('Componente',
                                                                    key=make_sorter(final_sort)), final_sort

        # Generacion de las propiedades fisicas para la generacion de kpl y hpl, ordenados de mayor a menor numero de nodos
        df = pd.read_excel(path, sheet_name='muros')
        areas = pd.read_excel(path, sheet_name='areas')
        areas = areas.iloc[:, :5]
        areas = areas[areas["Area"] != 0]
        conductividad, orientacion, orden = create_matrix(df, areas, "λ [W/mK]")
        densidad, orientacion, orden = create_matrix(df, areas, "ρ [kg/m³]")
        cp, orientacion, orden = create_matrix(df, areas, "c [J/kg K]")
        espesor, orientacion, orden = create_matrix(df, areas, "d [m]")
        pared = parametros.iloc[:, 0].dropna()
        area_ventana = np.float64(parametros.iloc[0, 8])
        ####################################################################################
        ##Ordena los elementos las listas de N a S, S a N, muros extra y techo-piso .
        lenpared = 0.0
        for i in range(0, len(areas)):
            lenpared += 1

        lenpared = int(lenpared)

        # #Otros parametros
        c_int = T.iloc[0, 45] * T.iloc[0, 46]
        dt = T.iloc[5, 34]
        ren = T.iloc[7, 34]
        F_ref = T.iloc[0, 47]
        Htr = T.iloc[0, 36]

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
        hci = np.zeros([3])
        hce = np.zeros([3])
        hri = np.zeros([3])
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

        ##################################################################
        ##Funcion para corregir el orden de los elementos que lo necesiten

        orientacion1 = orientacion.iloc[:, 1].to_list()
        data2 = orientacion1.copy()
        matches = {'HR': None,
                   'CT': None,
                   'FL': None
                   }

        def get_index(order_array, match=matches):
            for i in matches.keys():
                for index, j in enumerate(order_array):
                    if j == i:
                        matches[i] = index
            return matches, order_array

        def swap_cols(matrix, order_list, matches=matches):
            matches, order_final = get_index(order_list, matches)
            floor = []
            for key, val in matches.items():
                if key == 'HR':
                    roof = val
                else:
                    if val != None:
                        floor.append([key, val])
            final_index = matrix.shape[1] - 1
            if len(floor) == 1:
                floor = floor[0][1]
                if floor == final_index:
                    if roof != None:
                        matrix[:, [roof, final_index - 1]] = matrix[:, [final_index - 1, roof]]
                        # mover el techo al penultimo lugar
                        order_final[roof], order_final[final_index - 1] = order_final[final_index - 1], order_final[
                            roof]
                elif floor != final_index and roof == final_index:
                    if floor == final_index - 1:
                        matrix[:, [floor, roof]] = matrix[:, [roof, floor]]
                        # mover el techo por el piso
                        order_final[roof], order_final[floor] = order_final[floor], order_final[roof]
                    else:
                        matrix[:, [roof, final_index - 1]] = matrix[:, [final_index - 1, roof]]
                        matrix[:, [floor, roof]] = matrix[:, [roof, floor]]
                        # mover el techo por el penultimo y luego el piso por el penultimo
                        order_final[roof], order_final[final_index - 1] = order_final[final_index - 1], order_final[
                            roof]
                        order_final[roof], order_final[floor] = order_final[floor], order_final[roof]
                elif floor != final_index and roof == None:
                    matrix[:, [floor, final_index]] = matrix[:, [final_index, floor]]
                    order_final[floor], order_final[final_index] = order_final[final_index], order_final[floor]
                else:
                    matrix[:, [floor, final_index]] = matrix[:, [final_index, floor]]
                    matrix[:, [roof, final_index - 1]] = matrix[:, [final_index - 1, roof]]
                    order_final[floor], order_final[final_index] = order_final[final_index], order_final[floor]
                    order_final[roof], order_final[final_index - 1] = order_final[final_index - 1], order_final[roof]

            elif len(floor) == 2:
                """CT,FL,HR --- HR,FL,CT"""
                floor_ct = matches['CT']
                floor_fl = matches['FL']
                if floor_ct == final_index:
                    if floor_fl == final_index - 1:
                        pass
                    else:
                        matrix[:, [floor_fl, final_index - 1]] = matrix[:, [final_index - 1, floor_fl]]
                        order_final[floor_fl], order_final[final_index - 1] = order_final[final_index - 1], order_final[
                            floor_fl]
                        matches, _ = get_index(order_final)
                        floor_fl = matches['FL']
                        roof = matches['HR']
                    if roof != None:
                        matrix[:, [roof, final_index - 2]] = matrix[:, [final_index - 2, roof]]
                        order_final[roof], order_final[final_index - 2] = order_final[final_index - 2], order_final[
                            roof]
                        matches, _ = get_index(order_final)
                        floor_fl = matches['FL']
                        roof = matches['HR']
                else:
                    matrix[:, [floor_ct, final_index]] = matrix[:, [final_index, floor_ct]]
                    order_final[floor_ct], order_final[final_index] = order_final[final_index], order_final[floor_ct]
                    matches, _ = get_index(order_final)
                    floor_fl = matches['FL']
                    roof = matches['HR']
                    if floor_fl == final_index - 1:
                        pass
                    else:
                        matrix[:, [floor_fl, final_index - 1]] = matrix[:, [final_index - 1, floor_fl]]
                        order_final[floor_fl], order_final[final_index - 1] = order_final[final_index - 1], order_final[
                            floor_fl]
                        matches, _ = get_index(order_final)
                        floor_fl = matches['FL']
                        roof = matches['HR']
                    if roof != None:
                        matrix[:, [roof, final_index - 2]] = matrix[:, [final_index - 2, roof]]
                        order_final[roof], order_final[final_index - 2] = order_final[final_index - 2], order_final[
                            roof]
                        matches, _ = get_index(order_final)
                        floor_fl = matches['FL']
                        roof = matches['HR']
            else:
                if roof != None:
                    matrix[:, [roof, final_index - 2]] = matrix[:, [final_index - 2, roof]]
                    order_final[roof], order_final[final_index - 2] = order_final[final_index - 2], order_final[roof]
                    matches, _ = get_index(order_final)
                    floor_fl = matches['FL']
                    roof = matches['HR']
            return matrix, order_final

        # Ordena las propiedades físicas y retorna además el nuevo orden de los muros.

        data = espesor
        espesor, ordenfinal = swap_cols(data, data2)

        data = cp
        data2 = orientacion1.copy()
        cp, ordenfinal = swap_cols(data, data2)
        data = conductividad
        data2 = orientacion1.copy()
        conductividad, ordenfinal = swap_cols(data, data2)
        data = densidad
        data2 = orientacion1.copy()
        densidad, ordenfinal = swap_cols(data, data2)

        temperaturapared = []
        area = []
        for i in range(0, len(areas)):
            for j in range(0, len(areas)):
                if ordenfinal[i] == areas.iloc[j, 1]:
                    area.append(areas.iloc[j, 2])
                    temperaturapared.append(areas.iloc[j, 3])
        area = np.append(area, area_ventana)
        temperaturapared.append(parametros.iloc[0, 9])

        Atot = 0.0
        for i in range(0, len(area)):
            Atot += area[i]

        # Crea cantidad de nodos y dx para cada muro

        for j in range(start, len(area) - 1):
            nodeT = 0
            for i in range(start, stop):
                if j == (len(areas) - 2):
                    if conductividad[i, j] != 0:
                        Fo_L[i] = (conductividad[i, j] / (densidad[i, j] * cp[i, j])) * (dt / (espesor[i, j] ** 2))
                        if densidad[i, j] * cp[i, j] * espesor[i, j] >= 75000:
                            Nd[i, j] = max(5, int(raiz(F_ref / Fo_L[i]) + 0.999999))

                        else:
                            Nd[i, j] = max(1, int(raiz(F_ref / Fo_L[i]) + 0.999999))
                        dx[i, j] = espesor[i, j] / Nd[i, j]
                        nodeT = nodeT + int(Nd[i, j])

                elif j == (len(areas) - 1):
                    if conductividad[i, j] != 0:
                        Fo_L[i] = (conductividad[i, j] / (densidad[i, j] * cp[i, j])) * (dt / (espesor[i, j] ** 2))
                        if densidad[i, j] * cp[i, j] * espesor[i, j] >= 75000:
                            Nd[i, j] = max(5, int(raiz(F_ref / Fo_L[i]) + 0.999999))

                        else:
                            Nd[i, j] = max(1, int(raiz(F_ref / Fo_L[i]) + 0.999999))
                        dx[i, j] = espesor[i, j] / Nd[i, j]
                        nodeT = nodeT + int(Nd[i, j])
                else:
                    if conductividad[i, j] != 0:
                        Fo_L[i] = (conductividad[i, j] / (densidad[i, j] * cp[i, j])) * (dt / (espesor[i, j] ** 2))
                        if densidad[i, j] * cp[i, j] * espesor[i, j] >= 75000:
                            Nd[i, j] = max(5, int(raiz(F_ref / Fo_L[i]) + 0.999999))

                        else:
                            Nd[i, j] = max(1, int(raiz(F_ref / Fo_L[i]) + 0.999999))
                        dx[i, j] = espesor[i, j] / Nd[i, j]
                        nodeT = nodeT + int(Nd[i, j])

            nodos[j] = int(nodeT)

        # Vector contador para la creación de las resistencias rt
        largo = np.zeros(lenpared)
        for l in range(0, len(largo), 1):
            k = 0
            for i in range(start, stop, 1):
                if conductividad[i, l] != 0:
                    k += 1
            largo[l] = k

        # Vectores auxiliares para crear hpl y kpl

        rt = np.zeros([(int(max(nodos)) + 1), lenpared])
        kp = np.zeros([int(max(nodos)), lenpared])

        F1 = 0
        F2 = 0
        # Creación de los vectores kp, rt para cada muro. Luego se trabajan y reemplazan como kpl, hpl en el metodo de calculo
        for l in range(0, lenpared):
            i = 0
            dx_old = 0.0
            if temperaturapared[l] == "TE" and ordenfinal[l] == "HR":
                F1 = Rs_ext[1, 0]
                F2 = Rs_ext[1, 1]
                hre[l] = hre_e
            elif ordenfinal[l] == "FL":
                F1 = Rs_ext[2, 0]
                F2 = Rs_ext[2, 1]
                hre[l] = hre_e
            elif ordenfinal[l] == "CT":
                F1 = Rs_ext[2, 0]
                F2 = Rs_ext[2, 1]
                hre[l] = 0
            elif temperaturapared[l] == "TE":
                F1 = Rs_ext[0, 0]
                F2 = Rs_ext[0, 1]
                hre[l] = hre_e
            elif temperaturapared[l] == "ZTC" or temperaturapared[l] == "ZTU":
                F1 = Rs_ext[0, 0]
                F2 = Rs_ext[0, 0]
                hre[l] = hri[1]

            for j in range(start, stop):
                nn = Nd[j, l]
                Dx = dx[j, l]
                for k in range(0, int(nn)):
                    if k == 0 and j == start:

                        rt[i, l] = F1 + Dx / (2.0 * conductividad[j, l])
                        kp[i, l] = densidad[j, l] * cp[j, l] * Dx
                        i = i + 1

                    elif k == 0:

                        rt[i, l] = dx_old / (2.0 * conductividad[j - 1, l]) + Dx / (2.0 * conductividad[j, l])
                        kp[i, l] = densidad[j, l] * cp[j, l] * Dx
                        i = i + 1

                    else:

                        rt[i, l] = Dx / conductividad[j, l]
                        kp[i, l] = densidad[j, l] * cp[j, l] * Dx
                        i = i + 1

                if j == stop - 1:
                    rt[i, l] = F2 + dx[int(largo[l] - 1), l] / (2.0 * conductividad[int(largo[l] - 1), l])

                dx_old = Dx

        dim = np.shape(rt)
        hp = np.zeros([dim[0], dim[1]])
        for i in range(0, dim[1], 1):  # Columnas
            for j in range(0, dim[0], 1):  # Filas
                if rt[j, i] != 0:
                    hp[j, i] = 1.0 / rt[j, i]
                else:
                    hp[j, i] = 0

        # Se eliminan los elementos correspondientes a las superficies interna y externas porque se va a tomar hci,hce de tabla ISO
        hi = hp[0, :]
        he = np.zeros(lenpared)
        for i in range(0, lenpared):

            if ordenfinal[i] == "HR":
                hi[i] = hci[0]
                he[i] = hce[0]
            elif ordenfinal[i] == "FL" or ordenfinal[i] == "CT":
                # hi[i]=hci[2]
                hi[i] = hci[1]
                he[i] = hce[2]
            else:
                hi[i] = hci[1]
                he[i] = hce[1]

        hpl = np.delete(hp, 0, 0)
        # Elimina el último valor para el elemento que difiera en nodos del muro
        for i in range(0, lenpared):
            hpl[int(nodos[i]) - 1, i] = 0
        hpl = np.delete(hpl, int(max(nodos) - 1), 0)

        c_interior = T.iloc[0, 45] * T.iloc[0, 46]

        hpl = hpl[::-1]
        kp = kp[::-1]

        for i in range(0, lenpared - 1, 1):
            c_int = np.append(c_int, c_interior)
        # Agrega a la última fila del vector kp los coeficientes del aire interior
        kpl = np.vstack([kp, c_int])

        # ##############################################################################

        # Vector auxiliar para los muros con menos nodos
        cuenta = np.zeros(lenpared)
        for i in range(0, lenpared):
            for j in range(0, len(kpl)):
                if kpl[j, i] == 0:
                    cuenta[i] += 1

        n = int(sum(nodos)) + int(lenpared)  # Cantidad de nodos
        T_nodos = np.zeros([L, n + 3])
        T_nodos_axu = np.zeros([L, n + 3])
        T_nodos_free = np.zeros([L, n + 3])
        theta_int_op = np.zeros([L])
        theta_int_op2 = np.zeros([L])
        e = np.zeros([n + 3, n + 3])
        e2 = np.zeros([n + 3, n + 3])
        re = np.zeros([n + 3, 1])
        re2 = np.zeros([n + 3, 1])
        T_old = np.zeros([L + 1, n + 3])
        T_old2 = np.zeros([L + 1, n + 3])
        T_old3 = np.zeros([L + 1, n + 3])
        T_old4 = np.zeros([L + 1, n + 3])
        T_aire = np.zeros([L])
        T_aire2 = np.zeros([L])
        T_aire_HC = np.zeros([L])
        y = np.arange(0, len(kpl))
        yy = np.arange(0, n + 3)

        for i in yy:
            T_old[0, i] = T.iloc[0, 29]  # Temperatura inicial t=0
            T_old2[0, i] = T.iloc[0, 29]
            T_old3[0, i] = T.iloc[0, 29]
            T_old4[0, i] = T.iloc[0, 29]

        # #Considera la ecuación de balance al final de cada muro
        nodos = nodos + 1

        if area_ventana != 0:
            nodoventana = 3
            nodos2 = np.zeros(len(area))
            nodos2 = np.append(nodos, nodoventana)
        else:
            nodos2 = np.zeros(len(area))
            nodos2 = nodos

        ##Variables y funciones para el calculo de carga de clima.
        tetha_r_mn = 0

        def step5(phi_HC):
            if phi_HC > 0:
                phi_ld = phi_HC
            else:
                phi_ld = -phi_HC
            return phi_ld

        def step2(t_set, t_int_op, t_upper, phi_upper):

            phi_HC_ld_un = phi_upper * (t_set - t_int_op) / (t_upper - t_int_op)
            return phi_HC_ld_un

        theta_r_mn = 0.0
        pot_max = T.iloc[0, 28]
        theta_H_set = T.iloc[:, 25]
        theta_C_set = T.iloc[:, 26]
        theta_upper = np.zeros([L])
        flu_HC_ld_un = 0  # save numpy array as csv file

        # Funcion para obtener la temperatura del aire que entra por ventilacion en caso de tener un recuperador de calor.
        # aun falta por definir bien la ecuacion
        def ventilacion(ren, theta_aire, theta_e):
            theta_sup = ren * (theta_aire - theta_e) + theta_e
            # theta_sup=theta_e
            return theta_sup

        lambdaground = 2
        Rg = 0.5 / lambdaground
        # if ordenfinal[len(ordenfinal)-1]=="CT":
        #     kpl[int(cuenta[len(cuenta)-1]),kpl.shape[1]-1]=0

        # Generarición de la matriz de coeficientes

        for k in y:
            #   #Ecuacion nodo superficie exterior

            if k == 0:

                axu1 = 0

                for j in range(0, lenpared):

                    if j == lenpared - 1 and ordenfinal[j] == "CT":

                        e[(axu1), (axu1)] = kpl[len(kpl) - int(nodos[j]), j] / dt + hi[j] + hpl[
                            len(hpl) - int(nodos[j]) + 2, j]
                        e[(axu1), (axu1 + 1)] = -hpl[len(hpl) - int(nodos[j]) + 2, j]
                        axu1 = axu1 + int(nodos[j])

                    else:

                        ######## Cambio de hre y he por hri y hi

                        if ordenfinal[j] == "IN" or ordenfinal[j] == "AD":
                            e[(axu1), (axu1)] = kpl[len(kpl) - int(nodos[j]), j] / dt + hi[j] + hpl[
                                len(hpl) - int(nodos[j]) + 2, j]
                            e[(axu1), (axu1 + 1)] = -hpl[len(hpl) - int(nodos[j]) + 2, j]
                            axu1 = axu1 + int(nodos[j])
                        else:
                            e[(axu1), (axu1)] = kpl[len(kpl) - int(nodos[j]), j] / dt + hre[1] + he[j] + hpl[
                                len(hpl) - int(nodos[j]) + 2, j]
                            e[(axu1), (axu1 + 1)] = -hpl[len(hpl) - int(nodos[j]) + 2, j]
                            axu1 = axu1 + int(nodos[j])

                            #   #############################################################################
            #   #############################################################################
            #                                 #####Ecuación nodo superficie interior
            #                                 #####Elementos de la diagonal
            elif k == len(kpl) - 2:

                axu2 = 0
                for j in range(1, lenpared + 1):
                    axu2 += int(nodos[j - 1])
                    e[axu2 - 2, axu2 - 1] = -hi[j - 1]
                    e[axu2 - 2, axu2 - 3] = -hpl[len(hpl) - 1, j - 1]
                    e[axu2 - 2, axu2 - 2] = kpl[k, j - 1] / dt + hi[j - 1] + hpl[len(hpl) - 1, j - 1] + hri[1] - hri[
                        1] * \
                                            area[j - 1] / Atot

                #                               #Ecuación nodo superficie interior
                #                               #Elementos de la interacción entre muros

                axu3 = 0
                for j in range(1, lenpared + 1):
                    axu3 += int(nodos[j - 1])
                    axu4 = 0
                    for i in range(1, lenpared + 1):
                        axu4 += int(nodos[i - 1])
                        if e[axu3 - 2, axu4 - 2] == 0:
                            e[axu3 - 2, axu4 - 2] = -hri[1] * area[i - 1] / Atot

                #   #############################################################################
                #   #############################################################################
                #                                                             #####Ecuación balance aire interior

                # Elementos que interactuan entre muros

                axu3 = 0
                for j in range(1, lenpared + 1):
                    axu3 += int(nodos[j - 1])
                    axu4 = 0
                    for i in range(1, lenpared + 1):
                        axu4 += int(nodos[i - 1])
                        if e[axu3 - 1, axu4 - 2] == 0:
                            e[axu3 - 1, axu4 - 2] = -hi[i - 1] * area[i - 1]


            #   #############################################################################
            #   #############################################################################

            else:
                axu8 = 0  # Ecuación para los nodos internos, en el muro
                for j in range(0, lenpared):
                    for p in range(1, int(nodos[j]) - 2):
                        axu8 += 1
                        e[axu8, axu8 - 1] = -hpl[int(cuenta[j]) + p - 1, j]
                        e[axu8, axu8] = kpl[int(cuenta[j]) + p, j] / dt + hpl[int(cuenta[j]) + p - 1, j] + hpl[
                            int(cuenta[j]) + p, j]
                        e[axu8, axu8 + 1] = -hpl[int(cuenta[j]) + p, j]

                    axu8 += 3

            #   #############################################################################
            #   #############################################################################

            # Se agrega la ventana ponderada

            # Ventanas
            # Ecuación para nodo exterior
            e[n, n] = kpl_v[0] / dt + hre[1] + hce_v + hpl_v
            e[n, n + 1] = -hpl_v

            # Ecuacion para nodo interior
            e[n + 1, n] = -hpl_v
            e[n + 1, n + 2] = -hci_v
            e[n + 1, n + 1] = kpl_v[1] / dt + hci_v + hpl_v + hri[1] - hri[1] * area[len(area) - 1] / Atot

            # #Balance de energía interior

            areahci = 0
            for i in range(0, len(area)):
                if i == len(area) - 1:
                    areahci += area[i] * hci_v
                else:
                    areahci += area[i] * hi[i]
            e[n + 2, n + 1] = -hci_v * area[len(area) - 1]

            # Efecto de las ventanas otros muros
            axu9 = 0
            for j in range(1, lenpared + 1):
                axu9 += int(nodos[j - 1])
                e[axu9 - 2, n + 3 - 2] = -hri[1] * area[len(area) - 1] / Atot
                e[axu9 - 1, n + 3 - 2] = -hci_v * area[len(area) - 1]

            axu9 = 0
            for i in range(0, lenpared, 1):
                axu9 += int(nodos[i])
                if e[n + 1, axu9 - 2] != 0:
                    e[n + 1, axu9 - 2] = e[n + 1, axu9 - 2]
                else:
                    e[n + 1, axu9 - 2] = -hri[1] * area[i] / Atot
                    e[n + 2, axu9 - 2] = -hi[i] * area[i]

        # Valores para el posterior calculo en free flow
        e2 = e.copy()

        #############################################################################
        #############################################################################

        # Generabión del vector resultados y luego iteración por paso de tiempo

        areahci = 0
        for i in range(0, len(area)):
            if i == len(area) - 1:
                areahci += area[i] * hci_v
            else:
                areahci += area[i] * hi[i]
        x = np.arange(0, L, 1)

        theta_sup = np.zeros([L])
        theta_sup2 = np.zeros([L])
        auxk = len(kpl) - 1
        k = len(kpl) - 2

        for i in x:

            # Termino de ventilacion para el balance energetico

            axu2 = 0
            for j in range(1, lenpared + 1):
                axu2 += int(nodos[j - 1])
                e[(axu2 - 1), (axu2 - 1)] = kpl[auxk, j - 1] / dt + (Hve[i] + Hve_i[i]) + Htr + areahci

            e[n + 2, n + 2] = kpl_v[2] / dt + (Hve[i] + Hve_i[i]) + Htr + areahci

            # Si se tiene un recuperador de calor
            if ren != 0:
                theta_sup[i] = ventilacion(ren, T_old[i, T_old.shape[1] - 1], t_e[i])
            else:
                theta_sup[i] = t_e[i]

            axu10 = 0
            axu11 = 0
            # Factores dependientes solo de la hora
            # Nodo superficie interior
            b2 = (1.0 / Atot) * ((1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC[i])
            # Balance energetico
            c2 = Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[i] + f_int * flu_int[i] + f_sol * flu_sol[
                i] + f_HC * \
                 flu_HC[i]

            ## Vector de resultados para los nodos elementos opacos

            for j in range(0, lenpared):
                # Factores dependentientes de la pared correspondiente
                a1 = T_old[i, axu10] / dt
                b1 = T_old[i, axu10 + int(nodos[j]) - 2] / dt
                c1 = T_old[i, axu10 + int(nodos[j]) - 1] / dt
                if ordenfinal[j] == "N" or ordenfinal[j] == "NE" or ordenfinal[j] == "E" or ordenfinal[j] == "SE" or \
                        ordenfinal[j] == "S" \
                        or ordenfinal[j] == "SO" or ordenfinal[j] == "O" or ordenfinal[j] == "NO" or ordenfinal[
                    j] == "N" or \
                        ordenfinal[j] == "HR" \
                        or ordenfinal[j] == "FL":
                    if ordenfinal[j] == "N":
                        a2 = (hre[1] + hce[1]) * t_e[i] + NORTE[i]
                    elif ordenfinal[j] == "NE":
                        a2 = (hre[1] + hce[1]) * t_e[i] + NORESTE[i]
                    elif ordenfinal[j] == "E":
                        a2 = (hre[1] + hce[1]) * t_e[i] + ESTE[i]
                    elif ordenfinal[j] == "SE":
                        a2 = (hre[1] + hce[1]) * t_e[i] + SURESTE[i]
                    elif ordenfinal[j] == "S":
                        a2 = (hre[1] + hce[1]) * t_e[i] + SUR[i]
                    elif ordenfinal[j] == "SO":
                        a2 = (hre[1] + hce[1]) * t_e[i] + SUROESTE[i]
                    elif ordenfinal[j] == "O":
                        a2 = (hre[1] + hce[1]) * t_e[i] + OESTE[i]
                    elif ordenfinal[j] == "NO":
                        a2 = (hre[1] + hce[1]) * t_e[i] + NOROESTE[i]
                    elif ordenfinal[j] == "HR":
                        a2 = (hre[1] + hce[1]) * t_e[i] + HORIZONTAL[i]
                    elif ordenfinal[j] == "FL":
                        a2 = (hre[1] + hce[1]) * t_e[i] + PHISOL_DIF[i]

                ###### Piso ventilado

                elif ordenfinal[j] == "AD":

                    # Reemplazar por temperatura interior T_ZTC[i] por T_old[i,len(e)-1]

                    # ISO=0
                    # a2 = ISO*((hre[1]+hce[1])*T_ZTC[i])
                    a2 = (hci[1]) * T_old[i, len(e) - 1]
                    # a2 = (hre[1]+hce[1])*t_e[i]
                elif ordenfinal[j] == "IN":
                    a2 = (hci[1]) * T_ZTU[i]
                elif ordenfinal[j] == "CT":
                    # a2 = (1/Rg)*T_T[i]
                    a2 = (hci[1]) * T_T[i]

                ###############################################################################
                #####Crea los valores en la matriz de resultados para todos los nodos.
                for k in range(0, int(nodos[j])):

                    # Nodo Exterior
                    if k == 0:
                        re[axu10] = kpl[int(cuenta[j]) + k, j] * a1 + a2
                    # Nodo Interior
                    elif k == int(nodos[j]) - 2:
                        re[axu10 + int(nodos[j]) - 2] = kpl[int(cuenta[j]) + k, j] * b1 + b2
                        # Balance energético
                    elif k == int(nodos[j]) - 1:
                        re[axu10 + int(nodos[j]) - 1] = kpl[int(cuenta[j]) + k, j] * c1 + c2
                        # Nodos interiores
                    else:
                        if int(nodos[j]) > 3:
                            axu11 += 1
                            re[axu11] = kpl[int(cuenta[j]) + k, j] * T_old[i, axu11] / dt

                axu10 += int(nodos[j])
                axu11 += 3
            ###############################################################################

            # Ponderado ventana

            # Superficie externa
            re[n] = kpl_v[0] * T_old[i, n] / dt + (hce_v + hre[1]) * t_e[i] + PHISOL_VENTANA[i]
            # Superficie interna
            re[n + 1] = kpl_v[1] * T_old[i, n + 1] / dt + (1.0 / Atot) * (
                    (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC[i])
            # Balance interior
            re[n + 2] = kpl_v[2] * T_old[i, n + 2] / dt + Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[
                i] + f_int * \
                        flu_int[i] + f_sol * flu_sol[i] + f_HC * flu_HC[i]
            # Despeje de temperatura y guardado de temperaturas
            lu_piv = lu_factor(e)
            t_actual = lu_solve(lu_piv, re)
            T_nodos_free[i, :] = t_actual.T  # Reemplaza la temperatura en t-1 por la última temperatura

            T_old[i + 1, :] = t_actual.T
            T_aire[i] = T_nodos_free[i, len(e) - 1]

            ##########################################################################
            # Operaciones para determinar la demanda energetica
            # calculo de la temperatura operativa
            axu12 = 0
            sumatheta_r_mn = 0

            for j in range(0, len(area)):
                axu12 += int(nodos2[j])
                sumatheta_r_mn += area[j] * T_old[i + 1, axu12 - 2]
            theta_r_mn = sumatheta_r_mn / sum(area)
            theta_int_op[i] = (T_old[i + 1, len(e) - 1] + theta_r_mn) / 2

            if CLIMA[i] == 1:

                # Step 1
                if theta_H_set[i] <= theta_int_op[i] and theta_int_op[i] <= theta_C_set[i]:
                    flu_HC[i] = 0
                    T_nodos[i, :] = t_actual.T

                    # Step 2
                else:
                    if i >= 1:

                        if T_old2[i, 0] == 0:
                            T_old2[i, :] = T_old[i, :]
                            T_old3[i, :] = T_old[i, :]

                    flu_HC_upper = pot_max * area[len(area) - 2]
                    axu10 = 0
                    axu11 = 0
                    # Factores dependientes solo de la hora
                    # Nodo superficie interior
                    b2 = (1.0 / Atot) * (
                            (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC_upper)
                    # Balance energetico
                    c2 = Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[i] + f_int * flu_int[i] + f_sol * \
                         flu_sol[
                             i] + f_HC * flu_HC_upper

                    ## Vector de resultados para los nodos elementos opacos

                    for j in range(0, lenpared):
                        # Factores dependentientes de la pared correspondiente
                        a1 = T_old[i, axu10] / dt
                        b1 = T_old[i, axu10 + int(nodos[j]) - 2] / dt
                        c1 = T_old[i, axu10 + int(nodos[j]) - 1] / dt
                        if ordenfinal[j] == "N" or ordenfinal[j] == "NE" or ordenfinal[j] == "E" or ordenfinal[
                            j] == "SE" or \
                                ordenfinal[j] == "S" \
                                or ordenfinal[j] == "SO" or ordenfinal[j] == "O" or ordenfinal[j] == "NO" or ordenfinal[
                            j] == "N" or ordenfinal[j] == "HR" \
                                or ordenfinal[j] == "FL":
                            if ordenfinal[j] == "N":
                                a2 = (hre[1] + hce[1]) * t_e[i] + NORTE[i]
                            elif ordenfinal[j] == "NE":
                                a2 = (hre[1] + hce[1]) * t_e[i] + NORESTE[i]
                            elif ordenfinal[j] == "E":
                                a2 = (hre[1] + hce[1]) * t_e[i] + ESTE[i]
                            elif ordenfinal[j] == "SE":
                                a2 = (hre[1] + hce[1]) * t_e[i] + SURESTE[i]
                            elif ordenfinal[j] == "S":
                                a2 = (hre[1] + hce[1]) * t_e[i] + SUR[i]
                            elif ordenfinal[j] == "SO":
                                a2 = (hre[1] + hce[1]) * t_e[i] + SUROESTE[i]
                            elif ordenfinal[j] == "O":
                                a2 = (hre[1] + hce[1]) * t_e[i] + OESTE[i]
                            elif ordenfinal[j] == "NO":
                                a2 = (hre[1] + hce[1]) * t_e[i] + NOROESTE[i]
                            elif ordenfinal[j] == "HR":
                                a2 = (hre[1] + hce[1]) * t_e[i] + HORIZONTAL[i]
                            elif ordenfinal[j] == "FL":
                                a2 = (hre[1] + hce[1]) * t_e[i] + PHISOL_DIF[i]

                        ###### Piso ventilado

                        elif ordenfinal[j] == "AD":

                            # Reemplazar por temperatura interior T_ZTC[i] por T_old[len(T_old)-1]

                            # ISO=0
                            # a2 = ISO*((hre[1]+hce[1])*T_ZTC[i])
                            a2 = (hci[1]) * T_old[i, len(e) - 1]
                            # a2 = (hre[1]+hce[1])*t_e[i]
                        elif ordenfinal[j] == "IN":
                            a2 = (hci[1]) * T_ZTU[i]
                        elif ordenfinal[j] == "CT":
                            # a2 = (1/Rg)*T_T[i]
                            a2 = (hci[1]) * T_T[i]
                        ###############################################################################
                        #####Crea los valores en la matriz de resultados para todos los nodos.
                        for k in range(0, int(nodos[j])):

                            # Nodo Exterior
                            if k == 0:
                                re[axu10] = kpl[int(cuenta[j]) + k, j] * a1 + a2
                            # Nodo Interior
                            elif k == int(nodos[j]) - 2:
                                re[axu10 + int(nodos[j]) - 2] = kpl[int(cuenta[j]) + k, j] * b1 + b2
                                # Balance energético
                            elif k == int(nodos[j]) - 1:
                                re[axu10 + int(nodos[j]) - 1] = kpl[int(cuenta[j]) + k, j] * c1 + c2
                                # Nodos interiores
                            else:
                                if int(nodos[j]) > 3:
                                    axu11 += 1
                                    re[axu11] = kpl[int(cuenta[j]) + k, j] * T_old[i, axu11] / dt

                        axu10 += int(nodos[j])
                        axu11 += 3
                    ###############################################################################

                    # Ponderado ventana

                    # Superficie externa
                    re[n] = kpl_v[0] * T_old[i, n] / dt + (hce_v + hre[1]) * t_e[i] + PHISOL_VENTANA[i]
                    # Superficie interna
                    re[n + 1] = kpl_v[1] * T_old[i, n + 1] / dt + (1.0 / Atot) * (
                            (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC_upper)
                    # Balance interior
                    re[n + 2] = kpl_v[2] * T_old[i, n + 2] / dt + Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[
                        i] + f_int * flu_int[i] + f_sol * flu_sol[i] + f_HC * flu_HC_upper

                    lu_piv = lu_factor(e)
                    t_actual_upper = lu_solve(lu_piv, re)
                    T_nodos_axu[i, :] = t_actual_upper.T  # Reemplaza la temperatura en t-1 por la última temperatura

                    T_old2[i + 1, :] = t_actual_upper.T

                    #     ############
                    axu13 = 0
                    sumatheta_r_mn_upper = 0
                    for j in range(0, len(area)):
                        axu13 += int(nodos2[j])
                        sumatheta_r_mn_upper += area[j] * T_old2[i + 1, axu13 - 2]
                    theta_r_mn_upper = sumatheta_r_mn_upper / sum(area)
                    theta_upper[i] = (T_old2[i + 1, len(e) - 1] + theta_r_mn_upper) / 2

                    if theta_int_op[i] > theta_C_set[i]:
                        theta_int_set = theta_C_set[i]
                        flu_HC_ld_un = step2(theta_int_set, theta_int_op[i], theta_upper[i], flu_HC_upper)


                    elif theta_int_op[i] < theta_H_set[i]:
                        theta_int_set = theta_H_set[i]
                        flu_HC_ld_un = step2(theta_int_set, theta_int_op[i], theta_upper[i], flu_HC_upper)

                    # Step 3
                    # Step 4
                    flu_C_avail = -flu_HC_upper
                    flu_H_avail = flu_HC_upper
                    if flu_C_avail <= flu_HC_ld_un and flu_HC_ld_un <= flu_H_avail:
                        flu_HC[i] = flu_HC_ld_un
                    else:
                        if flu_HC_ld_un > 0:
                            flu_HC[i] = flu_H_avail
                        elif flu_HC_ld_un < 0:
                            flu_HC[i] = flu_C_avail

                    #######     #Finalmente vuelve a resolver el balance energetico para determinar las temperaturas

                    axu10 = 0
                    axu11 = 0
                    # Factores dependientes solo de la hora
                    # Nodo superficie interior
                    b2 = (1.0 / Atot) * (
                                (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC[i])
                    # Balance energetico
                    c2 = Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[i] + f_int * flu_int[i] + f_sol * \
                         flu_sol[
                             i] + f_HC * flu_HC[i]

                    ## Vector de resultados para los nodos elementos opacos

                    for j in range(0, lenpared):
                        # Factores dependentientes de la pared correspondiente
                        a1 = T_old[i, axu10] / dt
                        b1 = T_old[i, axu10 + int(nodos[j]) - 2] / dt
                        c1 = T_old[i, axu10 + int(nodos[j]) - 1] / dt
                        if ordenfinal[j] == "N" or ordenfinal[j] == "NE" or ordenfinal[j] == "E" or ordenfinal[
                            j] == "SE" or \
                                ordenfinal[j] == "S" \
                                or ordenfinal[j] == "SO" or ordenfinal[j] == "O" or ordenfinal[j] == "NO" or ordenfinal[
                            j] == "N" or ordenfinal[j] == "HR" \
                                or ordenfinal[j] == "FL":
                            if ordenfinal[j] == "N":
                                a2 = (hre[1] + hce[1]) * t_e[i] + NORTE[i]
                            elif ordenfinal[j] == "NE":
                                a2 = (hre[1] + hce[1]) * t_e[i] + NORESTE[i]
                            elif ordenfinal[j] == "E":
                                a2 = (hre[1] + hce[1]) * t_e[i] + ESTE[i]
                            elif ordenfinal[j] == "SE":
                                a2 = (hre[1] + hce[1]) * t_e[i] + SURESTE[i]
                            elif ordenfinal[j] == "S":
                                a2 = (hre[1] + hce[1]) * t_e[i] + SUR[i]
                            elif ordenfinal[j] == "SO":
                                a2 = (hre[1] + hce[1]) * t_e[i] + SUROESTE[i]
                            elif ordenfinal[j] == "O":
                                a2 = (hre[1] + hce[1]) * t_e[i] + OESTE[i]
                            elif ordenfinal[j] == "NO":
                                a2 = (hre[1] + hce[1]) * t_e[i] + NOROESTE[i]
                            elif ordenfinal[j] == "HR":
                                a2 = (hre[1] + hce[1]) * t_e[i] + HORIZONTAL[i]
                            elif ordenfinal[j] == "FL":
                                a2 = (hre[1] + hce[1]) * t_e[i] + PHISOL_DIF[i]

                        ###### Piso ventilado

                        elif ordenfinal[j] == "AD":

                            # Reemplazar por temperatura interior T_ZTC[i] por T_old[len(T_old)-1]

                            # ISO=0
                            # a2 = ISO*((hre[1]+hce[1])*T_ZTC[i])
                            a2 = (hci[1]) * T_old[i, len(e) - 1]
                            # a2 = (hre[1]+hce[1])*t_e[i]
                        elif ordenfinal[j] == "IN":
                            a2 = (hci[1]) * T_ZTU[i]
                        elif ordenfinal[j] == "CT":
                            # a2 = (1/Rg)*T_T[i]
                            a2 = (hci[1]) * T_T[i]
                        ###############################################################################
                        #####Crea los valores en la matriz de resultados para todos los nodos.
                        for k in range(0, int(nodos[j])):

                            # Nodo Exterior
                            if k == 0:
                                re[axu10] = kpl[int(cuenta[j]) + k, j] * a1 + a2
                            # Nodo Interior
                            elif k == int(nodos[j]) - 2:
                                re[axu10 + int(nodos[j]) - 2] = kpl[int(cuenta[j]) + k, j] * b1 + b2
                                # Balance energético
                            elif k == int(nodos[j]) - 1:
                                re[axu10 + int(nodos[j]) - 1] = kpl[int(cuenta[j]) + k, j] * c1 + c2
                                # Nodos interiores
                            else:
                                if int(nodos[j]) > 3:
                                    axu11 += 1
                                    re[axu11] = kpl[int(cuenta[j]) + k, j] * T_old[i, axu11] / dt

                        axu10 += int(nodos[j])
                        axu11 += 3
                    ###############################################################################

                    # Ponderado ventana

                    # Superficie externa
                    re[n] = kpl_v[0] * T_old[i, n] / dt + (hce_v + hre[1]) * t_e[i] + PHISOL_VENTANA[i]
                    # Superficie interna
                    re[n + 1] = kpl_v[1] * T_old[i, n + 1] / dt + (1.0 / Atot) * (
                            (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i] + (1.0 - f_HC) * flu_HC[i])
                    # Balance interior
                    re[n + 2] = kpl_v[2] * T_old[i, n + 2] / dt + Hve[i] * theta_sup[i] + Hve_i[i] * t_e[i] + Htr * t_e[
                        i] + f_int * flu_int[i] + f_sol * flu_sol[i] + f_HC * flu_HC[i]

                    lu_piv = lu_factor(e)
                    t_actual = lu_solve(lu_piv, re)
                    T_nodos[i, :] = t_actual.T  # Reemplaza la temperatura en t-1 por la última temperatura
                    T_old3[i + 1, :] = t_actual.T
                    T_aire_HC[i] = T_nodos[i, len(e) - 1]

                    axu12 = 0
                    sumatheta_r_mn = 0

                    for j in range(0, len(area)):
                        axu12 += int(nodos2[j])
                        sumatheta_r_mn += area[j] * T_old3[i + 1, axu12 - 2]
                    theta_r_mn = sumatheta_r_mn / sum(area)
                    theta_int_op[i] = (T_old3[i + 1, len(e) - 1] + theta_r_mn) / 2
                    T_old[i + 1, :] = T_old3[i + 1, :]
                    T_old2[i + 1, :] = T_old3[i + 1, :]

        T_aire = T_old[1:L + 1, len(e) - 1]

        ###############################################################################
        ###############################################################################
        ###############################################################################

        for i in x:

            # Termino de ventilacion para el balance energetico

            axu2 = 0
            for j in range(1, lenpared + 1):
                axu2 += int(nodos[j - 1])
                e2[(axu2 - 1), (axu2 - 1)] = kpl[auxk, j - 1] / dt + (Hve[i] + Hve_i[i]) + Htr + areahci

            e2[n + 2, n + 2] = kpl_v[2] / dt + (Hve[i] + Hve_i[i]) + Htr + areahci

            # Si se tiene un recuperador de calor
            if ren != 0:
                theta_sup2[i] = ventilacion(ren, T_old4[i, T_old4.shape[1] - 1], t_e[i])
            else:
                theta_sup2[i] = t_e[i]

            axu10 = 0
            axu11 = 0
            # Factores dependientes solo de la hora
            # Nodo superficie interior
            b2 = (1.0 / Atot) * ((1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i])
            # Balance energetico
            c2 = Hve[i] * theta_sup2[i] + Hve_i[i] * t_e[i] + Htr * t_e[i] + f_int * flu_int[i] + f_sol * flu_sol[i]

            ## Vector de resultados para los nodos elementos opacos

            for j in range(0, lenpared):
                # Factores dependentientes de la pared correspondiente
                a1 = T_old4[i, axu10] / dt
                b1 = T_old4[i, axu10 + int(nodos[j]) - 2] / dt
                c1 = T_old4[i, axu10 + int(nodos[j]) - 1] / dt
                if ordenfinal[j] == "N" or ordenfinal[j] == "NE" or ordenfinal[j] == "E" or ordenfinal[j] == "SE" or \
                        ordenfinal[j] == "S" \
                        or ordenfinal[j] == "SO" or ordenfinal[j] == "O" or ordenfinal[j] == "NO" or ordenfinal[
                    j] == "N" or \
                        ordenfinal[j] == "HR" \
                        or ordenfinal[j] == "FL":
                    if ordenfinal[j] == "N":
                        a2 = (hre[1] + hce[1]) * t_e[i] + NORTE[i]
                    elif ordenfinal[j] == "NE":
                        a2 = (hre[1] + hce[1]) * t_e[i] + NORESTE[i]
                    elif ordenfinal[j] == "E":
                        a2 = (hre[1] + hce[1]) * t_e[i] + ESTE[i]
                    elif ordenfinal[j] == "SE":
                        a2 = (hre[1] + hce[1]) * t_e[i] + SURESTE[i]
                    elif ordenfinal[j] == "S":
                        a2 = (hre[1] + hce[1]) * t_e[i] + SUR[i]
                    elif ordenfinal[j] == "SO":
                        a2 = (hre[1] + hce[1]) * t_e[i] + SUROESTE[i]
                    elif ordenfinal[j] == "O":
                        a2 = (hre[1] + hce[1]) * t_e[i] + OESTE[i]
                    elif ordenfinal[j] == "NO":
                        a2 = (hre[1] + hce[1]) * t_e[i] + NOROESTE[i]
                    elif ordenfinal[j] == "HR":
                        a2 = (hre[1] + hce[1]) * t_e[i] + HORIZONTAL[i]
                    elif ordenfinal[j] == "FL":
                        a2 = (hre[1] + hce[1]) * t_e[i] + PHISOL_DIF[i]

                ###### Piso ventilado

                elif ordenfinal[j] == "AD":

                    # Reemplazar por temperatura interior T_ZTC[i] por T_old[i,len(e)-1]

                    # ISO=0
                    # a2 = ISO*((hre[1]+hce[1])*T_ZTC[i])
                    a2 = (hci[1]) * T_old4[i, len(e) - 1]
                    # a2 = (hre[1]+hce[1])*t_e[i]
                elif ordenfinal[j] == "IN":
                    a2 = (hci[1]) * T_ZTU[i]
                elif ordenfinal[j] == "CT":
                    # a2 = (1/Rg)*T_T[i]
                    a2 = (hci[1]) * T_T[i]
                ###########################################################################
                #####Crea los valores en la matriz de resultados para todos los nodos.
                for k in range(0, int(nodos[j])):

                    # Nodo Exterior
                    if k == 0:
                        re2[axu10] = kpl[int(cuenta[j]) + k, j] * a1 + a2
                    # Nodo Interior
                    elif k == int(nodos[j]) - 2:
                        re2[axu10 + int(nodos[j]) - 2] = kpl[int(cuenta[j]) + k, j] * b1 + b2
                        # Balance energético
                    elif k == int(nodos[j]) - 1:
                        re2[axu10 + int(nodos[j]) - 1] = kpl[int(cuenta[j]) + k, j] * c1 + c2
                        # Nodos interiores
                    else:
                        if int(nodos[j]) > 3:
                            axu11 += 1
                            re2[axu11] = kpl[int(cuenta[j]) + k, j] * T_old4[i, axu11] / dt

                axu10 += int(nodos[j])
                axu11 += 3
            ###########################################################################

            # Ponderado ventana

            # Superficie externa
            re2[n] = kpl_v[0] * T_old4[i, n] / dt + (hce_v + hre[1]) * t_e[i] + PHISOL_VENTANA[i]
            # Superficie interna
            re2[n + 1] = kpl_v[1] * T_old4[i, n + 1] / dt + (1.0 / Atot) * (
                    (1.0 - f_int) * flu_int[i] + (1.0 - f_sol) * flu_sol[i])
            # Balance interior
            re2[n + 2] = kpl_v[2] * T_old4[i, n + 2] / dt + Hve[i] * theta_sup2[i] + Hve_i[i] * t_e[i] + Htr * t_e[
                i] + f_int * flu_int[i] + f_sol * flu_sol[i]
            # Despeje de temperatura y guardado de temperaturas
            lu_piv2 = lu_factor(e2)
            t_actual2 = lu_solve(lu_piv2, re2)
            T_old4[i + 1, :] = t_actual2.T

            ###########################################################################
            # Operaciones para determinar la demanda energetica
            # calculo de la temperatura operativa
            axu12 = 0
            sumatheta_r_mn = 0

            for j in range(0, len(area)):
                axu12 += int(nodos2[j])
                sumatheta_r_mn += area[j] * T_old4[i + 1, axu12 - 2]
            theta_r_mn = sumatheta_r_mn / sum(area)
            theta_int_op2[i] = (T_old4[i + 1, len(e) - 1] + theta_r_mn) / 2

        T_aire2 = T_old4[1:L + 1, len(e) - 1]
        ###############################################################################
        ###############################################################################
        ###############################################################################

        T_old = np.round(T_old, 2)
        T_old4 = np.round(T_old4, 2)
        valor = 0
        valor += T_old.shape[1] + T_old4.shape[1]
        valor += len(e)
        valor += 23 + 3 + 14 + 2 + 7 + 3 + 4
        valor += conductividad.shape[1] + cp.shape[1] + densidad.shape[1] + espesor.shape[1] + dx.shape[1] + kpl.shape[
            1] + \
                 hpl.shape[1] + Nd.shape[1]

        output = np.zeros([L, valor])

        ID_Recinto = []
        for i in range(0, L):
            ID_Recinto.append(ID2)

        hora1 = T.iloc[:, 0]
        hora2 = T.iloc[:, 4]
        dia = T.iloc[:, 3]
        mes = T.iloc[:, 1]

        def f_list(var, output, contador):
            for i in range(0, len(var)):
                output[i, contador] = var[i]
            contador += 1

            return output, contador

        def f_list2(var, output, contador, hora):
            for i in range(0, len(var) - hora):
                output[i, contador] = var[i + hora]
            contador += 1

            return output, contador

        def f_2d(var, output, contador):
            aux = 0
            for j in range(0, var.shape[1]):
                for i in range(0, var.shape[0]):
                    output[i, j + contador] = var[i, j]
                aux += 1
            contador += aux

            return output, contador

        def f_var(var, output, contador):
            output[0, contador] = var
            contador += 1
            return output, contador

        ##################################################################
        ##calculo de variables asociados a la humedad, calor latente ISO 52016-2 cap 6.5.14

        def G_HU_ld(densidad_aire, flujo_aire, x_set_min, x_a_sup, x_int_a, G_int, G_abs, volumen_aire, dt):

            G_HU = densidad_aire * flujo_aire * (x_set_min - x_a_sup) - G_int + G_abs + densidad_aire * volumen_aire * (
                    x_set_min - x_int_a) / dt

            G_HU_ld2 = max(G_HU, 0)
            return G_HU_ld2

        def G_DHU_ld(densidad_aire, flujo_aire, x_set_max, x_a_sup, x_int_a, G_int, G_abs, volumen_aire, dt):

            G_DHU = -(-densidad_aire * flujo_aire * (
                        x_set_max - x_a_sup) + G_int - G_abs - densidad_aire * volumen_aire * (
                              x_set_max - x_int_a) / dt)

            G_DHU_ld2 = min(G_DHU, 0)
            return G_DHU_ld2

        # Cambio de unidades a carga de calor latente por humidificacion o dehumidifacion
        # G_HU=h_we*G_HU
        # G_DHU=h_we*G_DHU

        def x_set_min(phi_set_HU, presion_sat_int, presion_atm):

            X_set_min_t = 0.622 * (phi_set_HU * presion_sat_int) / (presion_atm - phi_set_HU * presion_sat_int)

            return X_set_min_t

        def x_set_max(phi_set_DHU, presion_sat_int, presion_atm):

            X_set_max_t = 0.622 * (phi_set_DHU * presion_sat_int) / (presion_atm - phi_set_DHU * presion_sat_int)

            return X_set_max_t

        def presion_saturacion(theta_a_int, theta_int):

            p_sat_int = 611.2 * exp((17.62 * theta_a_int) / (243.12 + theta_int))
            return p_sat_int

        def x_int_aire(densidad_aire, flujo_aire, x_a_e, GHU_DHU, G_int, G_abs, Volumen_int, dt, x_int_aire_t1):

            x_int_aire = (
                                 densidad_aire * flujo_aire * x_a_e + GHU_DHU + G_int - G_abs + densidad_aire * Volumen_int * x_int_aire_t1 / dt) / (
                                 densidad_aire * flujo_aire + densidad_aire * Volumen_int / dt)

            return x_int_aire

        # Datos necesarios para lo referente a humedad en el aire

        densidad_a = humedad.iloc[0, 5]
        cp_aire = humedad.iloc[1, 5]
        Volumen_int = humedad.iloc[3, 5]
        presion_atm = humedad.iloc[2, 5]
        phi_setHU = humedad.iloc[0, 8]
        phi_setDHU = humedad.iloc[1, 8]
        G_abs = humedad.iloc[3, 8]
        x_int_aire_t1 = humedad.iloc[2, 8]
        x_a_e = humedad.iloc[:, 1]
        G_int = humedad.iloc[:, 2]
        hwe = 2466000

        flujo_aire = (Hve + Hve_i) / (cp_aire * densidad_a)  # En m3/s, mantiene forma de vector

        G_HU = np.zeros(L)
        G_DHU = np.zeros(L)
        x_setmin = np.zeros(L)
        x_setmax = np.zeros(L)
        p_sat = np.zeros(L)
        x_int_a = np.zeros(L + 1)
        x_int_a[0] = x_int_aire_t1

        # Método de cálculo de humedad según ISO52016-1 cap 6.5.14
        for i in range(0, L):
            p_sat[i] = presion_saturacion(T_aire[i], theta_int_op[i])
            x_setmin[i] = x_set_min(phi_setHU, p_sat[i], presion_atm)
            x_setmax[i] = x_set_max(phi_setDHU, p_sat[i], presion_atm)
            G_HU[i] = G_HU_ld(densidad_a, flujo_aire[i], x_setmin[i], x_a_e[i], x_int_a[i], G_int[i], G_abs,
                              Volumen_int,
                              dt)
            G_DHU[i] = G_DHU_ld(densidad_a, flujo_aire[i], x_setmax[i], x_a_e[i], x_int_a[i], G_int[i], G_abs,
                                Volumen_int,
                                dt)
            if G_HU[i] != 0:
                x_int_a[i + 1] = x_int_aire(densidad_a, flujo_aire[i], x_a_e[i], G_HU[i], G_int[i], G_abs, Volumen_int,
                                            dt,
                                            x_int_a[i])
            elif G_DHU[i] != 0:
                x_int_a[i + 1] = x_int_aire(densidad_a, flujo_aire[i], x_a_e[i], G_DHU[i], G_int[i], G_abs, Volumen_int,
                                            dt,
                                            x_int_a[i])
            elif G_HU[i] == 0 or G_DHU[i] == 0:
                x_int_a[i + 1] = x_int_aire(densidad_a, flujo_aire[i], x_a_e[i], G_HU[i], G_int[i], G_abs, Volumen_int,
                                            dt,
                                            x_int_a[i])

        G_HU = G_HU * hwe
        G_DHU = G_DHU * hwe
        G_HU = CLIMA * G_HU
        G_DHU = CLIMA * G_DHU
        x_int_a[1:RANGE + 1] = CLIMA * x_int_a[1:RANGE + 1]

        for i in range(0, len(e)):
            output[0:RANGE, i] = T_old[1:RANGE, i]

        for i in range(0, len(e)):
            output[0:RANGE, i + len(e)] = T_old4[1:RANGE, i]

        contador = len(e) * 2
        output, contador = f_list(ID_Recinto, output, contador)
        output, contador = f_list(hora2, output, contador)
        output, contador = f_list(dia, output, contador)
        output, contador = f_list(mes, output, contador)
        output, contador = f_list(T_aire, output, contador)
        output, contador = f_list(T_aire2, output, contador)
        output, contador = f_list(t_e, output, contador)
        output, contador = f_list(theta_int_op, output, contador)
        output, contador = f_list(theta_int_op2, output, contador)
        output, contador = f_list(theta_sup, output, contador)
        output, contador = f_list(theta_sup2, output, contador)
        output, contador = f_list(flu_HC, output, contador)
        output, contador = f_list(flu_int, output, contador)
        output, contador = f_list(flu_sol, output, contador)
        output, contador = f_list(Hve, output, contador)
        output, contador = f_list(Hve_i, output, contador)
        output, contador = f_list(NORTE, output, contador)
        output, contador = f_list(NORESTE, output, contador)
        output, contador = f_list(ESTE, output, contador)
        output, contador = f_list(SURESTE, output, contador)
        output, contador = f_list(SUR, output, contador)
        output, contador = f_list(SUROESTE, output, contador)
        output, contador = f_list(OESTE, output, contador)
        output, contador = f_list(NOROESTE, output, contador)
        output, contador = f_list(HORIZONTAL, output, contador)
        output, contador = f_list(PHISOL_DIF, output, contador)
        output, contador = f_list(PHISOL_VENTANA, output, contador)
        output, contador = f_list(theta_C_set, output, contador)
        output, contador = f_list(theta_H_set, output, contador)
        output, contador = f_list(area, output, contador)
        output, contador = f_2d(conductividad, output, contador)
        output, contador = f_2d(cp, output, contador)
        output, contador = f_2d(espesor, output, contador)
        output, contador = f_2d(densidad, output, contador)
        output, contador = f_var(c_interior, output, contador)
        output, contador = f_var(dt, output, contador)
        output, contador = f_var(a_sol, output, contador)
        output, contador = f_2d(dx, output, contador)
        output, contador = f_2d(e, output, contador)
        output, contador = f_var(f_HC, output, contador)
        output, contador = f_var(f_int, output, contador)
        output, contador = f_var(F_ref, output, contador)
        output, contador = f_var(F_sh, output, contador)
        output, contador = f_var(f_sol, output, contador)
        output, contador = f_list(hce, output, contador)
        output, contador = f_var(hce_v, output, contador)
        output, contador = f_list(hci, output, contador)
        output, contador = f_var(hci_v, output, contador)
        output, contador = f_list(hre, output, contador)
        output, contador = f_list(hri, output, contador)
        output, contador = f_var(Htr, output, contador)
        output, contador = f_list(he, output, contador)
        output, contador = f_list(hi, output, contador)
        output, contador = f_2d(hpl, output, contador)
        output, contador = f_2d(kpl, output, contador)
        output, contador = f_var(hpl_v, output, contador)
        output, contador = f_list(kpl_v, output, contador)
        output, contador = f_2d(Nd, output, contador)
        output, contador = f_list(nodos2, output, contador)
        output, contador = f_var(pot_max, output, contador)
        output, contador = f_var(ren, output, contador)
        output, contador = f_var(Rg, output, contador)
        output, contador = f_2d(Rs_ext, output, contador)
        output, contador = f_var(U_v, output, contador)

        theta_int_op = theta_int_op.round(2)
        theta_int_op2 = theta_int_op2.round(2)
        flu_HC = flu_HC.round(2)

        output2 = np.zeros([L - START, 11])
        contador2 = 0
        output2, contador2 = f_list2(ID_Recinto, output2, contador2, START)
        output2, contador2 = f_list2(hora2, output2, contador2, START)
        output2, contador2 = f_list2(dia, output2, contador2, START)
        output2, contador2 = f_list2(mes, output2, contador2, START)
        output2, contador2 = f_list2(t_e, output2, contador2, START)
        output2, contador2 = f_list2(theta_int_op2, output2, contador2, START)
        output2, contador2 = f_list2(theta_int_op, output2, contador2, START)
        output2, contador2 = f_list2(flu_HC, output2, contador2, START)
        output2, contador2 = f_list2(flu_sol, output2, contador2, START)
        output2, contador2 = f_list2(G_HU, output2, contador2, START)
        output2, contador2 = f_list2(G_DHU, output2, contador2, START)

        muros = []
        for i in range(0, len(ordenfinal)):
            for j in range(0, int(nodos[i])):
                muros.append(ordenfinal[i])
        if area_ventana != 0:
            for i in range(0, 3):
                muros.append("V")

        for i in range(0, len(ordenfinal)):
            for j in range(0, int(nodos[i])):
                muros.append(ordenfinal[i])
        if area_ventana != 0:
            for i in range(0, 3):
                muros.append("V")

        muros.append("ID_Recinto")
        muros.append("Hora")
        muros.append("Dia")
        muros.append("Mes")
        muros.append("Temperatura_aire_interior_con_clima")
        muros.append("Temperatura_aire_interior_free_float")
        muros.append("Temperatura_aire_exterior")
        muros.append("Temperatura_interior_operativa_con_clima")
        muros.append("Temperatura_interior_operativa_free_float")
        muros.append("Temperatura_ventilacion_con_clima")
        muros.append("Temperatura_ventilacion_free_float")
        muros.append("Demanda")
        muros.append("Cargas_internas")
        muros.append("Flujo_solar_ventana")
        muros.append("Coeficiente_ventilacion")
        muros.append("Coeficiente_infiltraciones")
        muros.append("Factor_solar_Norte")
        muros.append("Factor_solar_Noreste")
        muros.append("Factor_solar_Este")
        muros.append("Factor_solar_Sureste")
        muros.append("Factor_solar_Sur")
        muros.append("Factor_solar_Suroeste")
        muros.append("Factor_solar_Oeste")
        muros.append("Factor_solar_Noroeste")
        muros.append("Factor_solar_Horizontal")
        muros.append("Factor_solar_Difuso")
        muros.append("Factor_solar_Ventana_exterior")
        muros.append("Temperatura_seteo_calefaccion")
        muros.append("Temperatura_seteo_refrigeracion")
        muros.append("Areas")
        for i in range(0, len(nodos)):
            muros.append("Conductividad")
        for i in range(0, len(nodos)):
            muros.append("Cp")
        for i in range(0, len(nodos)):
            muros.append("Espesor")
        for i in range(0, len(nodos)):
            muros.append("Densidad")
        muros.append("Capacidad_terminca_ambiente_interior")
        muros.append("dt")
        muros.append("Coeficiente_de_absorcion_solar")
        for i in range(0, len(nodos)):
            muros.append("dx")
        for i in range(0, len(e)):
            muros.append("Matriz")
        muros.append("Fraccion_convectiva_H/C")
        muros.append("Fraccion_convectiva_ganancias_internas")
        muros.append("Numero_de_fourier_referencia")
        muros.append("Factor_de_sombreamiento")
        muros.append("Fraccion_convectiva_radiacion_solar")
        muros.append("hce")
        muros.append("hce_ventana")
        muros.append("hci")
        muros.append("hci_ventana")
        muros.append("hre")
        muros.append("hri")
        muros.append("Htr_(puentes_termicos)")
        muros.append("he")
        muros.append("hi")
        for i in range(0, len(nodos)):
            muros.append("hpl")
        for i in range(0, len(nodos)):
            muros.append("kpl")
        muros.append("hpl_ventana")
        muros.append("kpl_ventana")
        for i in range(0, len(nodos)):
            muros.append("Nodos")
        muros.append("Nodos_por_muro")
        muros.append("Potencia_disponible_clima_m2")
        muros.append("Rendimiento_recuperador_calor")
        muros.append("Resistencia_termica_capa_virtual_tierra")
        muros.append("Resistencia_superficial_aire_interior")
        muros.append("Resistencia_superficial_aire_exterior")
        muros.append("Coeficiente_transferencia_calor")

        muros2 = []
        muros2.append("ID_Recinto")
        muros2.append("Hora")
        muros2.append("Dia")
        muros2.append("Mes")
        muros2.append("Temperatura_exterior")
        muros2.append("Temperatura_operativa_free_float")
        muros2.append("Temperatura_operativa_con_clima")
        muros2.append("Demanda")
        muros2.append("Sol")
        muros2.append("G_HU")
        muros2.append("G_DHU")
        muros2.append("x_int_aire")

        muros3 = []
        muros3.append("ID_Recinto")
        muros3.append("Mes")
        muros3.append("Hora")
        muros3.append("Temperatura_exterior")
        muros3.append("Temperatura_operativa_free_float")
        muros3.append("Temperatura_operativa_con_climas")
        muros3.append("Demanda")
        muros3.append("G_HU")
        muros3.append("G_DHU")

        row_end = RANGE
        row_length = 288
        df2 = T.iloc[0:row_end, 0:6].reset_index()
        vectores = np.array(
            [theta_int_op2[1:row_end], theta_int_op[1:row_end], flu_HC[1:row_end], G_HU[1:row_end], G_DHU[1:row_end]]).T
        df3 = pd.DataFrame(vectores,
                           columns=['Temperatura op free float', 'Temperatura op', 'Demanda', 'G_HU', 'G_DHU'])

        df4 = pd.concat([df2, df3], axis=1)
        promedios = df4.groupby(['month', 'hours/week']).mean()
        promedios = promedios.reset_index()

        output3 = np.zeros([row_length, 9])
        contador3 = 0
        output3, contador3 = f_list2(ID_Recinto[0:row_length], output3, contador3, 0)
        output3[:, 1:3] = promedios.iloc[:, 0:2]
        output3[:, 3:7] = promedios.iloc[:, 6:10].round(2)
        output3[:, 7:9] = promedios.iloc[:, 10:12].round(4)

        demanda1 = np.zeros(L)
        demanda2 = np.zeros(L)

        muros4 = []
        muros4.append("ID_Recinto")
        muros4.append("Hora")
        muros4.append("dia")
        muros4.append("Mes")
        muros4.append("Presión_saturacion")
        muros4.append("x_set_min")
        muros4.append("x_set_max")
        muros4.append("x_int_aire")
        muros4.append("G_HU")
        muros4.append("G_DHU")

        output4 = np.zeros([L, 10])
        contador4 = 0
        output4, contador4 = f_list2(ID_Recinto, output4, contador4, START)
        output4, contador4 = f_list2(hora2, output4, contador4, START)
        output4, contador4 = f_list2(dia, output4, contador4, START)
        output4, contador4 = f_list2(mes, output4, contador4, START)
        output4, contador4 = f_list2(p_sat, output4, contador4, START)
        output4, contador4 = f_list2(x_setmin, output4, contador4, START)
        output4, contador4 = f_list2(x_setmax, output4, contador4, START)
        output4, contador4 = f_list2(x_int_a, output4, contador4, START + 1)
        output4, contador4 = f_list2(G_HU, output4, contador4, START)
        output4, contador4 = f_list2(G_DHU, output4, contador4, START)

        ##################################################################
        ##Creacion de los archivos de salida.

        id = str(project_id)
        if Informes == 0:

            output_path = output_dir + "/" + id + ".output_simple_promedios.txt"
            b_file = open(output_path, "a")
            headers3 = ""
            for i in range(0, len(muros3)):
                headers3 += muros3[i] + " "
            b_file.write(headers3 + "\n")
            np.savetxt(b_file, output3, fmt='%1.2f')
            b_file.close()

        elif Informes == 1:

            output_path = output_dir + "/" + id + ".output_simple.txt"
            file = open(output_path, "a")
            headers2 = ""
            for i in range(0, len(muros2)):
                headers2 += muros2[i] + " "
            file.write(headers2 + "\n")
            np.savetxt(file, output2, fmt='%1.2f')
            file.close()

            output_path = output_dir + "/" + id + ".output_humedad.txt"
            c_file = open(output_path, "a")
            headers4 = ""
            for i in range(0, len(muros4)):
                headers4 += muros4[i] + " "
            c_file.write(headers4 + "\n")
            np.savetxt(c_file, output4, fmt='%1.6f')
            c_file.close()

        elif Informes == 2:

            output_path = output_dir + "/" + id + ".output_completo.txt"
            a_file = open(output_path, "a")
            headers = ""
            for i in range(0, len(muros)):
                headers += muros[i] + " "
            a_file.write(headers + "\n")
            np.savetxt(a_file, output, fmt='%1.2f')
            a_file.close()

            output_path = output_dir + "/" + id + ".output_humedad.txt"
            c_file = open(output_path, "a")
            headers4 = ""
            for i in range(0, len(muros4)):
                headers4 += muros4[i] + " "
            c_file.write(headers4 + "\n")
            np.savetxt(c_file, output4, fmt='%1.6f')
            c_file.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(f"Error en el motor de cálculo: {str(e)}")
